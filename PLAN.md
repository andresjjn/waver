# Plan Maestro — Wave Rover + OAK-D Lite: de teleoperación a navegación autónoma

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

**Deuda técnica para Fase 3:**
- **Celdas 18650 agotadas** (sag ~1 V con ráfaga de CPU, ~2 h de autonomía):
  decidido reemplazo por **LiPo/Li-ion 3S CON BMS integrado**, ≥5 Ah (XT60);
  cargarla externamente si es RC pelada — nunca por el UPS sin verificar.
- **Fijación mecánica de conectores USB** (lidar y OAK): ambos se soltaron
  durante la sesión al manipular el robot — brida/hot-glue antes de rondas.
- `/oak/points` mudo desde la rotación 180° de los sensores (publisher existe,
  no fluyen datos): depurar interacción con el pipeline de pointcloud.
- La OAK negocia **USB 2.0** (`USB SPEED: HIGH`): el adaptador USB-A→C actual solo
  cablea pines 2.0. Conseguir cable USB-A 3.0→C de una pieza (marcado SS/5Gbps) y
  conectar al puerto azul → debe decir `SUPER`. Nota: el USB-C de la Pi 5 es SOLO
  alimentación, nunca para la cámara.
- `/oak/points` no aparece pese a `pointcloud.enable:=true` — revisar config del
  driver depthai antes del SLAM.
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

Brazos bimanuales con servos reciclados (decidido 2026-07-04):
- **Dos brazos de 3 GDL + pinza** (estilo cangrejo, esquinas frontales), alcance
  corto 15-18 cm, carga ~100-150 g por pinza. Reparto de servos del inventario:
  hombro elevación y codo = MG996R (los 4 existentes); pinzas = 2× MG996R **a
  comprar** (agarrar = stall continuo → engranaje metálico obligatorio); hombro
  giro (yaw) = 2× S3003 (no pelea contra gravedad). Sobrantes: MG995 (pan) +
  S3003 (tilt) → **pan-tilt del OAK**, + 3× S3003 repuesto. Descartado stepper
  en yaw: peso (NEMA17 ~280 g), homing necesario y holding current en batería.
- **Compras pendientes**: PCA9685 (I2C 0x40, convive con ESP32 en 0x11),
  UBEC 12V→6V 8-10A (picos MG996R ~2.5A c/u; JAMÁS del 5V de la Pi),
  2 kits brackets aluminio servo estándar, 2× MG996R (tienda >4.7, ojo fakes).
- **Software**: nodo `arm_controller` (patrón del motor driver), URDF de brazos,
  IK planar 2 eslabones, pipeline OAK (posición 3D en metros) → frame del brazo
  → agarre. Meta final: datasets de demostraciones + política con LeRobot.
- Si algún día se quiere más músculo: RoArm-M2-S (combo oficial Waveshare,
  base 163 mm ≈ toda la tapa, ~850 g, CG alto) o brazo en base fija de
  escritorio colaborando con el rover vía ROS 2. Decisión pospuesta a que
  los brazos baratos enseñen qué se necesita de verdad.

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
