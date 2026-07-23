"""Backends del PCA9685: mock (simulación/registro) y real (I2C).

REGLA DE ORO DEL PROYECTO, codificada:
  "JAMÁS mover motores sin confirmación explícita previa de Andrés."
El backend real NUNCA emite pulsos si no se armó explícitamente
(servicio /waver_arm/arm). El mock siempre es seguro: solo registra.
"""
import time
from abc import ABC, abstractmethod

from .servo_map import PCA9685_FREQ_HZ, ServoSpec


def retry_i2c(fn, tries: int = 3, wait_s: float = 0.005):
    """Reintenta una transacción I2C ante OSError transitorio.

    Visto en hardware (2026-07-22): el pico de corriente de un servo
    puede rebotar la tierra y corromper UNA transacción (Errno 121)
    sin resetear el chip. Un reintento milisegundos después funciona.
    """
    for intento in range(tries):
        try:
            return fn()
        except OSError:
            if intento == tries - 1:
                raise
            time.sleep(wait_s)


class Pca9685Backend(ABC):
    @abstractmethod
    def write(self, spec: ServoSpec, position: float) -> float:
        """Escribe una posición (rad/m). Devuelve el pulso en us aplicado."""

    @abstractmethod
    def disable_all(self) -> None:
        """Corta la señal de TODOS los canales (servos quedan sueltos)."""


class MockPca9685(Pca9685Backend):
    """Simulador: registra los pulsos que SE HABRÍAN enviado."""

    def __init__(self) -> None:
        self.last_us: dict[int, float] = {}
        self.write_count = 0
        self.enabled = True

    def write(self, spec: ServoSpec, position: float) -> float:
        us = spec.command_to_us(position)
        self.last_us[spec.channel] = us
        self.write_count += 1
        return us

    def disable_all(self) -> None:
        self.enabled = False
        self.last_us.clear()


class RealPca9685(Pca9685Backend):
    """Hardware real vía I2C (adafruit-circuitpython-pca9685).

    Solo se instancia con armado explícito y hardware presente.
    Import perezoso: el paquete no exige la librería para simular.
    """

    def __init__(self, i2c_address: int = 0x40, armed: bool = False) -> None:
        if not armed:
            raise PermissionError(
                'REGLA DE ORO: el backend real exige armado explícito '
                '(--armed / servicio /waver_arm/arm). Usa el mock para simular.')
        from adafruit_pca9685 import PCA9685  # import perezoso
        import board
        import busio
        self._pca = PCA9685(busio.I2C(board.SCL, board.SDA), address=i2c_address)
        self._pca.frequency = int(PCA9685_FREQ_HZ)

    def write(self, spec: ServoSpec, position: float) -> float:
        us = spec.command_to_us(position)
        # duty_cycle del driver adafruit es de 16 bits
        duty16 = int(us / (1_000_000.0 / PCA9685_FREQ_HZ) * 0xFFFF)

        def _tx():
            self._pca.channels[spec.channel].duty_cycle = duty16
        retry_i2c(_tx)
        return us

    def disable_all(self) -> None:
        for ch in self._pca.channels:
            retry_i2c(lambda c=ch: setattr(c, 'duty_cycle', 0))
