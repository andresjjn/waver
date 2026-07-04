# ROS2_Docker_oak_camera

OAK-D Lite (Luxonis) en ROS 2 Humble para el Wave Rover, con `depthai-ros`.
La red neuronal (YOLO espacial) corre **dentro de la cámara** (Myriad X); la
Pi solo recibe imágenes y detecciones con posición 3D.

## Instalación (una sola vez, en la Raspberry Pi)

```bash
sudo cp udev/80-movidius.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# Conectar la OAK a un puerto USB3 (azul) de la Pi 5
```

⚠️ **Alimentación**: la OAK-D Lite consume hasta ~4.5 W por USB. Con la Pi 5
alimentada del UPS del rover, vigilar caídas de voltaje (`vcgencmd get_throttled`,
`0x0` = ok). Si hay brownouts, usar hub USB3 alimentado.

## Uso

```bash
./scripts/build.sh
./scripts/run.sh
```

## Topics publicados

| Topic | Tipo | Uso |
|-------|------|-----|
| `/oak/rgb/image_raw` (+`/compressed`) | Image | Vídeo del dashboard |
| `/oak/rgb/camera_info` | CameraInfo | Calibración |
| `/oak/stereo/image_raw` | Image (depth, alineado a RGB) | RTAB-Map / obstáculos |
| `/oak/points` | PointCloud2 | Nube de puntos |
| `/oak/nn/spatial_detections` | SpatialDetectionArray | Objetos con XYZ |

## Visión nocturna

Las cámaras **mono** (las del par estéreo, que generan la profundidad) son
sensibles a infrarrojo: con focos IR en IO4/IO5 (`/lights`), la profundidad y
la detección de obstáculos funcionan a oscuras. El sensor RGB necesita luz
blanca para ver a color.

## Ajustes

Editar `config/oak.yaml` (resoluciones, FPS, modelo NN) y reconstruir. Para
cambiar el modelo YOLO: `nn.i_nn_config_path` (ver docs de depthai_ros_driver).
