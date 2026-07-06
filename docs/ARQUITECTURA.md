# WAVER — Arquitectura completa, decisiones y lecciones (al 2026-07-05)

Documento de estudio. Cada sección termina con el **porqué** — las decisiones son
lo que se transfiere a cualquier robot futuro; los comandos se olvidan.

---

## 1. Vista de pájaro

```
 Mac (dev/teleop)          Raspberry Pi 5 (4GB, Bookworm 64)          ESP32 (firmware propio)
 ┌──────────────┐   WiFi   ┌──────────────────────────────┐   I2C    ┌──────────────────┐
 │ Foxglove app │◄────────►│ Docker: 5 servicios + 2      │◄────────►│ waver_slate_v2   │
 │ joystick py  │  5GHz    │ perfiles (ROS2 Humble)       │  0x11    │ motores+failsafe │
 │ Claude Code  │  .16     │                              │          │ + luces reg 0x01 │
 └──────────────┘          └──────┬───────────┬───────────┘          └──────────────────┘
                                  │USB        │/dev/i2c-1 (bus compartido de la Pi)
                            LD06 lidar        ├── QMI8658 IMU (0x6B)   acc+gyro
                            OAK-D Lite        ├── AK09918 mag (0x0C)
                                              ├── INA219 (0x42)  V/I batería
                                              └── SSD1306 OLED (0x3C) panel batería
```

- La Pi lee TODOS los sensores I2C directamente; el ESP32 solo ejecuta motores
  (protocolo propio, failsafe de 1 s si no llegan comandos) y luces.
- **Por qué**: separar el tiempo-real barato (ESP32) del cómputo (Pi), y un solo
  dueño del bus I2C evita colisiones.

## 2. Contenedores (docker-compose en ~/Waver)

| Servicio | Contenido | Puertos/dispositivos |
|---|---|---|
| `base` | robot_state_publisher (URDF), cmd_vel_to_motors, twist_mux, imu, battery×2, display, lights, mode_manager | /dev/i2c-1 |
| `lidar` | ldlidar_stl_ros2 → `/scan` 10 Hz | /dev/ttyUSB0 |
| `oak` | depthai_ros_driver (RGB+estéreo+YOLO espacial on-device, ROTATE_180) | USB3 |
| `web` | dashboard :8000, rosbridge :9090, video :8080, **foxglove_bridge :8765** | — |
| `slam` (perfil) | rf2o + EKF (robot_localization) + slam_toolbox | — |
| `nav` (perfil) | Nav2 | — |

Decisiones:
- **`ipc: host` + `network_mode: host` en todos**: FastDDS usa memoria compartida
  entre procesos del mismo host; sin ipc:host los contenedores no se ven.
- **waver_web usa CycloneDDS** (UDP): el bridge foxglove/rosbridge convive mejor;
  el resto FastDDS. Interoperan por UDP loopback.
- **Trampa YAML documentada**: los `command:` del compose van en UNA línea o
  terminando en `&&` — el folded scalar de YAML rompe silenciosamente.
- **Trampa DDS + IP**: los participantes DDS anuncian la IP del host al nacer.
  Si la IP cambia con contenedores vivos, el descubrimiento queda incoherente
  (bug cazado: tópicos invisibles para el bridge). Boot limpio lo cura.

## 3. Control de movimiento

```
joystick Mac ──► /joy_vel (prio 100) ─┐
web dashboard ─► /web_vel (prio 90) ──┤ twist_mux ─► /cmd_vel ─► cmd_vel_to_motors ─► I2C
Nav2 ─────────► /nav_vel (prio 10) ───┤   locks: /e_stop (255), /lock_nav (50)
                                      └─ timeout 0.5 s por fuente
```

- **v_max = 0.8 m/s** calibrada físicamente (2.4 m en pulso de 3 s a PWM 255,
  medido con metro 2026-07-04). PWM útil: 40–255 (bajo 40 no vence fricción).
- **MAX_ANG altísimos (16/12/10 rad/s)**: NO son error — skid-steer sin encoders
  patina al girar; se necesita sobre-comandar. REGLA: no "corregirlos".
- **Failsafe**: ESP32 detiene motores si no recibe I2C en 1 s → zona WiFi muerta
  = robot parado, seguro.

## 4. Odometría y SLAM (la fase más delicada)

Sin encoders. La odometría nace del láser:

```
/scan (LD06, 10Hz) ─► rf2o_laser_odometry ─► /odom_rf2o ─► EKF ─► TF odom→base
                                                            ▲
/imu/data_raw (50Hz, gyro) ────────────────────────────────┘
/scan + TF ─► slam_toolbox (async) ─► /map + TF map→odom
```

- **EKF (robot_localization)**: fusiona la POSE de rf2o en modo `differential`
  (consume deltas) + **vyaw del giroscopio**. 
  - **Bug histórico**: fusionar el *twist* de rf2o (publica casi-cero) → 1 m real
    medía 9 cm. Lección: en fusión sensorial, verifica QUÉ publica realmente
    cada fuente (`ros2 topic echo`), no lo que "debería" publicar.
- **El gyro es el ancla de los giros**: el matching láser se pierde en rotaciones
  rápidas (a 10 Hz el mundo gira demasiado entre barridos) → derrapes en el mapa.
  Mitigación de manejo: giros lentos + pausa; cierre de lazos endereza el resto.
- **Mapas**: serializados con `tools/save_map.sh` (posegraph + data) → después
  slam_toolbox en modo localización sobre el mapa cargado.
- rf2o necesita el TF del URDF (`base_footprint`) y el frame del IMU debe existir
  (`imu_link`) o robot_localization descarta mensajes EN SILENCIO.

## 5. Energía (el cuello de botella real del proyecto)

- **Medición**: INA219, shunt 0.01 Ω — solo ve la rama de CONSUMO: la corriente
  del cargador es invisible → "CARGANDO" se infiere por tendencia de voltaje.
- **battery_manager v2**: WARN 11.1 V → CRITICAL 10.8 → apagado 10.4 sostenido
  60 s (debounce 300 @ 5 Hz) + flag a disco + watchdog systemd del host con
  ventana de recuperación 30 s. 
  - **Bug histórico**: un colcon build hunde el pack ~1 V 20 s → apagado en falso.
    Lección: TODO umbral necesita debounce dimensionado al transitorio real.
- **OLED**: driver SSD1306 propio (sin librerías, framebuffer por I2C), fuente
  5x7, voltaje/porcentaje/corriente/temp CPU, tendencia de carga, **latido**
  (punto parpadeante — si está quieto, la Pi murió: el OLED retiene su RAM).
- **Decisión batería (2026-07-05)**: pack de taladro 20V (compatible DeWalt,
  2×6 Ah) + cuna adaptadora + buck 20 A → 12 V + **2º INA219 en 0x41** midiendo
  el lado del pack + alarma buzzer. Hot-swap, cargador comercial, doble capacidad.
- **Dock (Fase 5) rediseñado**: "dock tonto, robot listo" — pletinas 24 V en la
  pared; el robot lleva su propio CC/CV 21 V/3 A conmutado por ROS, terminación
  por voltaje+corriente+temperatura+timeout. El docking de precisión sigue igual
  (Nav2 → ArUco → INA219 confirma).

## 6. Red y arranque autónomo (saga 2026-07-05)

Causa raíz de TODA la inestabilidad: **módulo WiFi interno dañado por golpe**
(-80 dBm al lado del router, desconexiones, carrusel de IPs .16→.15→.69, "boot
fantasma", sshd colgado por conexiones muertas).

Configuración final:
- **Realtek RTL8821CU USB (wlan1) única interfaz**: JEJEN_5G anclada por **MAC**
  (sobrevive renombres), IP estática 192.168.1.16, JEJEN 2.4 GHz de respaldo
  (misma IP), interna muerta vía `dtoverlay=disable-wifi`.
- Power save WiFi off (NetworkManager conf + deep-sleep rtw88 off) + udev
  anti-autosuspend USB del adaptador.
- **`systemctl enable docker.service`**: antes era socket-activated → tras reboot
  NADA arrancaba hasta el primer comando docker (ni el watchdog de batería).
  Con esto + `restart: unless-stopped`, el robot revive solo al encender.
- sshd endurecido: `ClientAliveInterval 15` + `MaxStartups 30:30:100` (las
  conexiones muertas ya no lo ahogan).
- Trampas aprendidas: botón de encendido de Pi 5 con sistema vivo = shutdown
  LIMPIO (no corte); daemon CLI de ros2 queda zombi tras reiniciar contenedores
  (`ros2 daemon stop`); verificar /scan por logs de rf2o, no por el CLI.

## 7. Visualización y operación

- **Foxglove app de escritorio** (la web pelea con mixed-content): conexión
  `ws://192.168.1.16:8765`. Paneles: 3D (/map + /scan + TF), Image, Raw /battery.
- Dashboard web propio :8000 (radar lidar, cámara, teleop táctil, telemetría).
- Claude opera la Mac con `screencapture` + `cliclick` (permisos de Grabación
  de pantalla y Accesibilidad) — usado para armar el layout de Foxglove.

## 8. CAD (iniciado 2026-07-05)

- **OpenSCAD paramétrico** en `cad/plataforma.scad` — CAD-por-código: las medidas
  del URDF son variables; Claude edita, Andrés ve en vivo (Automatic Reload).
- Diseño WAVER CRAB: bandeja atornillada + bahía de batería **pasante** trasera
  (CG mínimo, swap por atrás) + **torre-periscopio del lidar** (el pack de 80 mm
  superaba el plano de barrido a 57 mm → el LD06 sube y barre sobre TODO) +
  visor OAK frontal + 2 brazos cangrejo (yaw S3003 → hombro MG996R → codo MG996R
  → muñeca S3003 → pinza MG996R, dedo fijo + móvil) + caparazón facetado.
- Regla de oro heredada: **nada cruza el plano del lidar** (anillo fantasma en
  el modelo lo audita visualmente).

## 9. Stack exacto (librerías y herramientas)

| Capa | Tecnología |
|---|---|
| OS robot | Raspberry Pi OS Bookworm 64-bit |
| Middleware | ROS 2 Humble (contenedores Docker) |
| DDS | FastDDS (SHM, ipc:host) + CycloneDDS (waver_web) |
| Percepción | ldlidar_stl_ros2, depthai_ros_driver (YOLO on-device), rf2o_laser_odometry |
| Fusión/SLAM | robot_localization (EKF), slam_toolbox (async) |
| Navegación | Nav2 (DWB), twist_mux |
| Hardware IO | smbus2 (I2C directo: IMU/INA219/OLED/ESP32), pygame (joystick Mac) |
| Puentes | foxglove_bridge, rosbridge_suite, web_video_server |
| Host | systemd (watchdog batería, docker), NetworkManager, udev |
| CAD | OpenSCAD (paramétrico, git-friendly) |
| Dev | Claude Code (SSH a la Pi, cliclick+screencapture en Mac, Chrome MCP) |

## 10. Los 5 bugs épicos (casos de estudio de depuración)

1. **EKF 9 cm/1 m**: fusionaba twist casi-cero de rf2o. → Verifica los DATOS de
   cada fuente, no su nombre.
2. **Apagado en falso**: sag de 1 V por colcon build cruzó umbral 20 s. →
   Debounce dimensionado al peor transitorio + ventana de recuperación.
3. **Boot fantasma**: WiFi cayó (auth-fail 5G), Pi corrió invisible 90 min; el
   botón la apagó LIMPIAMENTE justo cuando "la encendían". → Los logs de journal
   reconstruyen todo; el hardware dañado imita bugs de software.
4. **OLED congelado**: la pantalla retiene su último frame sin alimentación de
   datos → parecía viva con la Pi muerta. → De ahí el "latido" parpadeante.
5. **Tópicos invisibles en Foxglove**: contenedores nacidos con IPs distintas
   durante el caos DHCP → anuncios DDS incoherentes. → IP estática + boot limpio;
   en DDS, la identidad de red es parte del descubrimiento.

## 11. Reglas inviolables del proyecto

1. JAMÁS mover motores sin confirmación explícita del operador.
2. No "corregir" los MAX_ANG del skid-steer.
3. `command:` del compose en una línea o `&&`.
4. Nada cruza el plano de barrido del lidar.
5. Sesiones en español; el conocimiento se documenta en PLAN.md y aquí.
