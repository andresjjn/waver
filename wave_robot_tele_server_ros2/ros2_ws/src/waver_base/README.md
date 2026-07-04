# waver_base

Capa base del Wave Rover sobre el firmware `waver_slate_v2`.

## Nodos

| Nodo | Suscribe | Publica | Nota |
|------|----------|---------|------|
| `cmd_vel_to_motors` | `/cmd_vel` (Twist) | `/motor_commands` (Int16MultiArray) | Watchdog 0.5 s, reenvia a 20 Hz |
| `imu_node` | — | `/imu/data_raw`, `/imu/mag`, `/imu/temperature`, `/imu/rpy` | QMI8658 (0x6B) + AK09918 (0x0C) directo por `/dev/i2c-1` |
| `battery_node` | — | `/battery` (BatteryState) | INA219 (0x42), shunt 0.01 Ω |
| `lights_node` | `/lights` [io4, io5] 0-255 | — | Escribe reg 0x01 del ESP32 (firmware v2) |
| `mode_manager` | `/joy`, `/set_mode`, `/set_estop` | `/robot_mode`, `/lock_nav`, `/e_stop` | Botón A = TELEOP↔AUTO, B = e-stop |

## Flujo de comandos

```
joy_vel (100) ─┐
web_vel (90) ──┤ twist_mux ──► /cmd_vel ──► cmd_vel_to_motors ──► /motor_commands ──► motor_controller ──► I2C 0x11
nav_vel (10) ──┘   ▲ locks: /lock_nav (50), /e_stop (255)
```

## Uso

```bash
ros2 launch waver_base base.launch.py            # robot completo
ros2 launch waver_base base.launch.py use_joy:=true   # con mando en la Pi

# pruebas rapidas
ros2 topic pub -r 10 /joy_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}}"
ros2 topic pub --once /lights std_msgs/msg/Int16MultiArray "{data: [255, 0]}"
ros2 topic echo /battery
```

## Calibración pendiente (parámetros de `cmd_vel_to_motors`)

- `max_linear_speed`: mide la velocidad real a PWM 255 (cronometra 2 m).
- `min_pwm`: sube desde 0 hasta que las ruedas empiecen a girar.
- `wheel_separation`: distancia entre centros de ruedas (regla).

Requiere `smbus2` (lo instala el Dockerfile del tele server) y acceso a
`/dev/i2c-1` (el `run.sh` ya lo pasa al contenedor).
