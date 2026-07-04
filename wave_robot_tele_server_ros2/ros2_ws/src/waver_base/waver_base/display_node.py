"""OLED 0.91" del Wave Rover (SSD1306 128x32, 0x3C) como panel de bateria.

El firmware waver_slate_v2 dejo el OLED sin dueño (el ESP32 original lo
manejaba via JSON {"T":3}); como esta en el mismo bus /dev/i2c-1 que la Pi
ya usa para IMU/INA219, lo pintamos directo con un driver minimo (sin
dependencias: solo smbus2 y una fuente 5x7 embebida).

Muestra a 1 Hz:
  linea grande (2x): voltaje y porcentaje  ->  "11.3V 62%"
  linea inferior:    estado de /battery_alert + corriente (o CARGANDO)
En CRITICAL invierte la pantalla a 1 Hz para que se vea de lejos.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import String

try:
    from smbus2 import SMBus, i2c_msg
except ImportError:
    SMBus = None

OLED_ADDR = 0x3C
WIDTH, PAGES = 128, 4  # 128x32

# Fuente 5x7 clasica (columnas, LSB arriba) — solo los glifos que usamos.
FONT = {
    '0': (0x3E, 0x51, 0x49, 0x45, 0x3E), '1': (0x00, 0x42, 0x7F, 0x40, 0x00),
    '2': (0x42, 0x61, 0x51, 0x49, 0x46), '3': (0x21, 0x41, 0x45, 0x4B, 0x31),
    '4': (0x18, 0x14, 0x12, 0x7F, 0x10), '5': (0x27, 0x45, 0x45, 0x45, 0x39),
    '6': (0x3C, 0x4A, 0x49, 0x49, 0x30), '7': (0x01, 0x71, 0x09, 0x05, 0x03),
    '8': (0x36, 0x49, 0x49, 0x49, 0x36), '9': (0x06, 0x49, 0x49, 0x29, 0x1E),
    '.': (0x00, 0x60, 0x60, 0x00, 0x00), '%': (0x23, 0x13, 0x08, 0x64, 0x62),
    ':': (0x00, 0x36, 0x36, 0x00, 0x00), '-': (0x08, 0x08, 0x08, 0x08, 0x08),
    '+': (0x08, 0x08, 0x3E, 0x08, 0x08), ' ': (0x00, 0x00, 0x00, 0x00, 0x00),
    'A': (0x7E, 0x11, 0x11, 0x11, 0x7E), 'C': (0x3E, 0x41, 0x41, 0x41, 0x22),
    'D': (0x7F, 0x41, 0x41, 0x22, 0x1C), 'G': (0x3E, 0x41, 0x49, 0x49, 0x7A),
    'I': (0x00, 0x41, 0x7F, 0x41, 0x00), 'K': (0x7F, 0x08, 0x14, 0x22, 0x41),
    'L': (0x7F, 0x40, 0x40, 0x40, 0x40), 'N': (0x7F, 0x04, 0x08, 0x10, 0x7F),
    'O': (0x3E, 0x41, 0x41, 0x41, 0x3E), 'R': (0x7F, 0x09, 0x19, 0x29, 0x46),
    'S': (0x46, 0x49, 0x49, 0x49, 0x31), 'T': (0x01, 0x01, 0x7F, 0x01, 0x01),
    'V': (0x1F, 0x20, 0x40, 0x20, 0x1F), 'W': (0x7F, 0x20, 0x18, 0x20, 0x7F),
}

INIT_SEQ = [0xAE, 0xD5, 0x80, 0xA8, 0x1F, 0xD3, 0x00, 0x40, 0x8D, 0x14,
            0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x02, 0x81, 0x8F, 0xD9, 0xF1,
            0xDB, 0x40, 0xA4, 0xA6, 0xAF]

# bit i -> bits 2i y 2i+1 (para escalar la fuente x2 en vertical)
_DOUBLE = [sum(0b11 << (2 * i) for i in range(4) if n & (1 << i))
           for n in range(16)]


class DisplayNode(Node):
    def __init__(self):
        super().__init__('display_node')
        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('rate_hz', 1.0)

        if SMBus is None:
            raise RuntimeError('smbus2 no instalado (pip install smbus2)')
        self.bus = SMBus(self.get_parameter('i2c_bus').value)

        self._batt = None
        self._batt_stamp = None
        self._alert = 'OK'
        self._inverted = False
        self._hist = []
        self._beat = False

        self._cmd(INIT_SEQ)
        self.create_subscription(BatteryState, 'battery', self._on_battery, 5)
        self.create_subscription(String, 'battery_alert', self._on_alert, 5)
        self.create_timer(1.0 / self.get_parameter('rate_hz').value, self._tick)
        self.get_logger().info('OLED SSD1306 (0x3C) mostrando bateria')

    def _on_battery(self, msg: BatteryState):
        self._batt = msg
        self._batt_stamp = self.get_clock().now()
        # Historial para la tendencia (muestra cada >=5 s, ventana de 3 min).
        # El INA219 del rover no ve la corriente del cargador (su shunt solo
        # mide la rama de consumo), asi que "cargando" se infiere del voltaje.
        t = self._batt_stamp.nanoseconds * 1e-9
        if not self._hist or t - self._hist[-1][0] >= 5.0:
            self._hist.append((t, msg.voltage))
            self._hist = [(ht, hv) for ht, hv in self._hist if t - ht <= 180.0]

    def _trend(self) -> str:
        if len(self._hist) < 2:
            return ' '
        (t0, v0), (t1, v1) = self._hist[0], self._hist[-1]
        if t1 - t0 < 45.0:
            return ' '
        slope = (v1 - v0) / (t1 - t0) * 60.0   # V/min
        if slope > 0.03:
            return '+'      # subiendo: cargando
        if slope < -0.03:
            return '-'      # bajando: descargando
        return ' '

    def _on_alert(self, msg: String):
        self._alert = msg.data

    # --- dibujo -----------------------------------------------------------

    def _tick(self):
        fb = bytearray(WIDTH * PAGES)
        stale = (self._batt is None or self._batt_stamp is None or
                 (self.get_clock().now() - self._batt_stamp).nanoseconds > 5e9)
        if stale:
            self._text(fb, 10, 1, 'SIN DATOS')
        else:
            b = self._batt
            trend = self._trend()
            self._text2x(fb, 0, 0,
                         f'{b.voltage:4.1f}V{trend}{int(b.percentage * 100):d}%')
            status = 'CARGANDO' if trend == '+' else self._alert
            self._text(fb, 0, 3,
                       f'{status} {abs(b.current):3.1f}A {self._cpu_temp()}')

        # Latido: puntito parpadeante abajo a la derecha. Si esta quieto, la
        # pantalla es una foto congelada (la Pi murio y el OLED retiene RAM).
        self._beat = not self._beat
        if self._beat:
            fb[3 * WIDTH + 125] = 0x60

        # En CRITICAL alterna video normal/invertido: destello visible de lejos
        want_invert = self._alert == 'CRITICAL' and not self._inverted
        try:
            self._cmd([0xA7 if want_invert else 0xA6])
            self._inverted = want_invert
            self._cmd([0x21, 0, WIDTH - 1, 0x22, 0, PAGES - 1])
            self.bus.i2c_rdwr(i2c_msg.write(OLED_ADDR, bytes([0x40]) + bytes(fb)))
        except OSError as e:
            self.get_logger().warn(f'Fallo escritura OLED: {e}',
                                   throttle_duration_sec=10.0)

    def _cmd(self, cmds):
        self.bus.write_i2c_block_data(OLED_ADDR, 0x00, list(cmds))

    def _cpu_temp(self) -> str:
        # /sys esta visible dentro del contenedor; si no, linea sin temperatura
        try:
            with open('/sys/class/thermal/thermal_zone0/temp') as f:
                return f'{int(f.read()) / 1000:.0f}C'
        except (OSError, ValueError):
            return ''

    def _text(self, fb, x, page, s):
        for ch in s.upper():
            for col in FONT.get(ch, FONT[' ']):
                if x >= WIDTH:
                    return
                fb[page * WIDTH + x] = col
                x += 1
            x += 1

    def _text2x(self, fb, x, page, s):
        for ch in s.upper():
            for col in FONT.get(ch, FONT[' ']):
                lo = _DOUBLE[col & 0x0F]
                hi = _DOUBLE[(col >> 4) & 0x0F]
                for _ in range(2):
                    if x >= WIDTH:
                        return
                    fb[page * WIDTH + x] = lo
                    fb[(page + 1) * WIDTH + x] = hi
                    x += 1
            x += 2


def main(args=None):
    rclpy.init(args=args)
    node = DisplayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()
