"""Cinematica diferencial: geometry_msgs/Twist -> /motor_commands (Int16MultiArray).

Los N20 del Wave Rover no tienen encoders: la "velocidad" es PWM en lazo
abierto. El mapeo m/s -> PWM se calibra con max_linear_speed (velocidad real
del robot a PWM maximo, medida empiricamente) y min_pwm (zona muerta donde el
motor no gira).

Publica a rate_hz fijo reenviando el ultimo comando (el firmware v2 tiene un
failsafe de 1 s y el nodo su propio watchdog: sin Twist fresco en cmd_timeout,
manda ceros).
"""
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from geometry_msgs.msg import Twist
from std_msgs.msg import Int16MultiArray


class CmdVelToMotors(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_motors')

        self.declare_parameter('wheel_separation', 0.125)   # m, distancia entre centros de ruedas [calibrar]
        self.declare_parameter('max_linear_speed', 1.0)     # m/s reales a PWM 255 [calibrar, spec dice 1.25]
        self.declare_parameter('max_pwm', 255)
        self.declare_parameter('min_pwm', 40)                # PWM minimo para vencer friccion [calibrar]
        self.declare_parameter('rate_hz', 20.0)
        self.declare_parameter('cmd_timeout', 0.5)           # s sin Twist -> parada
        # Trim: compensa la variacion de fabrica de los N20 (sin encoders el
        # mismo PWM no da la misma velocidad en ambos lados). Si el robot se
        # tuerce a la DERECHA (derecha mas lenta), sube trim_right o baja
        # trim_left, p. ej. trim_left=0.90. Calibrar hasta que avance recto.
        self.declare_parameter('trim_left', 1.0)
        self.declare_parameter('trim_right', 1.0)

        self.wheel_sep = self.get_parameter('wheel_separation').value
        self.max_speed = self.get_parameter('max_linear_speed').value
        self.max_pwm = self.get_parameter('max_pwm').value
        self.min_pwm = self.get_parameter('min_pwm').value
        self.cmd_timeout = self.get_parameter('cmd_timeout').value
        self.trim_l = self.get_parameter('trim_left').value
        self.trim_r = self.get_parameter('trim_right').value
        rate = self.get_parameter('rate_hz').value

        self._target = (0, 0)
        self._last_cmd_time = self.get_clock().now()

        self._pub = self.create_publisher(Int16MultiArray, 'motor_commands', 10)
        self.create_subscription(Twist, 'cmd_vel', self._on_twist, 10)
        self.create_timer(1.0 / rate, self._tick)
        # Permite calibrar en caliente: ros2 param set /cmd_vel_to_motors trim_left 0.9
        self.add_on_set_parameters_callback(self._on_params)

        self.get_logger().info(
            f'cmd_vel -> motor_commands listo (sep={self.wheel_sep} m, '
            f'vmax={self.max_speed} m/s, pwm=[{self.min_pwm},{self.max_pwm}])')

    def _on_params(self, params):
        for p in params:
            if p.name == 'trim_left':
                self.trim_l = float(p.value)
            elif p.name == 'trim_right':
                self.trim_r = float(p.value)
            elif p.name == 'max_linear_speed':
                self.max_speed = float(p.value)
            elif p.name == 'min_pwm':
                self.min_pwm = int(p.value)
        self.get_logger().info(f'trim L={self.trim_l:.2f} R={self.trim_r:.2f} '
                               f'vmax={self.max_speed} min_pwm={self.min_pwm}')
        return SetParametersResult(successful=True)

    def _speed_to_pwm(self, v: float) -> int:
        if abs(v) < 1e-3:
            return 0
        pwm = abs(v) / self.max_speed * self.max_pwm
        pwm = max(self.min_pwm, min(self.max_pwm, pwm))
        return int(pwm) if v > 0 else -int(pwm)

    def _on_twist(self, msg: Twist):
        v_l = msg.linear.x - msg.angular.z * self.wheel_sep / 2.0
        v_r = msg.linear.x + msg.angular.z * self.wheel_sep / 2.0

        # Si ambos superan la velocidad maxima, escala conservando el giro
        top = max(abs(v_l), abs(v_r))
        if top > self.max_speed:
            v_l *= self.max_speed / top
            v_r *= self.max_speed / top

        pwm_l = self._speed_to_pwm(v_l)
        pwm_r = self._speed_to_pwm(v_r)
        pwm_l = int(max(-self.max_pwm, min(self.max_pwm, pwm_l * self.trim_l)))
        pwm_r = int(max(-self.max_pwm, min(self.max_pwm, pwm_r * self.trim_r)))
        self._target = (pwm_l, pwm_r)
        self._last_cmd_time = self.get_clock().now()

    def _tick(self):
        age = (self.get_clock().now() - self._last_cmd_time).nanoseconds * 1e-9
        left, right = (0, 0) if age > self.cmd_timeout else self._target
        msg = Int16MultiArray()
        msg.data = [left, right]
        self._pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelToMotors()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Parada explicita al salir
        stop = Int16MultiArray()
        stop.data = [0, 0]
        node._pub.publish(stop)
        node.destroy_node()


if __name__ == '__main__':
    main()
