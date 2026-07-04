# Waver — Autonomous Home Rover

**A ROS 2 rover that maps and patrols a real house: SLAM without wheel encoders, on-camera spatial AI, Nav2 autonomy — the whole stack in Docker on a Raspberry Pi 5.**

Built on a Waveshare Wave Rover chassis (~$120) + LD06-class lidar + OAK-D Lite. No wheel encoders exist on this platform, so odometry comes from the lidar itself (`rf2o` laser odometry fused with IMU in an EKF). Skid-steer, budget hardware, honest engineering.

## What it does

- 🗺️ **SLAM with zero wheel encoders** — `rf2o_laser_odometry` + IMU → `robot_localization` EKF → `slam_toolbox`. The critical fix that made it work: fuse rf2o's **pose differentially, not its twist** (which publishes near-zero) — a 1 m straight-line test went from 9 cm estimated to 1.03 m.
- 👁️ **Spatial object detection on-camera** — OAK-D Lite runs YOLO on-device (zero Pi CPU), publishing RGB, stereo depth, detections and a point cloud at ~9.6 Hz over USB2.
- 🧭 **Autonomous navigation** — Nav2 tuned for skid-steer, commanding through a `twist_mux` priority chain (joystick 100 > web 90 > nav 10), with battery locks that veto navigation below 10.0 V.
- 🌙 **Night-patrol dashboard** — video with detection boxes, lidar radar, artificial horizon, compass, battery/temp telemetry, touch joystick + Gamepad API, e-stop and event log. Plain rosbridge + JS, served from the Pi; remote access via Tailscale. Foxglove bridge on :8765.
- 🔋 **Power management learned the hard way** — INA219 monitoring, warn/critical thresholds, a host-side shutdown watchdog service, and a motor watchdog (1 s failsafe in firmware).

## Architecture

```
┌──────────────────────── Raspberry Pi 5 (Docker, network+ipc: host) ───────────────────────┐
│                                                                                            │
│  base ──── /dev/i2c-1 ── motors (ESP32) · IMU · INA219 battery · lights · twist_mux · URDF │
│  lidar ─── /dev/ttyUSB0 ─ LD06 → /scan (506 pts/rev @ 10 Hz)                               │
│  oak ───── USB2 ───────── OAK-D Lite → RGB · depth · YOLO detections · /oak/points         │
│  slam ──── (profile) ──── rf2o laser odometry → EKF → slam_toolbox → /map                  │
│  nav ───── (profile) ──── Nav2 (skid-steer params) → nav_vel                               │
│  web ───── :8000 ──────── dashboard · rosbridge :9090 · video :8080 · foxglove :8765       │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
        firmware: Arduino/waver_slate_v2 (motor protocol + lights + 1 s failsafe)
```

Why `ipc: host` everywhere: FastDDS moves data between processes on the same host through shared memory — without a shared `/dev/shm`, containers discover each other but no data flows. That one line cost a night of debugging.

## Run it

```bash
git clone https://github.com/andresjjn/waver.git && cd waver

docker compose up -d                       # base + lidar + oak + web
docker compose --profile slam up -d slam   # start mapping
docker compose --profile nav up -d nav     # autonomous navigation (needs slam)

# dashboard:  http://<pi-ip>:8000
# Foxglove:   https://app.foxglove.dev → ws://<pi-ip>:8765
# save a map: tools/save_map.sh
```

## Hardware

| Part | Role | Notes |
|---|---|---|
| Waveshare Wave Rover | chassis + ESP32 driver board | skid-steer, no encoders |
| Raspberry Pi 5 | brain | runs the whole Docker stack |
| LD06-class 2D lidar | /scan + odometry source | 506 pts/rev @ 10 Hz |
| OAK-D Lite | spatial AI camera | YOLO on-device, depth, USB2 |
| INA219 | battery monitoring | warn 10.5 V / critical 10.0 V |

## Repo map

| Path | What |
|---|---|
| `docker-compose.yml` | the whole robot, service per container, slam/nav as profiles |
| `wave_robot_tele_server_ros2/` | `waver_base` (cmd_vel→I2C motors, IMU, battery, lights, mode manager, twist_mux) + `waver_description` (URDF) |
| `ROS2_Docker_slam/` | `waver_slam`: rf2o + EKF + slam_toolbox |
| `ROS2_Docker_nav2/` | Nav2 launch + skid-steer params |
| `ROS2_Docker_oak_camera/` | depthai-ros config (YOLO, point cloud, subpixel notes in `oak.yaml`) |
| `ROS2_Docker_web/` | night-patrol dashboard + rosbridge/video/foxglove bridges |
| `ROS2_Docker_lidar_stl06/` | lidar container (see credits) |
| `Arduino/waver_slate*/` | custom ESP32 firmware: motor protocol, lights register, failsafe |
| `tools/` | Mac joystick teleop, map saving, Pi battery-shutdown watchdog |
| `docs/` | physical-session checklist, Waveshare protocol reference |
| `PLAN.md` | the engineering log (Spanish): every phase, bug and calibration, dated |

## Honest numbers & limitations

- `v_max` calibrated at **0.8 m/s** (measured: 2.4 m in a 3 s pulse at PWM 255); Nav2 capped at 0.5 m/s.
- Skid-steer on smooth floors slips; laser odometry absorbs most of it, rough rotation estimates remain the weak spot.
- OAK-D Lite is USB2 on this Pi: point cloud tops out around ~9.6 Hz with on-device YOLO.
- Mapping quality depends on furniture density — long featureless hallways are rf2o's enemy.

## Credits

- Lidar container derived from [aldajo92/ROS2_Docker_lidar_stl06](https://github.com/aldajo92/ROS2_Docker_lidar_stl06) (Alejandro Gómez, Robótica Medellín) — modified Dockerfile + custom launch; vendored driver [ldrobotSensorTeam/ldlidar_stl_ros2](https://github.com/ldrobotSensorTeam/ldlidar_stl_ros2) keeps its own license.
- Laser odometry: vendored [MAPIRlab/rf2o_laser_odometry](https://github.com/MAPIRlab/rf2o_laser_odometry) (Univ. of Málaga) — **GPLv3**, license preserved in its folder.
- Chassis, driver board and stock firmware: [Waveshare Wave Rover](https://www.waveshare.com/wiki/WAVE_ROVER) (protocol notes in `docs/WAVESHARE_WIKI_REFERENCE.md`).
- Related standalone repos: [waver_motor_driver](https://github.com/andresjjn/waver_motor_driver) · [wave_rover_joystick_controller](https://github.com/andresjjn/wave_rover_joystick_controller).

## License

MIT © Andrés Felipe Jején Tabares — except vendored third-party components, which keep their upstream licenses.
