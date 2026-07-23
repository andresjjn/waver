"""Nodo waver_arm: recibe comandos de joints y los ejecuta con rampa segura.

Interfaz:
  Sub  /waver_arm/command      (sensor_msgs/JointState: name+position — objetivo)
  Pub  /joint_states           (posición actual rampada, alimenta RViz/TF)
  Srv  /waver_arm/arm          (std_srvs/SetBool: armar/desarmar salida real)

Seguridad (reglas del proyecto codificadas):
  - Arranca en modo MOCK y DESARMADO. El hardware real exige parámetro
    use_mock:=false Y armado explícito por servicio.
  - Rampa por joint (rate limit de servo_map) — nada de saltos bruscos.
  - Saturación a límites del URDF en el mapeo (command_to_us ya satura).
  - Los dedos mimic se calculan aquí (engranaje), no se comandan.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_srvs.srv import SetBool

from .pca9685_backend import MockPca9685, RealPca9685
from .servo_map import (
    MIMIC_JOINTS, RELEASE_WHEN_SETTLED, SERVO_MAP, SETTLE_S, rate_limit)

RATE_HZ = 50.0


class ArmController(Node):
    def __init__(self) -> None:
        super().__init__('waver_arm')
        self.declare_parameter('use_mock', True)
        use_mock = self.get_parameter('use_mock').value

        self.armed = False
        if use_mock:
            self.backend = MockPca9685()
            self.get_logger().info('Backend MOCK: pulsos solo registrados.')
        else:
            # Lanza PermissionError si nadie armó — es intencional.
            self.backend = RealPca9685(armed=False)

        # estado: posición actual y objetivo por joint (arranque en cero)
        self.current = {name: 0.0 for name in SERVO_MAP}
        self.target = dict(self.current)
        # tiempo asentado en el objetivo (para soltar joints autoblocantes)
        self.settled_s = {name: 0.0 for name in RELEASE_WHEN_SETTLED}

        self.create_subscription(JointState, 'waver_arm/command', self._on_command, 10)
        self.pub_js = self.create_publisher(JointState, 'joint_states', 10)
        self.create_service(SetBool, 'waver_arm/arm', self._on_arm)
        self.create_timer(1.0 / RATE_HZ, self._tick)

    def _on_command(self, msg: JointState) -> None:
        for name, pos in zip(msg.name, msg.position):
            if name in SERVO_MAP:
                self.target[name] = pos
            elif name not in MIMIC_JOINTS:
                self.get_logger().warn(f'joint desconocido: {name}')

    def _on_arm(self, req: SetBool.Request, res: SetBool.Response):
        self.armed = req.data
        if not req.data:
            self.backend.disable_all()
        res.success = True
        res.message = 'ARMADO' if req.data else 'DESARMADO (señal cortada)'
        self.get_logger().warn(f'waver_arm: {res.message}')
        return res

    def _tick(self) -> None:
        dt = 1.0 / RATE_HZ
        names, positions = [], []
        for name, spec in SERVO_MAP.items():
            self.current[name] = rate_limit(
                self.current[name], self.target[name], spec.max_rate, dt)
            if name in RELEASE_WHEN_SETTLED:
                # L16: husillo autoblocante — al asentarse, señal fuera.
                # Sostener PWM contra un tope acuña el husillo (2026-07-22).
                if self.current[name] == self.target[name]:
                    self.settled_s[name] += dt
                else:
                    self.settled_s[name] = 0.0
                if self.settled_s[name] >= SETTLE_S:
                    self.backend.release(spec.channel)
                else:
                    self.backend.write(spec, self.current[name])
            else:
                self.backend.write(spec, self.current[name])
            names.append(name)
            positions.append(self.current[name])
        # dedos espejo (engranaje físico)
        for mimic, (master, mult) in MIMIC_JOINTS.items():
            names.append(mimic)
            positions.append(self.current[master] * mult)

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = positions
        self.pub_js.publish(msg)


def main() -> None:
    rclpy.init()
    node = ArmController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.backend.disable_all()
        node.destroy_node()


if __name__ == '__main__':
    main()
