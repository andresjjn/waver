#!/bin/bash

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")"; cd ..; pwd)"
source ${PROJECT_ROOT}/config_docker.sh

docker run -it \
  --name=${DOCKER_CONTAINER_NAME} \
  --network ${ROS_NETWORK} \
  --rm \
  ${DOCKER_IMAGE_NAME} /autostart.sh /bin/bash
