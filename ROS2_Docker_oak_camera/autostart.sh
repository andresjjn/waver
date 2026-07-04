#!/bin/bash

source /opt/ros/$ROS_DISTRO/setup.bash

# camera.launch.py publica:
#   /oak/rgb/image_raw (+ compressed), /oak/rgb/camera_info
#   /oak/stereo/image_raw (depth alineado a RGB)
#   /oak/nn/spatial_detections (detecciones YOLO con posicion 3D)
#   /oak/points si pointcloud.enable:=true
ros2 launch depthai_ros_driver camera.launch.py \
  params_file:=/oak.yaml \
  pointcloud.enable:=true \
  parent_frame:=oak_link &

exec "$@"
