#!/usr/bin/env bash
# Guarda el mapa actual de slam_toolbox en la Pi: ./tools/save_map.sh [nombre]
# (por defecto "casa"). Genera /maps/<nombre>.posegraph + .data en ~/Waver/maps.
set -euo pipefail
NAME="${1:-casa}"
ssh -i ~/.ssh/id_rpi ros@192.168.1.16 "docker exec waver_slam bash -c \
  'source /opt/ros/humble/setup.bash && source /ros2_ws/install/setup.bash && \
   ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph \
   \"{filename: \\\"/maps/${NAME}\\\"}\"'"
echo "Mapa guardado en ~/Waver/maps/${NAME} (en la Pi)"
