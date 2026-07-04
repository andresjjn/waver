"""Bateria del Wave Rover via INA219 (0x42, shunt 0.01 ohm) leido directo por I2C.

Publica /battery (sensor_msgs/BatteryState) a 1 Hz con voltaje, corriente,
potencia y porcentaje estimado para 3S Li-ion. Corriente positiva = descarga;
si al acoplar al dock la corriente se vuelve negativa (o cae a ~0 con voltaje
alto), esta cargando — esa señal usara el battery_manager de la fase 5.
"""
import struct

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState

try:
    from smbus2 import SMBus
except ImportError:
    SMBus = None

INA_ADDR = 0x42
REG_CONFIG = 0x00
REG_SHUNT_V = 0x01   # signed, LSB 10 uV
REG_BUS_V = 0x02     # (val >> 3) * 4 mV
SHUNT_OHMS = 0.01

# Curva aproximada 3S Li-ion (voltaje reposo -> %)
CURVE = [(9.0, 0.0), (9.9, 0.1), (10.8, 0.3), (11.1, 0.5),
         (11.7, 0.75), (12.3, 0.95), (12.6, 1.0)]


def _pct(v: float) -> float:
    if v <= CURVE[0][0]:
        return 0.0
    for (v0, p0), (v1, p1) in zip(CURVE, CURVE[1:]):
        if v <= v1:
            return p0 + (p1 - p0) * (v - v0) / (v1 - v0)
    return 1.0


class BatteryNode(Node):
    def __init__(self):
        super().__init__('battery_node')
        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('rate_hz', 1.0)

        if SMBus is None:
            raise RuntimeError('smbus2 no instalado (pip install smbus2)')
        self.bus = SMBus(self.get_parameter('i2c_bus').value)

        # Config por defecto del INA219: 32V, ganancia /8 (+-320 mV), 12 bits.
        # Suficiente para 12.6 V y +-32 A con shunt de 0.01.
        self.pub = self.create_publisher(BatteryState, 'battery', 5)
        self.create_timer(1.0 / self.get_parameter('rate_hz').value, self._tick)
        self.get_logger().info('INA219 (0x42) publicando /battery')

    def _read_word(self, reg: int) -> int:
        raw = self.bus.read_i2c_block_data(INA_ADDR, reg, 2)
        return struct.unpack('>H', bytes(raw))[0]

    def _tick(self):
        try:
            bus_v = (self._read_word(REG_BUS_V) >> 3) * 0.004
            shunt_raw = struct.unpack('>h', struct.pack('>H', self._read_word(REG_SHUNT_V)))[0]
            shunt_v = shunt_raw * 1e-5
        except OSError as e:
            self.get_logger().warn(f'Fallo lectura INA219: {e}', throttle_duration_sec=10.0)
            return

        current = shunt_v / SHUNT_OHMS  # A, positivo = descarga

        msg = BatteryState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.voltage = float(bus_v)
        msg.current = float(-current)  # convencion ROS: negativo = descargando
        msg.percentage = float(_pct(bus_v))
        msg.power_supply_technology = BatteryState.POWER_SUPPLY_TECHNOLOGY_LION
        msg.power_supply_status = (
            BatteryState.POWER_SUPPLY_STATUS_CHARGING if current < -0.05
            else BatteryState.POWER_SUPPLY_STATUS_DISCHARGING)
        msg.present = True
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = BatteryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()
