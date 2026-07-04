"""Gestor de modos TELEOP/AUTO + parada de emergencia.

Entradas:
  /joy (sensor_msgs/Joy)      boton A alterna TELEOP<->AUTO, B alterna e-stop
  /set_mode (std_msgs/String) "TELEOP" | "AUTO" (para el dashboard web)
  /set_estop (std_msgs/Bool)  e-stop desde el dashboard

Salidas (candados del twist_mux, publicados periodicamente):
  /lock_nav (Bool)  True en TELEOP -> silencia /nav_vel (prioridad 50 > nav 10)
  /e_stop (Bool)    True -> silencia todo (prioridad 255)
  /robot_mode (String)  estado actual, para OLED/dashboard

En AUTO, Nav2 (fase 4) publicara en /nav_vel; este nodo solo abre/cierra el
candado. El joystick siempre puede sobreescribir (prioridad 100).
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from sensor_msgs.msg import Joy
from std_msgs.msg import Bool, String


class ModeManager(Node):
    def __init__(self):
        super().__init__('mode_manager')
        self.declare_parameter('mode_button', 0)   # A en mando estilo Xbox
        self.declare_parameter('estop_button', 1)  # B

        self.mode_btn = self.get_parameter('mode_button').value
        self.estop_btn = self.get_parameter('estop_button').value

        self.auto = False
        self.estop = False
        self._prev_buttons = []

        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub_mode = self.create_publisher(String, 'robot_mode', latched)
        self.pub_lock_nav = self.create_publisher(Bool, 'lock_nav', 5)
        self.pub_estop = self.create_publisher(Bool, 'e_stop', 5)

        self.create_subscription(Joy, 'joy', self._on_joy, 10)
        self.create_subscription(String, 'set_mode', self._on_set_mode, 10)
        self.create_subscription(Bool, 'set_estop', self._on_set_estop, 10)

        # Los candados se refrescan a 2 Hz (twist_mux los trata como estado)
        self.create_timer(0.5, self._publish_state)
        self._announce()

    def _on_joy(self, msg: Joy):
        def pressed(idx):
            now = idx < len(msg.buttons) and msg.buttons[idx] == 1
            before = idx < len(self._prev_buttons) and self._prev_buttons[idx] == 1
            return now and not before

        if pressed(self.mode_btn):
            self.auto = not self.auto
            self._announce()
        if pressed(self.estop_btn):
            self.estop = not self.estop
            self._announce()
        self._prev_buttons = list(msg.buttons)

    def _on_set_mode(self, msg: String):
        target = msg.data.strip().upper()
        if target in ('TELEOP', 'AUTO'):
            self.auto = target == 'AUTO'
            self._announce()

    def _on_set_estop(self, msg: Bool):
        self.estop = msg.data
        self._announce()

    def _announce(self):
        mode = 'E_STOP' if self.estop else ('AUTO' if self.auto else 'TELEOP')
        m = String()
        m.data = mode
        self.pub_mode.publish(m)
        self.get_logger().info(f'Modo: {mode}')
        self._publish_state()

    def _publish_state(self):
        lock = Bool()
        lock.data = not self.auto  # TELEOP bloquea navegacion
        self.pub_lock_nav.publish(lock)
        es = Bool()
        es.data = self.estop
        self.pub_estop.publish(es)


def main(args=None):
    rclpy.init(args=args)
    node = ModeManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()
