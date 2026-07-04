#!/usr/bin/env python3
"""Teleop del Wave Rover desde la Mac con Logitech Extreme 3D Pro.

Basado en el joystick.py del proyecto Alpha 1S (pygame), publicando
geometry_msgs/Twist en /joy_vel (prioridad maxima del twist_mux) via el
rosbridge del robot — no requiere ROS en la Mac.

Mapeo (Extreme 3D Pro):
  Palanca adelante/atras (eje 1) -> avance/retroceso
  GIRO DE LA PALANCA eje Z (eje 2) -> giro del robot sobre su propio eje
      (girar a la derecha = robot gira a la derecha; usa --invert-twist si
       quedo al reves)
  Palanca izq/der (eje 0)          -> giro suave combinado con avance
  Slider de potencia (eje 3)       -> escala de velocidad (abajo=lento)
  Gatillo (boton 0)                -> TURBO (ignora el slider)

Uso:
  python3 mac_joystick_teleop.py [--host 192.168.1.16] [--invert-twist]

Parar el robot: soltar la palanca (watchdog + failsafe) o Ctrl+C.
"""
import argparse
import json
import math
import sys
import time

import pygame
import websocket  # websocket-client

RATE_HZ = 20
MAX_LIN = 1.0    # m/s a escala completa (calibrar con max_linear_speed del rover)
# Skid-steer de 4 ruedas: girar en el sitio exige derrapar las 4 ruedas ->
# hace falta PWM alto. 16 rad/s nominal = rueda a plena velocidad en el giro
# (2 * MAX_LIN / wheel_separation = 2 * 1.0 / 0.125).
MAX_ANG = 16.0
DEADZONE = 0.10

AX_X, AX_Y, AX_TWIST, AX_THROTTLE = 0, 1, 2, 3
BTN_TRIGGER = 0


def dz(v: float) -> float:
    if abs(v) < DEADZONE:
        return 0.0
    # re-escala para que la salida arranque suave tras la zona muerta
    return math.copysign((abs(v) - DEADZONE) / (1 - DEADZONE), v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='192.168.1.16')
    ap.add_argument('--invert-twist', action='store_true',
                    help='invierte el sentido de giro del eje Z')
    args = ap.parse_args()

    url = f'ws://{args.host}:9090'
    print(f'Conectando a rosbridge {url} ...')
    ws = websocket.create_connection(url, timeout=5)
    ws.send(json.dumps({'op': 'advertise', 'topic': '/joy_vel',
                        'type': 'geometry_msgs/msg/Twist'}))
    print('Conectado ✅')

    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print('❌ No hay joystick conectado. Conecta la Logitech y reintenta.')
        sys.exit(1)
    joy = pygame.joystick.Joystick(0)
    print(f'Joystick: {joy.get_name()} ({joy.get_numaxes()} ejes)')
    print('Controlando... palanca=avanzar, giro de palanca=rotar, '
          'slider=velocidad, gatillo=turbo. Ctrl+C para salir.')

    twist_sign = 1.0 if args.invert_twist else -1.0  # REP-103: +z = antihorario

    try:
        while True:
            pygame.event.pump()

            fwd = -dz(joy.get_axis(AX_Y))          # palanca adelante = +
            steer = dz(joy.get_axis(AX_X))         # izq/der
            twist = dz(joy.get_axis(AX_TWIST))     # giro de la palanca
            # slider: arriba = -1 -> escala 1.0; abajo = +1 -> escala 0.15
            scale = 0.15 + (1 - joy.get_axis(AX_THROTTLE)) / 2 * 0.85
            if joy.get_button(BTN_TRIGGER):
                scale = 1.0                        # turbo

            lin = fwd * MAX_LIN * scale
            # giro: el twist manda; la inclinacion lateral aporta la mitad
            ang = (twist_sign * twist + twist_sign * 0.5 * steer) * MAX_ANG * scale

            ws.send(json.dumps({'op': 'publish', 'topic': '/joy_vel', 'msg': {
                'linear': {'x': round(lin, 3), 'y': 0.0, 'z': 0.0},
                'angular': {'x': 0.0, 'y': 0.0, 'z': round(ang, 3)},
            }}))
            time.sleep(1.0 / RATE_HZ)
    except KeyboardInterrupt:
        pass
    finally:
        # parada explicita antes de salir
        for _ in range(3):
            ws.send(json.dumps({'op': 'publish', 'topic': '/joy_vel', 'msg': {
                'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}}}))
            time.sleep(0.05)
        ws.close()
        print('\nDetenido. El robot queda parado (watchdog activo).')


if __name__ == '__main__':
    main()
