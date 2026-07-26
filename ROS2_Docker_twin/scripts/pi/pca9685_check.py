#!/usr/bin/env python3
"""Validacion PCA9685 SIN potencia (corre en la Pi 5, smbus2 nativo).

Programa 50 Hz, escribe el pulso seguro de cada canal del mapa real,
lo lee de vuelta del chip, y deja TODAS las salidas apagadas (FULL_OFF).
Sin V+ conectado ningun servo puede moverse; con V+ conectado despues,
nada salta porque todo queda apagado.

Mapa real 2026-07-22 (verificado con potencia): derecho 15->10 (garra
primero), izquierdo 9->4, L16 en canal 3 con convencion INVERTIDA
(2000 us = retraido). Historial en Waver/cad/MEDIDAS.md.
"""
import time
from smbus2 import SMBus

ADDR = 0x40
MODE1, PRESCALE = 0x00, 0xFE
LED0_ON_L = 0x06
ALL_LED_OFF_H = 0xFD

# (canal, nombre, us seguro: centro para servos, RETRAIDO para el L16)
MAPA = [
    (15, "garra der",        1500), (14, "muneca roll der",  1500),
    (13, "muneca pitch der", 1500), (12, "codo der",         1500),
    (11, "hombro der",       1500), (10, "yaw der",          1500),
    (9,  "garra izq",        1500), (8,  "muneca roll izq",  1500),
    (7,  "muneca pitch izq", 1500), (6,  "codo izq",         1500),
    (5,  "hombro izq",       1500), (4,  "yaw izq",          1500),
    (3,  "L16 torso (2000=retraido)", 2000),
]


def us_a_cuentas(us):
    return round(us / 20000.0 * 4096.0)


with SMBus(1) as bus:
    bus.write_byte_data(ADDR, MODE1, 0x10)
    bus.write_byte_data(ADDR, PRESCALE, 121)
    bus.write_byte_data(ADDR, MODE1, 0x20)
    time.sleep(0.01)
    pre = bus.read_byte_data(ADDR, PRESCALE)
    frec = 25_000_000 / (4096 * (pre + 1))
    print(f"prescale={pre} -> {frec:.1f} Hz " + ("OK" if pre == 121 else "ERROR"))

    fallas = 0
    for ch, nombre, us in MAPA:
        cuentas = us_a_cuentas(us)
        base = LED0_ON_L + 4 * ch
        bus.write_i2c_block_data(ADDR, base, [0, 0, cuentas & 0xFF, cuentas >> 8])
        leido = bus.read_i2c_block_data(ADDR, base, 4)
        eco = leido[2] | (leido[3] << 8)
        ok = eco == cuentas
        fallas += 0 if ok else 1
        print(f"  ch{ch:2d} {nombre:26s} {us}us = {cuentas:3d} -> eco {eco:3d} " + ("OK" if ok else "ERROR"))

    bus.write_byte_data(ADDR, ALL_LED_OFF_H, 0x10)
    eco_off = bus.read_i2c_block_data(ADDR, LED0_ON_L + 4 * 15, 4)
    apagado = bool(eco_off[3] & 0x10)
    print("salidas apagadas (FULL_OFF): " + ("OK" if apagado else "ERROR"))
    print("\nRESULTADO: " + ("TODO OK - seguro conectar potencia"
          if fallas == 0 and pre == 121 and apagado else f"{fallas} fallas - NO conectar"))
