# Guía de la próxima sesión física (todo lo remoto ya está hecho)

Estado al 2026-07-04 (sesión física 1 completada a medias): pasos 0-2 HECHOS
(v_max=0.8 m/s calibrada y persistida, giro verificado). El paso 3 (mapa)
quedó pendiente por batería agotada — el EKF ya mide bien (test del metro:
1.03 m) así que la próxima sesión es directo al paseo. Recordar: recargar la
pestaña de Foxglove tras reiniciar el SLAM, y vigilar el OLED (WARN a 11.1 V).

## 0. Preparación (2 min)

- [ ] Enchufar el USB del lidar (quedó suelto) y arrancar su contenedor
      (no puede arrancar sin el dispositivo presente):
      `ssh ros@192.168.1.16 "cd ~/Waver && docker compose up -d lidar"`
      → el radar del dashboard (http://192.168.1.16:8000) cobra vida.
- [ ] Robot en el suelo con 4 m libres en línea recta por delante.
- [ ] Deuda técnica pendiente de compra: cable USB-A 3.0 → USB-C de una pieza
      (marcado SS/5Gbps). Al conectarlo por el puerto azul, el log debe decir
      `USB SPEED: SUPER` (`docker logs waver_oak | grep SPEED`); entonces subir
      `i_resolution` a 1080P en `ROS2_Docker_oak_camera/config/oak.yaml`.

## 1. Calibrar velocidad real — max_linear_speed (5 min)

Con el robot mirando al espacio libre:

    # En la Mac (aviso: sale disparado 3 s a tope)
    python3 tools/mac_joystick_teleop.py   # gatillo = turbo, palanca a fondo
    # o pedirle a Claude que mande el pulso de 3 s

- [ ] Medir con metro la distancia recorrida en 3 s a PWM máximo.
- [ ] v_max = distancia / 3  (ej.: 2.4 m → 0.8 m/s)
- [ ] Persistir: en `waver_base/launch/base.launch.py` añadir el parámetro a
      cmd_vel_to_motors, o en caliente:
      `ros2 param set /cmd_vel_to_motors max_linear_speed 0.8`
- [ ] Actualizar `max_vel_x` en `ROS2_Docker_nav2/config/nav2_params.yaml`
      (hoy conservador: 0.30).

## 2. Verificar giro del twist (2 min)

- [ ] Con el joystick Logitech: girar la palanca (eje Z) a la derecha →
      el robot debe rotar a la derecha (horario visto desde arriba).
- [ ] Si va al revés: `python3 tools/mac_joystick_teleop.py --invert-twist`.

## 3. Primer mapa de la casa — Fase 3 (15-30 min)

    ssh ros@192.168.1.16
    cd ~/Waver && docker compose --profile slam up -d slam

- [ ] Ver el mapa en vivo: https://app.foxglove.dev → Open connection →
      `ws://192.168.1.16:8765`. Paneles: Map (/map), LaserScan (/scan),
      TF, Image (/oak/rgb/image_raw/compressed).
- [ ] Pasear el robot en teleop DESPACIO (0.2-0.3 de palanca), giros suaves,
      pasando por todas las habitaciones; cerrar lazos (volver al punto de
      partida) ayuda muchísimo al optimizador.
- [ ] Guardar el mapa al terminar:
      `docker exec waver_slam bash -c "source /opt/ros/humble/setup.bash &&
       source /ros2_ws/install/setup.bash &&
       ros2 service call /slam_toolbox/serialize_map
       slam_toolbox/srv/SerializePoseGraph \"{filename: '/maps/casa'}\""`
- [ ] Si la odometría rf2o patina (mapa doblado): reducir aún más la
      velocidad de paseo; el EKF y los ajustes finos se hacen en esta sesión.

## 4. Primera navegación autónoma — Fase 4 (si el mapa salió bien)

    docker compose --profile nav up -d nav

- [ ] En Foxglove: panel 3D → "Publish pose" → marcar un destino en el mapa.
- [ ] El robot debe planear y navegar esquivando (rama nav_vel, prioridad 10:
      la palanca del joystick SIEMPRE puede pisarla, y B = e-stop).
- [ ] Nav2 quedó con velocidades conservadoras y escala angular skid-steer
      (max_vel_theta 12 rad/s — NO bajarla a valores "normales", ver
      comentario en nav2_params.yaml).

## Chequeos rápidos si algo no aparece

    docker ps                                   # 4-6 contenedores Up
    docker logs waver_lidar --tail 5            # "Publish topic message"
    docker logs waver_oak 2>&1 | grep -c "what()"   # debe ser 0 (crashes)
    docker logs waver_slam --tail 5             # rf2o consumiendo /scan
    ros2 topic hz /scan /odom_rf2o /odometry/filtered /map
