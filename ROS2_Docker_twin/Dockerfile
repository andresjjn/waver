# Gemelo digital WAVER CRAB — imagen de validación/desarrollo (F1)
# Ligera (ros-base, sin GUI): compila el workspace y corre los smoke tests.
# Para RViz/Gazebo con ventana se usa ROS2_Docker_UI (osrf desktop).
FROM ros:humble-ros-base-jammy

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-tf2-ros \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ros2_ws
