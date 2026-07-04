FROM ros:humble-ros-base-jammy
ENV ROS_DISTRO=humble

RUN apt update && apt install -y \
    ros-${ROS_DISTRO}-navigation2 \
    ros-${ROS_DISTRO}-nav2-bringup \
    && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

ENTRYPOINT [ "/ros_entrypoint.sh" ]
