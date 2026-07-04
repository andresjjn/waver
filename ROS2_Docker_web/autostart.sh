#!/bin/bash

source /opt/ros/$ROS_DISTRO/setup.bash

# rosbridge: WebSocket ROS <-> navegador (puerto 9090)
ros2 launch rosbridge_server rosbridge_websocket_launch.xml &

# web_video_server: MJPEG de cualquier topic de imagen (puerto 8080)
ros2 run web_video_server web_video_server &

# Dashboard estatico (puerto 8000)
cd /www && python3 -m http.server 8000 &

exec "$@"
