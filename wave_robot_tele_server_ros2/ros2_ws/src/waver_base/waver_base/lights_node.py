"""Focos IO4/IO5 del Wave Rover (requiere firmware waver_slate_v2).

Suscribe /lights (std_msgs/Int16MultiArray, [io4, io5] en 0-255) y escribe el
registro 0x01 del ESP32 (0x11). IO4/IO5 son las salidas PWM de la placa
General Driver pensadas para focos LED/IR: IR para que las camaras mono de la
OAK vean de noche, LED blanco para el RGB.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray

try:
    from smbus2 import SMBus
except ImportError:
    SMBus = None

ESP32_ADDR = 0x11
REG_LIGHTS = 0x01


class LightsNode(Node):
    def __init__(self):
        super().__init__('lights_node')
        self.declare_parameter('i2c_bus', 1)

        if SMBus is None:
            raise RuntimeError('smbus2 no instalado (pip install smbus2)')
        self.bus = SMBus(self.get_parameter('i2c_bus').value)

        self.create_subscription(Int16MultiArray, 'lights', self._on_lights, 10)
        self.get_logger().info('Focos IO4/IO5 listos en /lights [io4, io5] 0-255')

    def _on_lights(self, msg: Int16MultiArray):
        if len(msg.data) != 2:
            self.get_logger().error('/lights espera exactamente 2 valores [io4, io5]')
            return
        io4 = max(0, min(255, int(msg.data[0])))
        io5 = max(0, min(255, int(msg.data[1])))
        try:
            self.bus.write_i2c_block_data(ESP32_ADDR, REG_LIGHTS, [io4, io5])
        except OSError as e:
            self.get_logger().error(f'Fallo escritura I2C de focos: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = LightsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()
