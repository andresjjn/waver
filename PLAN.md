# Plan Maestro — Wave Rover + OAK-D Lite: de teleoperación a navegación autónoma

> **📍 2026-07-07 — La meta del proyecto se redefinió: ver [PLAN MARATÓN](#-plan-maratón-2026-07-07--hoja-de-ruta-oficial) al final.**
> Demo objetivo: pick & place autónomo en diorama de estantes + carga autónoma en dock
> propio + días corriendo sin intervención, contando miles de repeticiones. Las fases
> históricas de abajo siguen vigentes como cimiento; lo superado está marcado ⛔.

Estado de partida (julio 2026): control de motores por I2C maduro (`waver_motor_driver`,
nodo `motor_controller` suscrito a `/motor_commands`), teleop server en Pi 5 y cliente
joystick en Docker funcionando por CycloneDDS, plantillas sueltas de cámara CSI y lidar
STL-06, URDF vacío, sin odometría/SLAM/Nav2, sin nada de DepthAI.

## ✅ Implementado (2026-07-03, pendiente de prueba en hardware)

- **Firmware v2** `Arduino/waver_slate_v2/`: protocolo motor compatible + reg 0x01
  para focos IO4/IO5 + failsafe de 1 s.
- **`waver_base`** (en `wave_robot_tele_server_ros2/ros2_ws/src/`): cmd_vel→motores
  con watchdog, IMU/magnetómetro/temperatura y batería INA219 leídos DIRECTO por
  `/dev/i2c-1` (el bus de periféricos de la placa es el mismo que ve la Pi),
  focos, mode_manager (A=AUTO, B=e-stop) y twist_mux (joy 100 > web 90 > nav 10).
- **`waver_description`**: URDF xacro con frames de lidar/OAK/IMU (medidas [calibrar]).
- **`ROS2_Docker_oak_camera`**: depthai-ros, YOLO espacial on-device, nube de puntos.
- **`ROS2_Docker_web`**: dashboard Vigilante Nocturno (vídeo conmutable, horizonte
  artificial, brújula, batería, temperatura, joystick táctil, Gamepad API para la
  ROG, focos, e-stop, log de eventos). Puerto 8000; acceso remoto vía Tailscale.
- **`docker-compose.yml`** raíz: base + lidar + oak + web.

**Probado en hardware (2026-07-03):** teleop completa (Logitech + web), lidar LD06
publicando `/scan` (506 pts/vuelta), OAK-D Lite publicando RGB + depth + detecciones
espaciales (`Camera ready!`, MobileNet on-device). Fase 1 cerrada.

**Sesión remota (2026-07-03 noche):** OAK estable con YOLO espacial + `/oak/points`
a ~9.6 Hz (bugs de subpixel/tamaño custom documentados en `oak.yaml`); dashboard con
radar lidar, cajas de detección sobre el vídeo y clases COCO en español;
`battery_manager` activo (WARN 10.5 V / CRITICAL 10.0 V → veta nav vía lock);
Foxglove bridge en el puerto 8765; stack SLAM (`--profile slam`: rf2o + EKF +
slam_toolbox) construido y smoke-test pasado; Nav2 (`--profile nav`) preparado con
params skid-steer. **Checklist de la próxima sesión física: `docs/SESION_FISICA.md`.**

**Sesión física (2026-07-04):** `ipc: host` verificado (`/scan` cruza contenedores
FastDDS a 10 Hz); **v_max calibrada = 0.8 m/s** (2.4 m en pulso de 3 s a PWM 255;
persistida en `base.launch.py`, Nav2 a 0.5); giro del joystick verificado; OAK
rotada 180° on-device (montaje invertido); **fix EKF crítico**: fusionar POSE de
rf2o en diferencial y no su twist (que publica casi-cero) — test del metro pasó
de 9 cm a 1.03 m estimados. **Sistema de energía v2** tras dos apagones: umbrales
11.1/10.8 V, OLED SSD1306 (0x3C, bus compartido) como panel de batería+temp CPU
vía `display_node` (driver propio sin dependencias), apagado limpio del host a
10.4 V sostenidos 60 s (flag + watchdog systemd `tools/pi_host/`) con ventana de
recuperación de 30 s (lección: un colcon build hunde el pack ~1 V → apagado en
falso). El INA219 no ve la corriente del cargador (shunt solo en la rama de
consumo): "cargando" se infiere por tendencia de voltaje en el OLED.
**El primer mapa quedó pendiente** (batería agotada, 3 intentos).

**Sesión remota (2026-07-05) — fiabilidad de red y arranque:** el robot llevaba
horas "desaparecido" estando vivo: WiFi **JEJEN_5G (5 GHz)** con -80 dBm +
power save activo → ciclos de desconexión y carrusel de IPs por DHCP
(.16→.15→.69). Arreglos aplicados en la Pi: (1) `systemctl enable
docker.service` — antes era socket-activated y **tras un reinicio no arrancaba
ningún contenedor** (ni el watchdog de batería) hasta el primer comando docker;
(2) power save del WiFi desactivado (persistente vía
`/etc/NetworkManager/conf.d/wifi-powersave-off.conf`); (3) robot movido a
**JEJEN 2.4 GHz con IP estática 192.168.1.16** (autoconnect-priority 20 vs 5 de
la 5G, ligada a wlan0) → 0% pérdida y ~8 ms. Boot fantasma del 04 explicado:
wlan0 falló al reasociar a la 5G (13:51, `CONN_FAILED`/`no-secrets`) y la Pi
corrió sin red hasta el apagado limpio de 15:05 (botón de encendido = shutdown
graceful si ya estaba viva). Pendiente opcional: reserva DHCP de .16 en el
router. Trampa CLI documentada: daemon de `ros2` queda zombi
(`!rclpy.ok()`) tras reiniciar contenedores → `ros2 daemon stop` antes de
diagnosticar; verificar /scan mejor por los logs de rf2o.

**Sesión 2026-07-05 (tarde) — energía y CAD:** decisión de batería: **pack de
taladro 20V compatible DeWalt** (2×6 Ah Waitley ~$323k) + cuna adaptadora con
fusible (~$39k) + buck 20 A→12 V (~$75k) + 2º INA219 en 0x41 (lado pack) +
alarma buzzer; dock Fase 5 rediseñado a "dock tonto (24 V) / robot listo
(CC/CV 21 V a bordo conmutado por ROS)". CAD iniciado: `cad/plataforma.scad`
(OpenSCAD paramétrico) — **WAVER CRAB**: bandeja, bahía de batería pasante
trasera, torre-periscopio del lidar (regla: nada cruza su plano), visor OAK,
2 brazos cangrejo con pinza (servos del inventario). `apt full-upgrade`
ejecutado sin errores (reboot de prueba pendiente). Arquitectura completa
documentada en **docs/ARQUITECTURA.md** (estudio). Próximo CAD: migrar a
Onshape edu (ensambles con juntas/límites, import STEP, onshape-to-robot→URDF).

**Sesión 2026-07-06 — reboot aprobado, audio y el freeze de los 64 GB:**
reboot post-upgrade aprobado (kernel 6.12.93, `disable-wifi` mató la interna,
la Realtek heredó `wlan0` y la conexión la siguió por el anclaje MAC, los 5
contenedores auto-arrancaron). Lección NM: **autoconnect-priority solo se
evalúa AL conectar** — si el boot cae en el respaldo 2.4 nunca migra solo a
la 5G → instalado `wifi-prefer-5g.timer` (reintenta JEJEN_5G a los 90 s del
arranque). **HAT DE AUDIO NUEVO**: tarjeta tipo HAT con speakers estéreo,
enumera como USB ("USB PnP Audio Device", **ALSA card 2, `plughw:2,0`**);
probados con tono 440 Hz y voz (`espeak-ng -v es-419 --stdout | aplay -D
plughw:2,0`, ya instalado). Usos: alertas de voz/alarma de batería (sustituye
al buzzer pendiente), intercomunicador Fase 6, feedback de estado del robot.
`/oak/points` **RESUELTO** al reconectar el USB de la cámara (publica nubes;
sigue en USB 2.0 hasta comprar el cable A-3.0→C). **Incidente épico #6**: al
manipular los cables USB, `battery_node` (código nativo rclpy/FastDDS, no el
.py) intentó asignar **64 GB de RAM** → userland de la Pi congelado (ping
vivo, sshd/web muertos, OLED "sin datos") → ciclo de energía. Mitigación:
**`mem_limit` por servicio en docker-compose** (el OOM del cgroup mata solo
al proceso desbocado y restart lo revive; la Pi nunca más se congela entera).
Causa raíz nativa pendiente de observar si reincide. **Forense ampliado**: en
el 2º freeze la tormenta la protagonizaron battery_node (74 GB), cmd_vel (67),
imu_node (74) — TODOS los participantes FastDDS, no un nodo → segmento SHM
corrupto/gigante que todos intentan mapear; correlación fuerte con el arranque
del pipeline de la OAK (2/2 freezes con cámara activa, 0 tormentas sin ella).
**Giro del caso**: la oak YA corría CycloneDDS (ENV del Dockerfile) — el bug
era **cross-vendor**: cada rebote USB del conector flaky de la cámara relanzaba
su descubrimiento CycloneDDS y los participantes FastDDS respondían con las
asignaciones absurdas; el kernel 6.12 (de ayer) loguea cada negación → tormenta
de logs → freeze (el kernel viejo negaba en silencio, por eso nunca pasó
antes). **FIX APLICADO Y APROBADO**: oak homogeneizada a FastDDS
(`RMW_IMPLEMENTATION=rmw_fastrtps_cpp` en compose) + experimento controlado con
tripwire (`/usr/local/bin/oak_tripwire.sh`): 15 min limpios, `/oak/points`
verificado cross-container hasta waver_slam. El cable USB nuevo sigue siendo
prioridad: el conector flaky era el gatillo físico. **Descubrimiento**: la Pi 5 es de **4 GB**
(revision c04170), no de 8 como asumían los docs — presupuesto de RAM real:
~2.7 GB disponibles con el stack corriendo; refuerza el upgrade a Jetson Orin
Nano para la Fase 7 (waver_brain local).

**Deuda técnica para Fase 3:**
- **Derrape del mapa en giros** (observado mapeando 2026-07-05): rf2o a 10 Hz
  pierde el hilo en rotaciones rápidas (sin encoders). Mitigación de manejo:
  giros lentos + pausa, cerrar lazos. Fix estructural pendiente: fusionar el
  giroscopio del QMI8658 (imu0, velocidad angular yaw) en ekf.yaml para dar
  referencia inercial a los giros; evaluar también minimum_travel_heading de
  slam_toolbox.
- ~~Zona muerta de WiFi~~ **RESUELTO 2026-07-05**: la causa raíz de TODA la
  inestabilidad de red era el **módulo WiFi interno de la Pi dañado por un
  golpe** (señal -80 dBm al lado del router, boot fantasma, carrusel de IPs).
  Config final: **Realtek RTL8821CU USB (wlan1) como única interfaz**, JEJEN_5G
  por defecto anclada por MAC con IP fija 192.168.1.16, JEJEN 2.4 GHz de
  respaldo automático (misma IP), interna deshabilitada con
  `dtoverlay=disable-wifi`, deep-sleep rtw88 off, udev anti-autosuspend USB.
  Resultado: Pi→router 0% pérdida / 2.3 ms. Nota: en rincones, el 5G puede
  ceder al respaldo 2.4 con un mini-corte (comportamiento esperado). Los
  warnings "failed to get tx report" del rtw88 son cosméticos. Si queda varado
  sin señal: empujarlo rodando, no alzarlo (secuestra al SLAM).
- **Celdas 18650 agotadas** (sag ~1 V con ráfaga de CPU, ~2 h de autonomía):
  decidido reemplazo por **LiPo/Li-ion 3S CON BMS integrado**, ≥5 Ah (XT60);
  cargarla externamente si es RC pelada — nunca por el UPS sin verificar.
- **Fijación mecánica de conectores USB** (lidar y OAK): ambos se soltaron
  durante la sesión al manipular el robot — brida/hot-glue antes de rondas.
- ~~`/oak/points` mudo desde la rotación 180°~~ **RESUELTO 2026-07-06**: era el
  USB físicamente suelto; reconectado publica nubes de 1280 de ancho.
- La OAK negocia **USB 2.0** (`USB SPEED: HIGH`): el adaptador USB-A→C actual solo
  cablea pines 2.0. Conseguir cable USB-A 3.0→C de una pieza (marcado SS/5Gbps) y
  conectar al puerto azul → debe decir `SUPER`. Nota: el USB-C de la Pi 5 es SOLO
  alimentación, nunca para la cámara.
- ~~`/oak/points` no aparece pese a `pointcloud.enable:=true`~~ **RESUELTO
  2026-07-06** (mismo caso: USB suelto).
- `usb_max_current_enable=1` ya aplicado en `/boot/firmware/config.txt` (la OAK
  necesita >600 mA).

Estrategia nocturna: el **lidar 2D es el sensor principal a oscuras** (láser propio,
360°, SLAM y anti-choque sin luz) y los **focos IR en IO4/IO5 dan visión nocturna a
las cámaras mono de la OAK** (profundidad estéreo funciona bajo IR); el LED blanco
solo cuando se quiera RGB a color. Descartado por decisión: integración con alarma
doméstica / Home Assistant.

Arquitectura objetivo:

```
ROG Ally (Windows) ──WiFi──► Raspberry Pi 5 (Docker/ROS2 Humble) ──I2C──► ESP32 ──► Motores
   │  Foxglove / Web UI              │
   │  Mando Xbox (teleop)            ├── OAK-D Lite (USB3): RGB + depth + YOLO on-device
   │  Botón A = modo autónomo        ├── Lidar STL-06: /scan
   └── video en tiempo real          └── IMU del ESP32: /imu/data_raw
```

---

## FASE 0 — Dominar el robot con ROS (consolidar lo que ya hay)

Objetivo: un solo `docker compose` en la Pi que levante todo el robot, controlable con
interfaces estándar de ROS, visible en RViz/Foxglove desde el PC. Sin esto, ninguna
pieza de navegación encaja.

- **0.1 Capa cinemática `cmd_vel`** — nuevo paquete `waver_base` con nodo
  `cmd_vel_to_motors`: suscribe `geometry_msgs/Twist` en `/cmd_vel`, aplica cinemática
  diferencial (separación de ruedas ~0.13 m, sin encoders ⇒ mapear m/s → PWM con curva
  calibrada empíricamente), publica `/motor_commands` (Int16MultiArray) reenviando a
  ≥10 Hz para respetar el heartbeat de 3 s del ESP32. Incluir watchdog propio: si no
  llega Twist en 500 ms, enviar [0,0].
- **0.2 URDF y TF** — crear `ROS_WAVE_URDF/waver.urdf.xacro` con `base_link`, ruedas,
  `laser_frame`, `oak_rgb_camera_frame`, `imu_link` (medidas del DXF de Waveshare).
  `robot_state_publisher` en el compose. Verificar árbol TF en RViz.
- **0.3 IMU en ROS** — nodo que lea la IMU del ESP32 (JSON `{"T":126}` por UART, o
  extender el firmware I2C) y publique `sensor_msgs/Imu` en `/imu/data_raw`; filtro
  `imu_filter_madgwick` → `/imu/data`.
- **0.4 Integrar lidar** — mover `ldlidar_stl_ros2` al workspace del server principal
  (o al compose como servicio), TF estático `base_link → laser_frame`. Topic `/scan`.
- **0.5 Teleop estándar** — sustituir el controlador de joystick custom por
  `joy` + `teleop_twist_joy` publicando `/cmd_vel`. Así el mismo camino sirve para
  humano y para Nav2.
- **0.6 twist_mux** — multiplexor de `/cmd_vel` con prioridades:
  joystick > navegación > detenido. Es la pieza que luego permite el "botón de modo
  autónomo" sin condiciones raras en el código.
- **0.7 docker-compose.yml + launch files** — un `robot.launch.py` que levante base +
  IMU + lidar + robot_state_publisher. Compose con servicios: `base`, `lidar`,
  `camera` (fase 1), `nav` (fase 4).

**Criterio de salida:** desde el PC ves en RViz el TF, el `/scan` y mueves el robot
con el mando publicando `/cmd_vel`.

## FASE 1 — OAK-D Lite en la Pi 5 + vídeo por WiFi

- **1.1 Contenedor `ROS2_Docker_oak_camera`** — mismo patrón Docker del proyecto,
  base `ros:humble-ros-base-jammy`, con `depthai-ros` (rama humble de Luxonis).
  Reglas udev (`SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"`) en la Pi,
  `-v /dev/bus/usb:/dev/bus/usb --device-cgroup-rule='c 189:* rmw'` en el run.
  - Topics: `/oak/rgb/image_raw`, `/oak/stereo/image_raw` (depth),
    `/oak/points` (nube de puntos), `CameraInfo`.
  - Resoluciones contenidas: RGB 720p@15–30, depth 400p — la Pi 5 lo mueve sin ahogarse.
  - ⚠️ Alimentación: la OAK-D Lite consume hasta ~4.5 W por USB. Verificar presupuesto
    de corriente del riel 5 V del UPS del rover; si hay brownouts, hub USB alimentado
    o alimentar la Pi con la salida adecuada.
- **1.2 Streaming eficiente por WiFi** — el vídeo crudo satura el WiFi; usar:
  - `image_transport` comprimido (JPEG/H264 via `ffmpeg_image_transport`) para ROS, y
  - **`foxglove_bridge`** en la Pi (WebSocket): desde la ROG se abre Foxglove Studio
    y se ve vídeo, nube de puntos, TF, detecciones y gráficas en tiempo real sin
    instalar ROS en Windows. Es la vía recomendada para "ver la cámara en la ROG".
- **1.3 Preprocesamiento en la cámara** — el chip Myriad X de la OAK corre la red
  neuronal on-device: configurar pipeline `spatial detection` (YOLOv6/8n o MobileNet-SSD)
  para que la cámara entregue directamente detecciones con posición 3D
  (`/oak/nn/spatial_detections`) sin gastar CPU de la Pi. La Pi solo re-publica y anota.

**Criterio de salida:** en la ROG ves RGB + depth + nube de puntos en Foxglove con
<300 ms de latencia, y las detecciones de objetos llegan como topic.

## FASE 2 — Control total desde la ROG Ally (mando estilo Xbox)

La ROG Ally corre Windows; dos vías, ordenadas por recomendación:

- **Opción A (recomendada): Foxglove + joy remoto.** Foxglove Studio en Windows para
  visualización, y para el mando dos alternativas:
  1. **Web UI servida desde la Pi** (paquete `waver_web_teleop`): página con
     Gamepad API del navegador (detecta los sticks de la Ally/mando Xbox nativamente),
     vídeo por WebRTC o MJPEG, y `rosbridge_suite` para publicar `/joy` → la Pi lo
     convierte a `/cmd_vel`. Cero instalación en la ROG: solo abrir el navegador.
  2. Foxglove teleop panel (más limitado, sirve de fallback).
- **Opción B: WSL2/dual-boot Linux en la Ally** reutilizando el contenedor
  `wave_rover_joystick_controller` existente. Funciona pero DDS a través de WSL2 es
  frágil; solo si la Opción A se queda corta.
- **2.1 Botón de modo autónomo** — mapear un botón del mando (p. ej. `A`/`X`) a un
  nodo `mode_manager`: alterna entre `TELEOP` y `AUTO` conmutando prioridades del
  `twist_mux` y lanzando/cancelando goals de Nav2. Otro botón = parada de emergencia
  (bloquea el mux). Feedback del modo en el OLED del rover (`{"T":3,...}`) y en la UI.

### 2.2 Centro de mando web "Vigilante Nocturno" (cualquier dispositivo)

La misma web teleop de la Opción A evoluciona a un **dashboard completo servido desde
la Pi**, accesible desde el celular, tablet, la ROG o cualquier navegador:

- **Panel de sensores en vivo** (vía rosbridge/WebSocket):
  - Inclinación (roll/pitch) y rumbo con horizonte artificial — de `/imu/data`
    (el rover tiene IMU de 9 ejes: QMI8658 acel+giro y **magnetómetro AK09918**,
    ambos expuestos por `{"T":126}`).
  - **Batería**: voltaje, corriente y potencia del INA219 (`{"T":130}`) como
    `BatteryState`, con % estimado e histórico de consumo.
  - **Temperatura**: la reporta la propia IMU/ESP32 en `{"T":126}`.
  - Señal WiFi de la Pi, carga de CPU/RAM/temperatura de la Pi, estado del modo
    (TELEOP/AUTO/PATRULLA/VOLVIENDO A BASE), posición en el mapa en miniatura.
- **Cámara en vivo**: WebRTC (baja latencia) con fallback MJPEG; conmutador
  RGB / profundidad coloreada / vista con detecciones anotadas.
- **Mandos virtuales**: joystick táctil (nipple.js) para celular/tablet + soporte
  Gamepad API cuando hay mando físico conectado. Botones de: modo autónomo, parada
  de emergencia, iniciar patrulla, volver a base, snapshot.
- **Focos nocturnos**: la placa del rover tiene salidas PWM IO4/IO5 (`{"T":132}`)
  pensadas para LEDs — cablear focos LED/IR y controlarlos con un slider desde la
  web. Clave para el rol de vigilante: la OAK-D Lite no tiene visión nocturna
  propia (sus cámaras mono ven algo de IR, pero necesita iluminación).
- **Modo vigilante**: log de eventos (persona/mascota detectada, con hora, snapshot
  y posición en el mapa), galería de capturas, notificaciones push
  (Telegram/ntfy.sh), grabación de clips al detectar movimiento/personas.
- **Acceso desde fuera de casa**: NO exponer el puerto a internet directamente
  (es control físico de un robot). Usar **Tailscale** (VPN mesh, gratis, cero
  config de router) o Cloudflare Tunnel con autenticación. Dentro de la LAN,
  la web pide login igualmente.
- Stack sugerido: backend FastAPI/Node en la Pi (contenedor `waver_web`),
  frontend estático (React o vanilla), rosbridge + WebRTC (aiortc o
  MediaMTX para el vídeo).

**Criterio de salida:** desde el celular en la cama: ves vídeo con focos encendidos,
telemetría completa (inclinación, rumbo, batería, temperatura), conduces con el
joystick táctil, y desde la ROG lo mismo pero con sticks físicos.

## FASE 3 — Odometría, SLAM y nube de puntos del espacio

Sin encoders, la odometría sale de la visión (y opcionalmente del lidar):

- **3.1 RTAB-Map RGB-D con la OAK** — odometría visual (`rgbd_odometry`) + SLAM:
  genera el **mapa 3D (nube de puntos del espacio)** y la proyección 2D
  (`/map`) para Nav2. Contenedor `nav` con `rtabmap_ros`.
- **3.2 Fusión sensorial** — `robot_localization` (EKF): odometría visual + IMU
  → `/odom` estable y TF `odom → base_link`. Si la odometría visual patina en
  paredes sin textura, añadir odometría láser (`rf2o_laser_odometry`) como tercera fuente.
- **3.3 Alternativa/complemento 2D** — `slam_toolbox` con el STL-06 para un mapa 2D
  robusto; RTAB-Map puede consumir ese mapa y aportar solo la capa 3D/visual.
- **3.4 Persistencia** — guardar/cargar mapas (base de datos de RTAB-Map) para
  localización pura en sesiones posteriores (modo `localization`).

**Criterio de salida:** paseas el robot en teleop por la casa y en Foxglove se
construye la nube de puntos 3D del espacio; al reiniciar, el robot se localiza en
el mapa guardado.

## FASE 4 — Navegación autónoma (Nav2)

- **4.1 Nav2 bringup** — costmap global (mapa de SLAM) + costmap local (obstáculos
  de `/scan` + depth de la OAK vía `depthimage_to_laserscan` o voxel layer con
  `/oak/points`). Planner + controller (DWB o RPP) publicando en `/cmd_vel` (rama
  "nav" del twist_mux). Ajustar footprint al chasis y velocidades máx. a lo calibrado
  en 0.1.
- **4.2 Waypoints** — `nav2_waypoint_follower`: marcar puntos en Foxglove/RViz y que
  el robot haga la ruta. Guardar rutas con nombre ("ronda de la casa").
- **4.3 Exploración autónoma** — frontier exploration (`explore_lite` o
  `nav2_explore`): el botón de modo autónomo puede lanzar "explora y mapea todo el
  espacio tú solo".
- **4.4 Comportamientos con objetos** — combinar detecciones espaciales de la OAK con
  Nav2: "ve hasta la silla", seguir a una persona (spatial tracker on-device de la
  OAK + goal dinámico), detenerse ante mascotas.

**Criterio de salida:** desde la ROG pulsas el botón, marcas un destino en el mapa
(o eliges "explorar") y el robot navega esquivando obstáculos, reportando los
objetos que reconoce.

## FASE 5 — Energía y carga autónoma (el robot se cuida solo)

> ⛔ **5.1 y 5.2 SUPERADAS por la decisión D3 del PLAN MARATÓN (2026-07-07)**: fuente
> única = pack DeWalt 20V 6Ah DENTRO del módulo TORSO; el UPS 3S sale de la cadena
> crítica; dock propio con pogo pins cargando a 20.4V (~85-90%) con el robot siempre
> vivo (Jetson en espera). 5.3 y 5.4 siguen vigentes (docking AprilTag + battery_manager),
> ahora como parte de F6 del plan maratón. Detalles en `cad/MEDIDAS.md` § F0.

Prerequisito: fases 0–4 estables y medición real de consumo (el INA219 ya nos da
voltaje/corriente en vivo — la telemetría de 2.2 sirve para levantar el perfil de
consumo en teleop, patrulla y reposo antes de decidir batería).

- **5.1 Upgrade de batería** — el UPS del rover es 3S (12.6 V carga, 11.1 V nominal)
  con protección y carga integradas:
  - Opción segura: 18650 de alta capacidad y descarga real (Molicel P28A/Samsung 35E
    legítimas — muchas 18650 baratas mienten la capacidad). Cero cambios de hardware.
  - Opción LiPo: un pack **3S LiPo/Li-ion con BMS propio** de 8–12 Ah cabe en el rol,
    misma química de 4.2 V/celda ⇒ compatible con el cargador de 12.6 V del rover,
    pero hay que verificar corriente máx. de carga del circuito UPS y proteger/fijar
    bien el pack (los LiPo blandos son delicados en un chasis todoterreno).
  - Medir horas de autonomía objetivo: Pi 5 + OAK + lidar + motores ≈ 10–18 W según
    actividad; un 3S de 10 Ah (~110 Wh) daría en teoría 6–10 h de ronda mixta.
- **5.2 Base de carga** — dos caminos:
  - **Dock casero (recomendado)**: fuente CC/CV de 12.6 V limitada en corriente +
    dos pletinas de contacto en rampa, y contactos de resorte (pogo/pletina de
    cobre) bajo el chasis conectados al puerto de carga del rover. Diodo ideal para
    evitar chispazos al acoplar.
  - **Reusar dock Xiaomi**: ojo — los docks de aspiradoras Xiaomi entregan ~20 V,
    NO se puede conectar directo al puerto de 12.6 V del rover. Serviría solo como
    estructura mecánica/contactos añadiendo un regulador buck CC/CV a 12.6 V entre
    dock y robot. Viable, pero el dock casero es más simple y seguro.
- **5.3 Docking de precisión** — Nav2 lleva al robot a ~30 cm del dock (waypoint
  guardado en el mapa); la aproximación final es visual servoing sobre un
  **ArUco/AprilTag pegado en el dock** con la OAK (precisión de ±1 cm). Confirmación
  de acople: el INA219 detecta corriente de carga entrante. Si falla, reintenta con
  pequeño retroceso (hasta 3 veces) y notifica.
- **5.4 Autonomía energética completa** — nodo `battery_manager`:
  - Voltaje < umbral de aviso (p. ej. 10.5 V) → notificación + termina la ronda actual.
  - Voltaje < umbral crítico (p. ej. 10.0 V) → aborta lo que esté haciendo,
    `mode_manager` pasa a RETURN_TO_DOCK y navega a cargarse solo.
  - Cargado (corriente de carga cae + voltaje ≈ 12.5 V) → opcional: reanudar patrulla.
  - Último recurso: apagado limpio de la Pi antes del corte del BMS para no corromper
    la SD.

**Criterio de salida:** el robot patrulla, detecta batería baja, vuelve solo al dock,
se acopla, carga, y (si está configurado) retoma la ronda — sin intervención humana.

## FASE 7 (futuro) — Cerebro AI local: `waver_brain`

Validado conceptualmente (2026-07-03). Un nodo cognitivo dirigido por EVENTOS
(nunca en el lazo de control en tiempo real — los reflejos siguen en ROS):

- **Arquitectura**: `waver_brain` escucha eventos (detecciones YOLO, batería,
  horarios de ronda, mensajes del usuario) y emite decisiones de alto nivel:
  goals de Nav2, `/lights`, `/set_mode`, alertas push, snapshots.
- **Híbrido con fallback**: API de Claude con WiFi (razonamiento real:
  interpretar eventos, planear rondas, redactar alertas con contexto);
  fallback local sin internet con Ollama + modelo 3B cuantizado
  (Qwen 2.5 3B / Llama 3.2 3B: ~6-10 tok/s y ~3 GB RAM en Pi 5 de 8 GB).
- **VLM local opcional** (Moondream 2B): describir snapshots de alertas
  (~15-40 s/imagen, aceptable para eventos, no para tiempo real).
- **Restriccion**: inferir solo por eventos — la CPU compite con RTAB-Map/Nav2.
- **Upgrade path**: si el cerebro local queda corto, Jetson Orin Nano
  reemplaza a la Pi sin cambiar la arquitectura ROS.
- Prerequisitos: fases 3-4 (necesita mapa y navegación para actuar) y el
  nodo de notificaciones de la fase 2.2.

## FASE 6 — Para sacarle todo el jugo (backlog de ideas)

Visión/IA (la OAK hace el trabajo pesado on-device):
- **Seguir a una persona** con el spatial tracker (modo "mascota").
- **Mapa semántico**: anclar las detecciones 3D en el mapa ("aquí hay una planta,
  aquí el sofá") y navegar por nombre de objeto.
- **Control por gestos** (modelos de hand-tracking de DepthAI) y
  **control por voz o LLM**: un agente (Claude API) que traduzca "ve a la cocina y
  dime si hay alguien" a goals de Nav2 + consulta de detecciones.
- **ArUco/AprilTags**: además del docking (fase 5.3), localización barata y
  calibración de la curva PWM→velocidad midiendo contra un tag.
- **Reidentificación de caras/personas** para saludar en el OLED a quien reconozca.

Robot/plataforma:
- **Patrulla de vigilancia programada**: rondas nocturnas por waypoints en horarios
  (cron), integrando el modo vigilante de la web (2.2): detección de personas →
  snapshot + notificación con posición en el mapa.
- **Audio bidireccional**: la OAK-D Lite no trae micrófono; con un mic/altavoz USB
  en la Pi se añade intercomunicador ("¡quieto ahí!"), sirena y hasta comandos de voz.
- **Pan-tilt de Waveshare** (`{"T":133}`) para que la cámara rastree objetivos
  independientemente del chasis.
- **Gemelo digital**: completar el URDF y simular en Gazebo (reusar `ROS2_Docker_UI`)
  para probar Nav2 sin gastar batería.
- **Telemetría seria**: publicar voltaje/corriente del INA219 (`{"T":130}`) como
  `sensor_msgs/BatteryState`, alarma de batería baja → volver a base.
- **rosbag2**: grabar misiones (vídeo+scan+TF) y reproducirlas para depurar o
  entrenar modelos propios.
- **Dashboard web público en la Pi**: estado, mapa, vídeo y botones de misión,
  accesible desde cualquier móvil de la casa.

Brazos bimanuales:
- ⛔ **SUPERADO (2026-07-07)**: el plan de brazos 3GDL con servos reciclados y el
  CAD del brazo vishnu quedaron obsoletos. Decisión final: **2× brazo 6DOF de
  aluminio ROT3U completo (ThanksBuyer, "Arm Only")** usando los 13× MG996R ya
  comprados (compatibilidad 40×20/25T verificada), montados en el módulo **TORSO**
  elevable (L16-140-63-6-R + rieles 8mm). Historia completa y decisiones D1-D4 en
  `cad/MEDIDAS.md`; fases nuevas en el PLAN MARATÓN al final de este documento.
- Sigue vigente de aquel plan: PCA9685 (I2C 0x40), 2× UBEC 8-10A (uno por brazo,
  JAMÁS del 5V del host), meta LeRobot (datasets de demostración → política).

---

## Orden de ejecución sugerido y esfuerzo

| Paso | Entregable | Esfuerzo estimado |
|------|-----------|-------------------|
| 0.1–0.2 | cmd_vel + URDF/TF | 1–2 sesiones |
| 0.3–0.7 | IMU + lidar + mux + compose | 2–3 sesiones |
| 1.1–1.2 | OAK en ROS + Foxglove en la ROG | 2 sesiones |
| 2.1 + web teleop básica | Conducir desde ROG/celular + botón de modo | 2 sesiones |
| 1.3 | YOLO espacial on-device | 1 sesión |
| 2.2 | Dashboard vigilante completo (sensores, focos, eventos, Tailscale) | 3–4 sesiones (incremental) |
| 3.x | RTAB-Map + EKF + mapa persistente | 3–4 sesiones (la fase más delicada) |
| 4.1–4.2 | Nav2 + waypoints | 2–3 sesiones |
| 4.3–4.4 | Exploración autónoma + objetos | 2 sesiones |
| 5.1–5.2 | Batería nueva + dock físico | 1–2 sesiones + hardware |
| 5.3–5.4 | Docking ArUco + battery_manager | 2–3 sesiones |
| 6 | Backlog (Home Assistant, audio, voz/LLM…) | incremental |

Riesgos conocidos: presupuesto de corriente 5 V para Pi 5 + OAK; CPU de la Pi con
RTAB-Map + Nav2 simultáneos (mitigar bajando resolución de depth y delegando NN a la
OAK); odometría visual en pasillos sin textura y **a oscuras** (crítico para rondas
nocturnas: la odometría visual necesita luz — mitigar con focos IR/LED de IO4/IO5,
apoyarse más en lidar+IMU de noche); compatibilidad eléctrica del dock (nunca
conectar 20 V de un dock Xiaomi directo al puerto de 12.6 V); seguridad de acceso
remoto (solo vía VPN/tunnel autenticado).

---

## 🏁 PLAN MARATÓN (2026-07-07) — hoja de ruta oficial

**La demo**: en un diorama de estantes, el robot reconoce objetos, los agarra
(feedback visual de la cámara), navega esquivando obstáculos (cámara+lidar),
los deposita en otro lugar, y cuando su batería baja se acopla SOLO a su dock,
carga, sale y sigue — durante DÍAS, sin intervención humana. La métrica estrella
es un contador público de repeticiones consecutivas sin fallo. Todo el cómputo
(percepción, navegación, LLM del asistente de voz) corre embebido en la Jetson:
**la prueba del avión ✈️ = WiFi apagado y el robot sigue completo.**

**Las dos capas** (independientes, comparten cuerpo):
- **Capa A — Manipulación embebida**: percibir → agarrar → navegar → depositar.
  Alcanzable con objetos CONOCIDOS + visual servoing (absorbe la imprecisión de
  MG996R y base skid-steer). NO se promete "objetos arbitrarios" — eso es
  research-grade; escena controlada sigue siendo digno de tesis.
- **Capa B — Asistente "Jarvis"**: wake word + Whisper (STT) + LLM local +
  Piper (TTS) + herramientas estilo MCP (recordatorios, citas, pico y placa,
  gimnasio, oficina). Madura, útil desde el día 1, motivación cuando A se atasque.
  Si la tesis se valida: asistente personal de escritorio.

### F0 · Sala de decisiones — ✅ CERRADA (2026-07-07, bitácora en cad/MEDIDAS.md)

| # | Decisión | Veredicto |
|---|----------|-----------|
| D1 | Configuración módulo superior | **Torso elevable B directo**: sub-chasis fijo + torso ≤4kg que sube 140mm (L16-140-63-6-R, ya en mano). Rieles 8mm+LM8UU obligatorios |
| D1b | LiDAR | **Fijo en el sub-chasis** (SLAM 2D exige altura constante) |
| D2 | Cómputo | **Jetson Orin Nano Super 8GB SOLA**, migración por etapas; Pi 5 queda de repuesto caliente |
| D3 | Energía | **Fuente única DeWalt 6Ah dentro del TORSO** (junto a Jetson, con separación térmica). Robot SIEMPRE vivo; en dock = modo espera. Dock pogo pins propio a 20.4V. UPS viejo fuera de cadena crítica. 2× UBEC (uno por brazo) |
| D4 | Interfaz TORSO↔plataforma | **"4 tornillos M4 + XT30 12V + 1 USB serial JSON"**. Las plataformas se adaptan al TORSO |
| D5 | PLAN.md | Esta sección |

Reglas operativas que nacieron de F0 (invariantes del behavior tree):
1. **Navegar con torso ABAJO** (vuelco θ≈18° vs 14° arriba); subir solo detenido.
2. Ningún motor se mueve sin confirmación explícita de Andrés (regla de oro vigente).
3. Masa elevada ≤4 kg (retención del L16 sin corriente = 46N).
4. Carga a 20.4V (~85-90%), nunca 21V (packs de taladro no balancean).

### Las 8 fases (formato: objetivo / aprenderás / decides / validación)

**F1 · Cimientos en simulación** *(YA — no espera hardware)*
Gemelo digital: rover + TORSO (junta prismática) + 2 brazos 6DOF en Gazebo,
movidos por MoveIt2. Aprenderás: URDF/xacro, árbol TF, cinemática directa vs
inversa (con MG996R hacemos IK, no dinámica inversa real — esa exige control de
torque; el concepto se aprende en Gazebo, que sí simula dinámica), solvers IK
(KDL vs TRAC-IK), ros2_control. Decides: geometría del torso, nombres de joints,
solver. ✓: MoveIt2 lleva la garra a una pose objetivo en Gazebo.

**F2 · Percepción** — OAK-D → YOLO on-device (VPU) + pose 3D del objeto → TF.
Aprenderás: calibración intrínsecos/extrínsecos, nubes de puntos, por qué
"reconocer" es fácil y "dónde está en 3D" es lo difícil. Decides: los 3-5
objetos del diorama (tamaño garra, distintivos). ✓: RViz muestra el objeto
como frame TF estable con el robot en movimiento.

**F3 · Fusión cámara+lidar en Nav2** — depth del OAK a los costmaps (capa
voxel/STVL): esquiva lo que el lidar no ve. Aprenderás: costmaps por capas,
voxel grids. Decides: resolución/rango voxel (CPU vs detalle). ✓: caja baja
invisible al lidar → la esquiva.

**F4 · Brazos reales + visual servoing** *(al llegar brazos)* — PCA9685 (12
servos + L16 como canal 13), calibración pulso→ángulo, y el corazón: la cámara
ve garra y objeto y corrige en lazo cerrado. Aprenderás: calibración hand-eye,
lazo cerrado vs abierto. Decides: AprilTag en garra vs detección directa.
✓: pick 8/10 con la base en posiciones ligeramente distintas.

**F5 · Migración a Jetson + asistente local** — todo el stack a la Orin Nano
por etapas (1º OAK/percepción, 2º SLAM/Nav2, 3º base+web). LLM local cuantizado
+ Whisper + Piper + wake word + herramientas MCP. Aprenderás: cuantización
INT4/FP16, presupuesto de 8GB compartidos (el LLM compite con YOLO y Nav2),
TensorRT. Decides: tamaño del LLM (3B holgado vs 7B apretado) CON benchmark
real. ✓: la prueba del avión.

**F6 · Dock de carga con pogo pins** — diseño+fabricación: geometría de
auto-alineación (embudo/rampa: la mecánica perdona lo que el software no logra)
+ AprilTag + `opennav_docking` (Nav2 oficial: se estudia, no se inventa).
INA3221 confirma corriente de carga = acople exitoso; reintentos con retroceso.
Aprenderás: electrónica de carga CC/CV, docking de precisión. Decides: ubicación
del dock en el diorama. 🔴 No negociable: fusible, termistor, corte por
sobre-temperatura, superficie ignífuga, protocolo validado ANTES de la maratón.
✓: 10 dockings consecutivos sin intervención.

**F7 · Orquestación + confiabilidad** — behavior tree (BehaviorTree.CPP, el
motor interno de Nav2): patrullar → detectar → agarrar → transportar → depositar
→ ¿batería? → dock → repetir. Watchdogs, políticas de reinicio Docker,
recuperación ante fallo (3 reintentos → saltar y registrar), telemetría con
dashboard (contador de repeticiones, éxitos/fallos, temperatura Jetson,
corriente por servo). **El dashboard ES la demo.** Aprenderás: behavior trees
vs máquinas de estado, diseño para fallo, observabilidad — lo más transferible
a cualquier proyecto futuro. ✓: 24h en simulación/mesa sin cuidador.

**F8 · La maratón** — runs incrementales 2h → 8h → 24h → 72h, análisis de cada
fallo entre runs (cada fallo = lección documentada). Métrica: repeticiones
consecutivas sin intervención humana, en contador gigante.

### Riesgos propios de la maratón (además de los históricos)
1. **Desgaste de MG996R**: miles de ciclos desgastan engranajes/potenciómetro.
   Comprar 2-3 repuestos, monitorear corriente por servo como indicador, agarres
   sin carga sostenida. La maratón es también un experimento de vida útil.
   Upgrade no destructivo: DS3225 (25kg, mismo cuerpo/spline) en hombros.
2. **Térmica de la Jetson**: LLM+visión+Nav2 por días = throttling sin flujo de
   aire. El CAD del TORSO incluye ventilación y deflector (el exhaust no puede
   bañar el pack de litio).
3. **Presupuesto energético**: trabajo 38-45W ≈ 3h/carga; recarga ~2h → ritmo
   3:2 ✓. Validar con INA3221 real ANTES de construir el dock.
4. **Carga desatendida de litio = el riesgo #1 del proyecto** — ver F6.

### Método de trabajo (anti-caja-negra, acordado)
1. Mini-clase del concepto antes de tocar código.
2. Opciones con trade-offs presentadas → **Andrés decide**.
3. Código por capas pequeñas, legibles y cuestionables.
4. Cada fase cierra con validación medible + entrada de bitácora (patrón ADR
   de MEDIDAS.md extendido a todo el proyecto).
5. **Grabar SIEMPRE los hitos y los builds en video** (el material crudo es
   irrecuperable) y actualizar la tabla de estado de `ROADMAP.md` al cerrar
   cada fase.

### Dependencias y arranque
F1→F4 (la sim valida antes del hierro) · F2→F3,F4 · F6→F8 · F7→F8 ·
F5 es paralela (victoria motivacional). Pendiente de sesiones anteriores que
sigue en cola: fusión gyro QMI8658→EKF (deuda de Fase 3, arregla derrape del
mapa — victoria rápida en robot vivo). **Próximo paso: F1 (URDF del TORSO
completo + Gazebo + MoveIt2), que no espera ningún paquete de AliExpress.**
