"""Gestor de energia del Wave Rover (Fase 5.4, parte software).

Vigila /battery y publica /battery_alert (String: OK | WARN | CRITICAL):
  - WARN  (< warn_voltage, def. 11.1 V ~ 50%): avisar y terminar la ronda.
  - CRITICAL (< critical_voltage, def. 10.8 V ~ 30%): ademas publica
    lock_nav=true en el twist_mux para vetar la rama autonoma.
  - shutdown_voltage (def. 10.4 V): escribe el flag de apagado limpio que el
    watchdog del host (tools/pi_host/) convierte en `shutdown -h` — proteger
    la SD vale mas que el ultimo 5% de ronda.

Umbrales subidos 2026-07-04 tras un apagon sin aviso: las 18650 actuales se
desploman de 11.4 V a corte en ~2 h de uso, asi que con WARN a 10.5 V la
alerta llegaba tarde (upgrade de celdas pendiente, Fase 5.1).

Ademas de /battery_alert (visible solo si miras el dashboard), las alertas
parpadean los focos IO4/IO5: destello cada 5 s en WARN, 1 Hz continuo en
CRITICAL. Desactivable con alert_blink:=false (p. ej. rondas nocturnas IR).

El voltaje de un 3S se hunde bajo carga (motores a fondo ~ -0.5 V), asi que
cada umbral exige `debounce_n` lecturas consecutivas por debajo (a 1 Hz del
battery_node = segundos sostenidos, no picos). La recuperacion (subir de
estado) exige salir del umbral con `hysteresis` V de margen.

Cuando exista el dock (Fase 5.2/5.3), CRITICAL disparara RETURN_TO_DOCK en el
mode_manager en lugar de solo vetar nav.
"""
import os

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Bool, Int16MultiArray, String

LEVELS = ['OK', 'WARN', 'CRITICAL']


class BatteryManager(Node):
    def __init__(self):
        super().__init__('battery_manager')
        self.declare_parameter('warn_voltage', 11.1)
        self.declare_parameter('critical_voltage', 10.8)
        self.declare_parameter('shutdown_voltage', 10.4)
        self.declare_parameter('hysteresis', 0.25)
        self.declare_parameter('debounce_n', 5)      # lecturas seguidas (~5 s)
        # El shutdown exige MUCHO mas sostenido: un colcon build hundio el
        # pack de 11.27 a 10.28 V durante ~20 s y provoco un apagado en falso
        # (2026-07-04). 300 lecturas @ 5 Hz = 60 s reales bajo umbral.
        self.declare_parameter('shutdown_debounce_n', 300)
        self.declare_parameter('republish_s', 10.0)  # refresco del estado actual
        self.declare_parameter('alert_blink', True)  # focos como alarma visual
        # /ros2_ws esta bind-mounteado desde el host: el watchdog de systemd
        # del host ve este archivo y ejecuta el apagado limpio.
        self.declare_parameter('shutdown_flag_path',
                               '/ros2_ws/.battery_shutdown_request')

        self.v_warn = self.get_parameter('warn_voltage').value
        self.v_crit = self.get_parameter('critical_voltage').value
        self.v_shut = self.get_parameter('shutdown_voltage').value
        self.hyst = self.get_parameter('hysteresis').value
        self.n = int(self.get_parameter('debounce_n').value)
        self.n_shut = int(self.get_parameter('shutdown_debounce_n').value)
        self.blink = bool(self.get_parameter('alert_blink').value)
        self.flag_path = self.get_parameter('shutdown_flag_path').value

        self.state = 'OK'
        self._below_warn = 0
        self._below_crit = 0
        self._below_shut = 0
        self._shutdown_requested = False
        self._last_v = None
        self._blink_i = 0
        self._blink_on = False

        # Flag huerfano de una sesion anterior: no apagar la Pi nada mas nacer.
        try:
            os.remove(self.flag_path)
        except OSError:
            pass

        self.pub_alert = self.create_publisher(String, 'battery_alert', 5)
        self.pub_lock = self.create_publisher(Bool, 'lock_nav', 5)
        self.pub_lights = self.create_publisher(Int16MultiArray, 'lights', 5)
        self.create_subscription(BatteryState, 'battery', self._on_battery, 5)
        self.create_timer(self.get_parameter('republish_s').value, self._republish)
        # El lock del twist_mux caduca a los 2 s: refresco a 1 Hz mientras
        # dure CRITICAL para mantener vetada la rama autonoma.
        self.create_timer(1.0, self._hold_lock)
        self.create_timer(0.5, self._blink_tick)

        self.get_logger().info(
            f'battery_manager: WARN<{self.v_warn} V, CRITICAL<{self.v_crit} V, '
            f'shutdown<{self.v_shut} V (debounce {self.n} lecturas)')

    def _on_battery(self, msg: BatteryState):
        v = msg.voltage
        if v <= 0.1:   # lectura invalida
            return
        self._last_v = v
        charging = msg.power_supply_status == BatteryState.POWER_SUPPLY_STATUS_CHARGING

        self._below_warn = self._below_warn + 1 if v < self.v_warn else 0
        self._below_crit = self._below_crit + 1 if v < self.v_crit else 0
        self._below_shut = self._below_shut + 1 if v < self.v_shut else 0

        if (self._below_shut >= self.n_shut and not charging
                and not self._shutdown_requested):
            self._shutdown_requested = True
            self.get_logger().fatal(
                f'Bateria en voltaje de apagado ({v:.2f} V): solicitando '
                f'shutdown limpio del host via {self.flag_path}')
            try:
                with open(self.flag_path, 'w') as f:
                    f.write(f'{v:.2f}\n')
            except OSError as e:
                self.get_logger().error(f'No pude escribir el flag: {e}')
        elif self._below_shut == 0 and self._shutdown_requested:
            # Recuperacion antes de que el watchdog dispare: retirar el flag
            # (el watchdog espera 30 s antes de actuar, esta es su ventana)
            self._shutdown_requested = False
            try:
                os.remove(self.flag_path)
                self.get_logger().warn(
                    f'Bateria recuperada ({v:.2f} V): shutdown cancelado')
            except OSError:
                pass

        new = self.state
        if self.state != 'CRITICAL' and self._below_crit >= self.n:
            new = 'CRITICAL'
        elif self.state == 'OK' and self._below_warn >= self.n:
            new = 'WARN'
        elif self.state == 'CRITICAL' and (charging or v > self.v_crit + self.hyst):
            new = 'WARN' if v < self.v_warn else 'OK'
        elif self.state == 'WARN' and (charging or v > self.v_warn + self.hyst):
            new = 'OK'

        if new != self.state:
            self.state = new
            self.get_logger().warn(f'Bateria {new}: {v:.2f} V')
            self._republish()

    def _republish(self):
        self.pub_alert.publish(String(data=self.state))

    def _hold_lock(self):
        if self.state == 'CRITICAL':
            self.pub_lock.publish(Bool(data=True))

    def _blink_tick(self):
        # Alarma visual con los focos. En OK no publica nada (no pisa el
        # control manual de /lights); solo manda un apagado al salir de alerta.
        if not self.blink or self.state == 'OK':
            if self._blink_on:
                self._set_lights(0)
            return
        self._blink_i += 1
        if self.state == 'CRITICAL':
            want = self._blink_i % 2 == 0        # 1 Hz continuo
        else:
            want = self._blink_i % 10 == 0       # destello 0.5 s cada 5 s
        if want != self._blink_on:
            self._set_lights(255 if want else 0)

    def _set_lights(self, pwm: int):
        self.pub_lights.publish(Int16MultiArray(data=[pwm, pwm]))
        self._blink_on = pwm > 0


def main(args=None):
    rclpy.init(args=args)
    node = BatteryManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()
