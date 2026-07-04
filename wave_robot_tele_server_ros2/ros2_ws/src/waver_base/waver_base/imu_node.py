"""IMU del Wave Rover leida directo por I2C desde la Pi.

El firmware waver_slate deja libre el bus de perifericos de la placa
(SDA=32/SCL=33 del ESP32 = /dev/i2c-1 de la Pi), asi que la Pi habla
directamente con:
  - QMI8658 (0x6B): acelerometro + giroscopio + temperatura
  - AK09918 (0x0C): magnetometro

Publica:
  /imu/data_raw    sensor_msgs/Imu        (sin orientacion valida)
  /imu/mag         sensor_msgs/MagneticField
  /imu/temperature std_msgs/Float32
  /imu/rpy         geometry_msgs/Vector3Stamped  (grados: roll, pitch, yaw
                   por filtro complementario + rumbo magnetico compensado)

Verificar con `i2cdetect -y 1` que aparecen 0x6b y 0x0c antes de arrancar.
"""
import math
import struct

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, MagneticField
from std_msgs.msg import Float32
from geometry_msgs.msg import Vector3Stamped

try:
    from smbus2 import SMBus
except ImportError:  # permite importar el modulo en entornos sin smbus2
    SMBus = None

G = 9.80665

# --- QMI8658 ---
QMI_ADDR = 0x6B
QMI_WHO_AM_I = 0x00       # debe leer 0x05
QMI_CTRL1 = 0x02
QMI_CTRL2 = 0x03          # accel: bits6:4 rango, bits3:0 ODR
QMI_CTRL3 = 0x04          # gyro:  bits6:4 rango, bits3:0 ODR
QMI_CTRL7 = 0x08          # enable: bit0 accel, bit1 gyro
QMI_TEMP_L = 0x33
QMI_AX_L = 0x35           # 12 bytes: ax..gz little-endian

ACC_LSB_PER_G = 4096.0    # rango +-8 g
GYRO_LSB_PER_DPS = 64.0   # rango +-512 dps

# --- AK09918 ---
AK_ADDR = 0x0C
AK_WIA2 = 0x01            # debe leer 0x0C
AK_ST1 = 0x10
AK_HXL = 0x11
AK_ST2 = 0x18
AK_CNTL2 = 0x31
AK_MODE_CONT_100HZ = 0x08
AK_UT_PER_LSB = 0.15


class ImuNode(Node):
    def __init__(self):
        super().__init__('imu_node')
        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('frame_id', 'imu_link')
        self.declare_parameter('rate_hz', 50.0)
        self.declare_parameter('alpha', 0.98)  # peso del giroscopio en el filtro

        self.frame_id = self.get_parameter('frame_id').value
        self.alpha = self.get_parameter('alpha').value
        rate = self.get_parameter('rate_hz').value
        self.dt = 1.0 / rate

        if SMBus is None:
            raise RuntimeError('smbus2 no instalado (pip install smbus2)')
        self.bus = SMBus(self.get_parameter('i2c_bus').value)
        self._init_qmi8658()
        self._init_ak09918()

        self.pub_imu = self.create_publisher(Imu, 'imu/data_raw', 20)
        self.pub_mag = self.create_publisher(MagneticField, 'imu/mag', 10)
        self.pub_temp = self.create_publisher(Float32, 'imu/temperature', 5)
        self.pub_rpy = self.create_publisher(Vector3Stamped, 'imu/rpy', 10)

        self.roll = 0.0
        self.pitch = 0.0
        self.mag = (0.0, 0.0, 0.0)
        self._n = 0

        self.create_timer(self.dt, self._tick)
        self.get_logger().info('IMU QMI8658 + AK09918 inicializada por I2C directo')

    # --- init ---
    def _init_qmi8658(self):
        who = self.bus.read_byte_data(QMI_ADDR, QMI_WHO_AM_I)
        if who != 0x05:
            self.get_logger().warn(f'QMI8658 WHO_AM_I=0x{who:02x} (esperado 0x05)')
        self.bus.write_byte_data(QMI_ADDR, QMI_CTRL1, 0x40)  # auto-increment, little-endian
        self.bus.write_byte_data(QMI_ADDR, QMI_CTRL2, 0x24)  # +-8g, ODR 500 Hz
        self.bus.write_byte_data(QMI_ADDR, QMI_CTRL3, 0x54)  # +-512 dps, ODR 500 Hz
        self.bus.write_byte_data(QMI_ADDR, QMI_CTRL7, 0x03)  # habilita accel + gyro

    def _init_ak09918(self):
        try:
            wia = self.bus.read_byte_data(AK_ADDR, AK_WIA2)
            if wia != 0x0C:
                self.get_logger().warn(f'AK09918 WIA2=0x{wia:02x} (esperado 0x0c)')
            self.bus.write_byte_data(AK_ADDR, AK_CNTL2, AK_MODE_CONT_100HZ)
            self.has_mag = True
        except OSError:
            self.get_logger().warn('AK09918 no responde; se publica sin magnetometro')
            self.has_mag = False

    # --- lecturas ---
    def _read_qmi(self):
        raw = self.bus.read_i2c_block_data(QMI_ADDR, QMI_AX_L, 12)
        ax, ay, az, gx, gy, gz = struct.unpack('<6h', bytes(raw))
        acc = (ax / ACC_LSB_PER_G * G, ay / ACC_LSB_PER_G * G, az / ACC_LSB_PER_G * G)
        gyr = tuple(math.radians(v / GYRO_LSB_PER_DPS) for v in (gx, gy, gz))
        traw = self.bus.read_i2c_block_data(QMI_ADDR, QMI_TEMP_L, 2)
        temp = struct.unpack('<h', bytes(traw))[0] / 256.0
        return acc, gyr, temp

    def _read_mag(self):
        st1 = self.bus.read_byte_data(AK_ADDR, AK_ST1)
        if not (st1 & 0x01):
            return None
        raw = self.bus.read_i2c_block_data(AK_ADDR, AK_HXL, 8)  # incluye ST2
        mx, my, mz = struct.unpack('<3h', bytes(raw[0:6]))
        return (mx * AK_UT_PER_LSB, my * AK_UT_PER_LSB, mz * AK_UT_PER_LSB)

    # --- fusion simple para el dashboard ---
    def _update_rpy(self, acc, gyr):
        ax, ay, az = acc
        acc_roll = math.atan2(ay, az)
        acc_pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az))
        self.roll = self.alpha * (self.roll + gyr[0] * self.dt) + (1 - self.alpha) * acc_roll
        self.pitch = self.alpha * (self.pitch + gyr[1] * self.dt) + (1 - self.alpha) * acc_pitch

        mx, my, mz = self.mag
        # rumbo magnetico compensado por inclinacion
        xh = mx * math.cos(self.pitch) + mz * math.sin(self.pitch)
        yh = (mx * math.sin(self.roll) * math.sin(self.pitch) + my * math.cos(self.roll)
              - mz * math.sin(self.roll) * math.cos(self.pitch))
        yaw = math.atan2(-yh, xh) if (mx or my or mz) else 0.0
        return yaw

    def _tick(self):
        try:
            acc, gyr, temp = self._read_qmi()
        except OSError as e:
            self.get_logger().warn(f'Fallo lectura QMI8658: {e}', throttle_duration_sec=5.0)
            return

        now = self.get_clock().now().to_msg()

        imu = Imu()
        imu.header.stamp = now
        imu.header.frame_id = self.frame_id
        imu.linear_acceleration.x, imu.linear_acceleration.y, imu.linear_acceleration.z = acc
        imu.angular_velocity.x, imu.angular_velocity.y, imu.angular_velocity.z = gyr
        imu.orientation_covariance[0] = -1.0  # sin orientacion
        self.pub_imu.publish(imu)

        self._n += 1
        if self.has_mag and self._n % 3 == 0:  # magnetometro a ~16 Hz
            try:
                m = self._read_mag()
                if m:
                    self.mag = m
                    mag = MagneticField()
                    mag.header = imu.header
                    # Tesla (AK09918 entrega uT)
                    mag.magnetic_field.x = m[0] * 1e-6
                    mag.magnetic_field.y = m[1] * 1e-6
                    mag.magnetic_field.z = m[2] * 1e-6
                    self.pub_mag.publish(mag)
            except OSError:
                pass

        yaw = self._update_rpy(acc, gyr)
        rpy = Vector3Stamped()
        rpy.header = imu.header
        rpy.vector.x = math.degrees(self.roll)
        rpy.vector.y = math.degrees(self.pitch)
        rpy.vector.z = math.degrees(yaw)
        self.pub_rpy.publish(rpy)

        if self._n % 50 == 0:  # temperatura a 1 Hz
            t = Float32()
            t.data = float(temp)
            self.pub_temp.publish(t)


def main(args=None):
    rclpy.init(args=args)
    node = ImuNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()
