FROM ros:humble-ros-base-jammy
ENV ROS_DISTRO=humble

# slam_toolbox: SLAM 2D con el lidar LD06
# robot_localization: EKF que fusiona rf2o + IMU -> odom->base_link estable
# rf2o_laser_odometry NO esta en apt para humble: va vendorizado en
# ros2_ws/src y se compila con colcon al arrancar el contenedor.
RUN apt update && apt install -y \
    ros-${ROS_DISTRO}-slam-toolbox \
    ros-${ROS_DISTRO}-robot-localization \
    libeigen3-dev \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

ENTRYPOINT [ "/ros_entrypoint.sh" ]
