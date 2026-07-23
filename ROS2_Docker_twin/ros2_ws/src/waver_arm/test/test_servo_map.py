"""Pruebas del mapeo joint->pulso y de las reglas de seguridad. Sin ROS."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from waver_arm.pca9685_backend import (  # noqa: E402
    MockPca9685, RealPca9685, retry_i2c)
from waver_arm.servo_map import (  # noqa: E402
    MIMIC_JOINTS, SERVO_MAP, rate_limit)

HALF_PI = math.pi / 2


class TestMapeoServo180:
    """Servo 180°: 500-2500 us sobre ±90° (manual: PWM 0.5-2.5 ms)."""

    def test_centro_es_1500us(self):
        spec = SERVO_MAP['left_arm_shoulder_joint']
        assert spec.command_to_us(0.0) == pytest.approx(1500.0)

    def test_extremos(self):
        spec = SERVO_MAP['left_arm_yaw_joint']
        assert spec.command_to_us(-HALF_PI) == pytest.approx(500.0)
        assert spec.command_to_us(HALF_PI) == pytest.approx(2500.0)

    def test_satura_fuera_de_limites(self):
        """La seguridad #1: pedir 180° no puede pasar de 2500 us."""
        spec = SERVO_MAP['left_arm_elbow_joint']
        assert spec.command_to_us(math.pi) == pytest.approx(2500.0)
        assert spec.command_to_us(-10.0) == pytest.approx(500.0)

    def test_45_grados(self):
        spec = SERVO_MAP['right_arm_wrist_pitch_joint']
        assert spec.command_to_us(HALF_PI / 2) == pytest.approx(2000.0)


class TestL16Torso:
    """Actuonix L16-140-63-6-R: 0-140 mm. Unidad de Andrés INVERTIDA
    (verificado con potencia 2026-07-22): 2.0 ms = retraído, 1.0 ms =
    extendido. El 8s de "retraer" que lo sacó completo fue la prueba."""

    def test_retraido(self):
        spec = SERVO_MAP['torso_lift_joint']
        assert spec.command_to_us(0.0) == pytest.approx(2000.0)

    def test_extendido(self):
        spec = SERVO_MAP['torso_lift_joint']
        assert spec.command_to_us(0.14) == pytest.approx(1000.0)

    def test_mitad_de_carrera(self):
        spec = SERVO_MAP['torso_lift_joint']
        assert spec.command_to_us(0.07) == pytest.approx(1500.0)

    def test_velocidad_maxima_es_la_del_l16(self):
        # 20 mm/s del datasheet (63:1)
        assert SERVO_MAP['torso_lift_joint'].max_rate == pytest.approx(0.020)


class TestCanales:
    def test_sin_canales_duplicados(self):
        canales = [s.channel for s in SERVO_MAP.values()]
        assert len(canales) == len(set(canales))

    def test_13_canales_pca9685(self):
        """12 servos de brazo + L16 = 13 canales, caben en 16."""
        assert len(SERVO_MAP) == 13
        assert all(0 <= s.channel <= 15 for s in SERVO_MAP.values())

    def test_cableado_real_2026_07_22(self):
        """Contrato con el cableado físico de Andrés: derecho 15..10
        (garra primero), izquierdo 9..4, L16 provisional en 0."""
        assert SERVO_MAP['right_arm_finger_l_joint'].channel == 15
        assert SERVO_MAP['right_arm_yaw_joint'].channel == 10
        assert SERVO_MAP['left_arm_finger_l_joint'].channel == 9
        assert SERVO_MAP['left_arm_yaw_joint'].channel == 4
        assert SERVO_MAP['torso_lift_joint'].channel == 0
        # "codo 2" del cableado = wrist_pitch del URDF, canal contiguo al codo
        assert (SERVO_MAP['right_arm_wrist_pitch_joint'].channel
                == SERVO_MAP['right_arm_elbow_joint'].channel + 1)

    def test_mimic_sin_canal(self):
        """Los dedos derechos son engranaje: no deben tener canal PWM."""
        assert not (set(MIMIC_JOINTS) & set(SERVO_MAP))

    def test_duty_12bits(self):
        spec = SERVO_MAP['left_arm_shoulder_joint']
        # 1500 us de 20000 us -> ~307 cuentas de 4095
        assert spec.us_to_duty12(1500.0) == 307


class TestRampaSeguridad:
    def test_no_salta_mas_del_paso(self):
        # de 0 hacia 1 rad a 2.5 rad/s con dt=0.02 -> máx 0.05 por tick
        assert rate_limit(0.0, 1.0, 2.5, 0.02) == pytest.approx(0.05)

    def test_llega_exacto_si_esta_cerca(self):
        assert rate_limit(0.99, 1.0, 2.5, 0.02) == pytest.approx(1.0)

    def test_funciona_en_reversa(self):
        assert rate_limit(1.0, 0.0, 2.5, 0.02) == pytest.approx(0.95)

    def test_l16_tarda_7s_la_carrera(self):
        """Integrar la rampa completa: 140 mm a 20 mm/s = 7.0 s (datasheet)."""
        pos, t, dt = 0.0, 0.0, 0.02
        spec = SERVO_MAP['torso_lift_joint']
        while pos < 0.14:
            pos = rate_limit(pos, 0.14, spec.max_rate, dt)
            t += dt
        assert t == pytest.approx(7.0, abs=0.05)


class TestReglaDeOro:
    def test_backend_real_sin_armar_es_imposible(self):
        """JAMÁS mover motores sin confirmación explícita."""
        with pytest.raises(PermissionError):
            RealPca9685(armed=False)

    def test_mock_registra_sin_mover_nada(self):
        mock = MockPca9685()
        spec = SERVO_MAP['left_arm_yaw_joint']
        us = mock.write(spec, 0.0)
        assert us == pytest.approx(1500.0)
        assert mock.last_us[spec.channel] == pytest.approx(1500.0)

    def test_disable_all_limpia(self):
        mock = MockPca9685()
        mock.write(SERVO_MAP['torso_lift_joint'], 0.07)
        mock.disable_all()
        assert mock.last_us == {} and mock.enabled is False


class TestReintentoI2C:
    """Errno 121 transitorio (visto 2026-07-22) no debe tumbar el nodo."""

    def test_recupera_tras_fallo_transitorio(self):
        intentos = []

        def tx():
            intentos.append(1)
            if len(intentos) < 2:
                raise OSError(121, 'Remote I/O error')
            return 'ok'

        assert retry_i2c(tx, wait_s=0.0) == 'ok'
        assert len(intentos) == 2

    def test_relanza_si_el_fallo_persiste(self):
        def tx():
            raise OSError(121, 'Remote I/O error')

        with pytest.raises(OSError):
            retry_i2c(tx, tries=3, wait_s=0.0)
