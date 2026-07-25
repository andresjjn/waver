# HANDOFF → Proyecto SOMA (Skilled Operator via Mimicry & Autonomy)

Documento de traspaso para la sesión que crea `andresjjn/soma-arms`: la librería
embodied AI de los 2 brazos 6DOF, independiente de Waver y futura dependencia
suya. Escrito 2026-07-25 tras el primer encendido real (2026-07-22).

## 1. Qué es SOMA y cómo termina

Librería ROS2 para los brazos duales, con escalera pública de releases
(cada versión = tag + video en README + short en inglés):

| Versión | Entregable |
|---|---|
| v0.1 | URDF con medidas REALES de calibrador + RViz + CI (tests + xacro) |
| v0.2 | Driver real: sliders → metal (el código ya existe, ver §3) |
| v0.3 | MoveIt2: trayectorias planeadas, poses candle/compact |
| v0.4 | Teleop básica (teclado/web) |
| v0.5 | Teleop por visión: OAK-D Lite + BlazePose en la VPU → los brazos imitan |
| v1.0 | "Operario": 2h de ciclos pick-and-place en banco, contador público. FIN |

Al llegar v1.0 el proyecto se CIERRA y los brazos se integran a Waver
(plataforma móvil, demo maratón). Regla anti-pozo-sin-fondo: lo que falte en
v1.0 se vuelve issues, no razones para no volver a Waver.

Paquetes: `soma_description`, `soma_driver`, `soma_moveit_config`,
`soma_teleop`, `soma_operator`.

## 2. El hardware (verdad medida, no datasheet)

- 2 brazos 6DOF de aluminio (kit ROT3U-like, manual en
  `Manual de ensamble ^ DOF arm.pdf` en la raíz de Waver, 30 págs).
- Servos: **MG996R** (~10 kg·cm) — NO los "25KG" que anuncia el manual.
  Regla derivada: poses compactas siempre (a 30 cm de alcance el payload
  útil es ~330 g). PWM 500-2500 µs sobre ±90°, 50 Hz.
- Cadena por brazo (nomenclatura de Andrés → URDF): rotación de hombro =
  `yaw` (A), elevación = `shoulder` (B), codo 1 = `elbow` (C), codo 2 =
  **`wrist_pitch`** (D, cabecea igual que el codo), rotación de muñeca =
  `wrist_roll` (E), pinza = garra de engranajes (F; dedo derecho es mimic
  ×-1 del izquierdo, SIN canal propio).
- Torso: actuador lineal **Actuonix L16-140-63-6-R** (140 mm, 100 N máx,
  46 N hold SIN energía —husillo autoblocante—, 20 mm/s, 6V, RC 1-2 ms).
- Driver: PCA9685 (I2C 0x40) en Raspberry Pi 5 (bus 1, pines 1/3/5/6).
- **Mapa de canales VERIFICADO CON POTENCIA** (2026-07-22): brazo derecho
  15→10 (garra primero, de externo a interno), izquierdo 9→4 igual,
  **L16 = canal 3** (el 0 quedó bajo sospecha tras fallas; 0-2 repuesto).
  La placa NO trae serigrafía de canales.
- **L16 INVERTIDO (medido)**: 2000 µs = retraído, 1000 µs = extendido.
- Potencia: LiPo 2S → interruptor+fusible → UBEC 6V → borne V+ del PCA9685.
  JAMÁS la LiPo directa (8.4V llena > 7.2V máx del MG996R). Falta 2º UBEC
  (plan: uno por brazo).
- URDF: TODAS las longitudes de eslabón están `[calibrar]` (estimadas de
  fotos del manual). **Medirlas con calibrador es prerequisito de v0.1.**
  También pendiente: peso real por brazo y patrón de tornillos de la base.

## 3. Código que se MIGRA (no se reescribe)

Desde `/Users/andresjjn/Projects/Robotics/Waver/ROS2_Docker_twin/ros2_ws/src/`:

- `waver_arm_description/` → `soma_description` (+ `soma_moveit_config`):
  xacro paramétrico del brazo (macro ×2), URDF del ensamble, SRDF con grupos
  y poses candle/compact, controllers.yaml (JTC), kinematics.yaml (KDL;
  TRAC-IK pendiente de decidir), launch de RViz con sliders.
- `waver_arm/` → `soma_driver`: `servo_map.py` (PURO, testeable sin ROS;
  contiene el mapa verificado y su documentación), `pca9685_backend.py`
  (Mock default + Real con regla de oro + reintentos I2C), 
  `arm_controller_node.py` (rampa 50 Hz, mimics, auto-release del torso),
  `test/` con **24 tests** que codifican TODOS los contratos de hardware.
  Los tests son la especificación: si migrando algo se rompe uno, el error
  está en la migración, no en el test.

Al terminar la migración: Waver borra sus copias e importa SOMA
(submódulo/vcstool) — anotarlo como tarea en Waver.

## 4. Reglas de seguridad INVIOLABLES (van al CLAUDE.md de SOMA)

1. **JAMÁS mover motores sin confirmación explícita previa de Andrés.**
   Codificada: `RealPca9685(armed=False)` lanza `PermissionError`; el nodo
   arranca MOCK y DESARMADO; armar = servicio SetBool explícito.
2. **Nunca sostener comandos contra topes físicos.** El L16 se ACUÑÓ contra
   su tope interno el 2026-07-22 (comando sostenido estando ya en el límite)
   y hubo que liberarlo a mano (extender + tracción manual). Mitigado con:
   límites suaves 5-135 mm (anchors 1964.3-1035.7 µs) y auto-release
   (asentado 0.5 s → señal fuera; el husillo sostiene solo). Los servos de
   brazo NUNCA se liberan (necesitan par activo o el brazo se cae).
3. Energizar V+ siempre con brazos en pose compacta apoyada (los MG996R
   clones dan latigazo de power-on).
4. Conectores: los dupont fallan (3 caídas de bus I2C en una sesión por un
   dupont roto por dentro). Arnés definitivo: JST con seguro para I2C,
   retén de silicona en conectores de servo, V+ con cable ≥16 AWG.

## 5. Entorno y herramientas validadas

- Pi 5: SSH con alias `waver_robot` (usuario ros, raspberrypi.local).
  ROS2 Humble corre en Docker en la Pi. smbus2 disponible nativo.
- Scripts YA en la Pi (`/home/ros/`): `pca9685_check.py` (validación sin
  potencia: 50 Hz, eco de registros, FULL_OFF) y `servo_discovery.py`
  (identificación canal por canal con bursts de 60 ms). Protocolo probado.
- Twin en la Mac: RViz EN NAVEGADOR con `tiryoh/ros2-desktop-vnc:humble`
  → http://localhost:6080/vnc.html. Gotchas resueltos: lanzar como
  `-u ubuntu` con `DISPLAY=:1 HOME=/home/ubuntu`; montar con ruta ABSOLUTA.
  Config lista en `.claude/launch.json` de Waver (`twin-vnc`).
- Smoke test E2E de referencia: `ROS2_Docker_twin/scripts/smoke_test.sh`
  (build + tests + xacro + TF verifica +140 mm del torso). Gotcha: URDF a
  robot_state_publisher por `--params-file` (por `-p` CLI rompe el parser).
- Tests locales rápidos en la Mac: venv con pytest basta (servo_map es puro).
- Cámara: OAK-D Lite disponible (hoy en Waver); para v0.5 corre BlazePose
  en su VPU (depthai), la Pi solo recibe landmarks.

## 6. Pendientes técnicos que SOMA hereda

- Calibración fina con potencia (era task #14 de Waver): offset de horn,
  signo y rango seguro por servo; topes REALES del L16 en µs (llevarlo por
  pasos de 25 µs midiendo con regla hasta que deje de avanzar, -5 mm).
  Un servo a la vez, bursts, nunca contra topes.
- Medidas de calibrador para el URDF (§2) — prerequisito v0.1.
- Decidir KDL vs TRAC-IK con pruebas reales (v0.3).
- Gazebo con física + controladores activos (el twin solo corrió RViz).

## 7. Reglas de marca (contenido público del repo)

- README y docs públicos EN INGLÉS. Sin guión largo "—" en textos públicos.
- Números honestos siempre (specs medidas > specs de fabricante).
- NDA Perficient: jamás mencionar clientes/código del empleo actual.
- Nada de estrategia de búsqueda laboral en repos públicos.
- Cada release: tag + video en README + short EN + bullet de CV.

## 8. Contexto entre sesiones

- Con Andrés se habla SIEMPRE en español.
- La bitácora maestra de decisiones de hardware sigue siendo
  `Waver/cad/MEDIDAS.md` (leerla ante cualquier duda de historia).
- El CLAUDE.md de SOMA debe apuntar de vuelta a este archivo y a MEDIDAS.md
  (sección "ecosistema Waver").
