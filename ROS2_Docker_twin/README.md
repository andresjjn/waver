# ROS2_Docker_twin — Gemelo digital WAVER CRAB (Fase F1)

Workspace del gemelo digital: URDF/xacro del robot completo de la demo maratón
(rover + módulo TORSO elevable + 2 brazos 6DOF de aluminio a ±45°). Corre en el
computador de desarrollo (Mac/PC), **no** en la Pi.

## Contenido

```
ros2_ws/src/waver_arm_description/
├── urdf/
│   ├── arm_6dof.xacro          # macro del brazo (se instancia 2 veces)
│   ├── arm_standalone.urdf.xacro  # 1 brazo en pedestal (estudio/calibración)
│   ├── waver_crab.urdf.xacro   # ensamble completo: rover+TORSO+2 brazos
│   └── materials.xacro
├── launch/display.launch.py    # RViz + sliders por joint
└── rviz/twin.rviz
```

## La cadena del brazo (del manual del kit, 30 pág.)

| Servo | Joint URDF | Eje |
|---|---|---|
| A | `*_yaw_joint` (base sobre rodamiento) | Z |
| B | `*_shoulder_joint` | Y |
| C | `*_elbow_joint` (bloque doble servo) | Y |
| D | `*_wrist_pitch_joint` | Y |
| E | `*_wrist_roll_joint` | Z local |
| F | `*_finger_l_joint` + `*_finger_r_joint` (mimic ×-1, garra de engranajes) | X local |

Además: `torso_lift_joint` **prismática** (Actuonix L16-140: 0–0.14 m,
100 N, 0.02 m/s) entre el sub-chasis y la placa-torso.

⚠️ Todas las longitudes están marcadas `[calibrar]` en `arm_6dof.xacro`:
son estimadas de las fotos del manual. Al llegar el kit se miden con
calibrador y se corrigen las propiedades UNA vez.

## Cómo visualizarlo (reusa la imagen de ROS2_Docker_UI)

```bash
cd ROS2_Docker_UI && ./scripts/build   # si aún no existe la imagen

docker run -it --rm \
  -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$(pwd)/../ROS2_Docker_twin/ros2_ws:/ros2_ws" \
  ros2_ui_image bash -c \
  "cd /ros2_ws && colcon build --symlink-install && source install/setup.bash && \
   ros2 launch waver_arm_description display.launch.py"
```

Con `model:=arm_standalone.urdf.xacro` se ve un solo brazo en pedestal.
Mueve los sliders del `joint_state_publisher_gui`; el dedo derecho es mimic
del izquierdo (la garra de engranajes se espeja sola).

## Validación sin ROS (en la Mac pelada)

`pip install xacro urdf-parser-py` y el script de la sesión (scratchpad)
procesa los xacro y verifica árbol/nombres/límites. Última corrida:
ambos modelos ✅ (CRAB: 29 links, 28 joints, 15 móviles, 6.26 kg;
masa elevada 2.4 kg ≤ 4 kg regla D3 ✓).

## Próximos pasos de F1

1. Gazebo: `<gazebo>` tags + `ros2_control` (posición por joint).
2. MoveIt2: SRDF + grupos `left_arm`/`right_arm` + IK (TRAC-IK).
3. Nodo `waver_arm` con driver PCA9685 **mock** (regla de oro: ningún
   motor real sin confirmación explícita).
