#!/usr/bin/env python3
"""Descubrimiento/verificacion de canales — version MINIMO MOVIMIENTO.

Burst de 60 ms (3 pulsos PWM): el servo da un brinco de pocos grados y
se apaga. Repetible con Enter. Un canal a la vez, el operador decide todo.
Tip: dedo suave sobre el cuerpo del servo para sentir cual vibra.

Mapa real 2026-07-22 (verificado con potencia): derecho 15->10 (garra
primero), izquierdo 9->4, L16 en canal 3 INVERTIDO (2000 us = retraido).
"""
import time
from smbus2 import SMBus

ADDR, MODE1, PRESCALE, LED0, ALL_OFF_H = 0x40, 0x00, 0xFE, 0x06, 0xFD
BURST_S = 0.06

# (canal, nombre, us_objetivo, duracion_burst_s)
# Servos: centro 1500us, 60ms -> brinco de pocos grados.
# L16 (lineal, 20 mm/s, INVERTIDO medido): 2000us = RETRAIDO. Si ya esta
# retraido no se mueve; si no, repta max 6 mm en 0.3s. Oir el motor.
ESPERADO = [
    (15, "GARRA derecha", 1500, 0.06), (14, "MUNECA ROLL derecha", 1500, 0.06),
    (13, "MUNECA PITCH derecha (codo 2)", 1500, 0.06), (12, "CODO derecho (codo 1)", 1500, 0.06),
    (11, "HOMBRO derecho (elevacion)", 1500, 0.06), (10, "YAW derecho (rotacion hombro)", 1500, 0.06),
    (9, "GARRA izquierda", 1500, 0.06), (8, "MUNECA ROLL izquierda", 1500, 0.06),
    (7, "MUNECA PITCH izquierda (codo 2)", 1500, 0.06), (6, "CODO izquierdo (codo 1)", 1500, 0.06),
    (5, "HOMBRO izquierdo (elevacion)", 1500, 0.06), (4, "YAW izquierdo (rotacion hombro)", 1500, 0.06),
    (3, "L16 TORSO (lineal, oir el motorreductor)", 2000, 0.30),
]


def burst(bus, ch, us=1500, seg=BURST_S):
    c = round(us / 20000.0 * 4096.0)
    base = LED0 + 4 * ch
    bus.write_i2c_block_data(ADDR, base, [0, 0, c & 0xFF, c >> 8])
    time.sleep(seg)
    bus.write_i2c_block_data(ADDR, base, [0, 0, 0, 0x10])


with SMBus(1) as bus:
    bus.write_byte_data(ADDR, MODE1, 0x10)
    bus.write_byte_data(ADDR, PRESCALE, 121)
    bus.write_byte_data(ADDR, MODE1, 0x20)
    time.sleep(0.01)
    bus.write_byte_data(ADDR, ALL_OFF_H, 0x10)
    print("PCA9685 a 50 Hz, todo apagado.")
    print("Burst corto: brinco, y el servo queda SUELTO despues.\n")

    resultados = []
    for ch, nombre, us, seg in ESPERADO:
        print(f"\nch{ch:2d} — esperado: {nombre}")
        res = None
        while res is None:
            r = input(f"  [Enter]=burst {int(seg*1000)}ms  s=coincidio  n=fue otro  x=saltar  q=salir > ").strip().lower()
            if r == "":
                burst(bus, ch, us, seg)
            elif r == "s":
                res = "OK"
            elif r == "n":
                res = "REAL: " + input("  cual se movio? > ").strip()
            elif r == "x":
                res = "saltado"
            elif r == "q":
                res = "quit"
        if res == "quit":
            break
        resultados.append((ch, nombre, res))

    bus.write_byte_data(ADDR, ALL_OFF_H, 0x10)
    print("\n=== RESUMEN (todo apagado de nuevo) ===")
    malos = 0
    for ch, nombre, res in resultados:
        marca = "  OK " if res == "OK" else " ?? "
        if res not in ("OK", "saltado"):
            malos += 1
        print(f"{marca} ch{ch:2d} {nombre} -> {res}")
    print(f"\n{malos} discrepancias." + (" El mapa es correcto." if malos == 0 else " Corregir servo_map."))
