# ROS2_Docker_web — Dashboard "Vigilante Nocturno"

Centro de mando web del Wave Rover servido desde la Raspberry Pi. Funciona en
cualquier navegador: celular, tablet, ROG Ally (con mando), PC.

```
navegador ──ws 9090──► rosbridge ──► ROS 2
     │───http 8080──► web_video_server (MJPEG de /oak/...)
     └───http 8000──► dashboard estático (/www)
```

## Uso

```bash
./scripts/build.sh
./scripts/run.sh
# abrir http://<IP-de-la-Pi>:8000
```

## Funciones

- **Vídeo en vivo** conmutable: RGB / profundidad / detecciones + snapshot.
- **Horizonte artificial** (roll/pitch) y **brújula** (magnetómetro AK09918), de `/imu/rpy`.
- **Batería** (INA219): voltaje, corriente, %, estado de carga, alerta ≤20%.
- **Temperatura** de la IMU y contador de detecciones YOLO con log de eventos.
- **Joystick virtual** táctil (esquina del vídeo) → publica `/web_vel`.
- **Gamepad API**: sticks de la ROG Ally / mando Xbox sin instalar nada.
  Botón A = modo autónomo, botón B = e-stop.
- **Focos**: sliders LED (IO4) e IR (IO5) → `/lights` (requiere firmware v2).
- Al soltar el mando/joystick, el robot se detiene solo (timeout del twist_mux
  + watchdog de `cmd_vel_to_motors` + failsafe del firmware: triple seguro).

## Acceso remoto seguro

**No abrir estos puertos a internet** (control físico de un robot, sin
autenticación). Para acceso desde fuera de casa instalar
[Tailscale](https://tailscale.com) en la Pi y en el celular/ROG:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# luego usar http://<ip-tailscale-de-la-pi>:8000 desde cualquier lugar
```

Pendiente (fase 2.2 del PLAN): notificaciones push, galería de snapshots y
grabación de clips por evento.
