# WAVER Roadmap: The Marathon Demo

**The goal:** a mobile manipulator that works unattended for days.

In a shelf diorama, WAVER recognizes known objects, picks them up using
closed-loop visual feedback, navigates around obstacles fusing camera and
LiDAR, places them somewhere else, and when its battery runs low it finds
its charging dock, aligns, docks itself, charges, undocks and keeps working.
The headline metric is a public counter: **consecutive pick and place cycles
without human intervention.**

Everything runs on board. Perception, navigation, manipulation and a local
voice assistant (wake word, speech to text, LLM, text to speech) all live on
an NVIDIA Jetson Orin Nano. The acceptance test is what I call the airplane
test: turn off the WiFi and the robot still sees, plans, talks and grabs.

## Architecture

Two decoupled parts, so the "being" of the robot can move to a future
platform (tracks, a bigger base) without touching the software stack:

```
TORSO module (self-contained backpack)
├── Sub-chassis (fixed): battery, Jetson, LiDAR, PCA9685,
│   dock contacts, base of the elevation column
└── Elevating trunk (max 4 kg): two 6DOF aluminum arms,
    depth camera as the "face", 140 mm of vertical travel
    driven by a linear actuator (Actuonix L16)

Platform (today: Waveshare Wave Rover): wheels + ESP32
Interface contract: 4 bolts, one XT30 power connector, one USB cable
```

Why an elevating trunk? Hobby servos (MG996R) are strong only in compact
poses: at 30 cm of horizontal reach their useful payload is close to zero.
The column moves the whole workspace up and down 140 mm, so the arms always
work folded, cool and precise. Vertical coverage comes from the spine, not
from stretching. That is also how the robot survives thousands of cycles:
compact poses mean low sustained torque, which means servos that last.

## Engineering rules (decided with numbers, logged in cad/MEDIDAS.md)

1. Navigate with the trunk DOWN (tip-over margin 18° vs 14° raised).
2. Elevated mass stays under 4 kg (the L16 holds 46 N with power cut).
3. Charge the tool battery to 20.4 V (~85%), never to the top: drill packs
   do not balance cells, and partial charging multiplies cycle life.
4. The LiDAR never rides the elevator: 2D SLAM needs a constant scan height.
5. Dock contacts are dead by default and only energize after a handshake.

## Phases

| Phase | What | Status |
|-------|------|--------|
| F0 | Architecture decisions (torso, compute, power, interfaces) | ✅ Closed |
| F1 | Digital twin: full URDF + Gazebo + MoveIt2, before any hardware | 🚧 In progress (URDF done: 15 joints, validated) |
| F2 | Perception: on-device object detection + 3D pose as TF frames | Planned |
| F3 | Camera + LiDAR fusion in Nav2 costmaps (dodge what LiDAR can't see) | Planned |
| F4 | Real arms + visual servoing: camera closes the loop on the grasp | Waiting on hardware |
| F5 | Full migration to Jetson + 100% local voice assistant (airplane test) | Waiting on hardware |
| F6 | Charging dock: magnetic pogo contacts, AprilTag docking, opennav_docking | Planned |
| F7 | Orchestration: behavior tree + watchdogs + live metrics dashboard | Planned |
| F8 | The marathon: 2h → 8h → 24h → 72h unattended runs | The finish line |

## What gets measured

The dashboard IS the demo: consecutive cycles, success/failure per stage,
charge cycles, Jetson temperature, per-servo current (a rising current is a
wearing gearbox). Every failure between marathon runs becomes a documented
lesson, and the full telemetry will be published as an open dataset.

## Base stack (already running)

ROS 2 Humble in Docker on a Raspberry Pi 5: SLAM without wheel encoders
(rf2o laser odometry + IMU + EKF + slam_toolbox), Nav2 tuned for skid-steer,
OAK-D Lite spatial detection, web command center. The Pi hands over to the
Jetson in F5 and stays as a hot spare.

Follow the build: videos and write-ups are published as each phase closes.
