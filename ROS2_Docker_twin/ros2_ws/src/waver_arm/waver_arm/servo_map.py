"""Mapeo joint -> canal PCA9685 y conversión ángulo/carrera -> pulso PWM.

Módulo PURO (sin ROS): se prueba con pytest en cualquier máquina.

Fuentes de verdad:
- Manual del kit: servos "180°, PWM 0.5-2.5 ms" (formato MG996R).
- Actuonix L16-140-63-6-R: servo RC lineal, 1.0 ms = retraído, 2.0 ms =
  extendido (carrera 140 mm), interfaz idéntica a un servo.
- CABLEADO REAL de Andrés (2026-07-22): canales descendiendo desde el 15,
  brazo derecho primero, de externo a interno: garra F, muñeca roll E,
  "codo 2" = muñeca pitch D, "codo 1" = codo C, elevación = hombro B,
  rotación = base yaw A. Luego el izquierdo en el mismo orden (9..4).
  6 servos por brazo, todos independientes (sin pares espejados).
  [verificar en primer encendido]: la placa no trae serigrafía; el
  arranque en 15 sale de la imagen del vendedor.
"""
from dataclasses import dataclass

PCA9685_FREQ_HZ = 50.0  # estándar servo: periodo 20 ms
PERIOD_US = 1_000_000.0 / PCA9685_FREQ_HZ


@dataclass(frozen=True)
class ServoSpec:
    """Especificación de un canal servo."""
    channel: int
    min_us: float          # pulso en el límite inferior del joint
    max_us: float          # pulso en el límite superior del joint
    lower: float           # límite inferior del joint (rad o m)
    upper: float           # límite superior del joint (rad o m)
    max_rate: float        # velocidad máx permitida (rad/s o m/s) — seguridad

    def command_to_us(self, value: float) -> float:
        """Posición del joint -> ancho de pulso, con SATURACIÓN a límites."""
        v = min(max(value, self.lower), self.upper)
        frac = (v - self.lower) / (self.upper - self.lower)
        return self.min_us + frac * (self.max_us - self.min_us)

    def us_to_duty12(self, us: float) -> int:
        """Ancho de pulso -> cuenta de 12 bits del PCA9685 (0-4095)."""
        return round(us / PERIOD_US * 4095.0)


HALF_PI = 1.5707963267948966

# Servo 180°: 500-2500 us sobre ±90°. MG996R ~0.17 s/60° -> ~6 rad/s;
# limitamos a 2.5 rad/s por seguridad (regla: movimientos suaves).
def _arm_servo(ch: int) -> ServoSpec:
    return ServoSpec(ch, 500.0, 2500.0, -HALF_PI, HALF_PI, 2.5)


# Garra: joint 0..1 rad -> usamos media banda del servo (calibrar en real).
def _gripper_servo(ch: int) -> ServoSpec:
    return ServoSpec(ch, 1500.0, 2500.0, 0.0, 1.0, 2.5)


SERVO_MAP: dict[str, ServoSpec] = {
    # brazo derecho: canales 15..10 (garra primero, cableado real)
    'right_arm_finger_l_joint':    _gripper_servo(15),
    'right_arm_wrist_roll_joint':  _arm_servo(14),
    'right_arm_wrist_pitch_joint': _arm_servo(13),   # "codo 2"
    'right_arm_elbow_joint':       _arm_servo(12),   # "codo 1"
    'right_arm_shoulder_joint':    _arm_servo(11),
    'right_arm_yaw_joint':         _arm_servo(10),
    # brazo izquierdo: canales 9..4 (mismo orden)
    'left_arm_finger_l_joint':    _gripper_servo(9),
    'left_arm_wrist_roll_joint':  _arm_servo(8),
    'left_arm_wrist_pitch_joint': _arm_servo(7),     # "codo 2"
    'left_arm_elbow_joint':       _arm_servo(6),     # "codo 1"
    'left_arm_shoulder_joint':    _arm_servo(5),
    'left_arm_yaw_joint':         _arm_servo(4),
    # torso: L16-140 (0-0.14 m sobre 1.0-2.0 ms), 20 mm/s máx real
    # [por conectar] canal 0 provisional; 1-3 quedan de repuesto
    'torso_lift_joint': ServoSpec(0, 1000.0, 2000.0, 0.0, 0.14, 0.020),
}

# Los dedos derechos son mimic (engranajes): NO tienen canal propio.
MIMIC_JOINTS = {
    'left_arm_finger_r_joint':  ('left_arm_finger_l_joint', -1.0),
    'right_arm_finger_r_joint': ('right_arm_finger_l_joint', -1.0),
}


def rate_limit(current: float, target: float, max_rate: float, dt: float) -> float:
    """Acerca current a target sin exceder max_rate (rampa de seguridad)."""
    step = max_rate * dt
    delta = target - current
    if delta > step:
        return current + step
    if delta < -step:
        return current - step
    return target
