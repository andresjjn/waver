FROM ros:humble-ros-base-jammy
ENV ROS_DISTRO humble

RUN apt update && apt install -y \
    git \
    nano \
    tmux \
    wget \
    curl \
    iputils-ping \
    net-tools \
    libusb-1.0-0 \
    udev \
    python3-pip \
    python3-colcon-common-extensions

# Driver ROS 2 oficial de Luxonis (OAK-D Lite): incluye depthai SDK,
# depthai_ros_driver, depthai_bridge y los modelos NN (yolo, mobilenet)
RUN apt update && apt install -y \
    ros-${ROS_DISTRO}-depthai-ros \
    ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
    ros-${ROS_DISTRO}-image-transport-plugins

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

COPY config/oak.yaml /oak.yaml
COPY autostart.sh /autostart.sh
RUN chmod +x /autostart.sh

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

ENTRYPOINT [ "/ros_entrypoint.sh" ]
