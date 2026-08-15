# Rescate 2026-08-15 — trabajo local atrapado en clones de terceros

Antes de eliminar los clones de referencia (gitignorados en este monorepo), se rescató aquí el trabajo propio que contenían:

- `Docker_ROS2_Humble_Template-mods.patch` — cambios locales sobre https://github.com/aldajo92/Docker_ROS2_Humble_Template (Dockerfile, config_local.sh, docker_scripts/*). Aplicar con `git apply` sobre un clon fresco.
- `Docker_ROS2_Humble_Template-ros2_ws-waver_motor_driver/` — copia del paquete tal como estaba dentro del template. El código coincide con el repo andresjjn/waver_motor_driver (verificado con diff); se conserva por si el contexto del workspace importa.
- `ROS2_Docker_rpi_camera-mods.patch` — cambios locales sobre https://github.com/aldajo92/ROS2_Docker_rpi_camera (config_docker.sh).
- `ROS2_Docker_rpi_camera-scripts/publish.sh` — script propio no trackeado que vivía en ese clon.

Clones eliminados localmente el 2026-08-15; se re-clonan de las URLs de arriba si hacen falta.
