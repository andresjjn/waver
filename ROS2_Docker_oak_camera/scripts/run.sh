#!/bin/bash

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")"; cd ..; pwd)"
source ${PROJECT_ROOT}/config_docker.sh

# La OAK re-enumera su USB al arrancar el pipeline (bootloader -> firmware),
# por eso se monta /dev/bus/usb completo con la regla de cgroup en vez de
# un --device fijo.
docker run -it \
  --name=${DOCKER_CONTAINER_NAME} \
  --network ${ROS_NETWORK} \
  -v /dev/bus/usb:/dev/bus/usb \
  --device-cgroup-rule='c 189:* rmw' \
  --rm \
  ${DOCKER_IMAGE_NAME} /autostart.sh /bin/bash
