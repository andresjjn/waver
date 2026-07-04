FROM ros:humble-ros-base-jammy
ENV ROS_DISTRO humble

RUN apt update && apt install -y \
    curl \
    nano \
    iputils-ping \
    net-tools \
    python3-pip \
    ros-${ROS_DISTRO}-rosbridge-suite \
    ros-${ROS_DISTRO}-web-video-server \
    ros-${ROS_DISTRO}-foxglove-bridge \
    ros-${ROS_DISTRO}-rmw-cyclonedds-cpp

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

COPY www /www

# roslib vendorizado en build (el dashboard no depende de internet en runtime)
RUN curl -fsSL https://cdn.jsdelivr.net/npm/roslib@1.4.1/build/roslib.min.js \
    -o /www/roslib.min.js

COPY autostart.sh /autostart.sh
RUN chmod +x /autostart.sh

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

ENTRYPOINT [ "/ros_entrypoint.sh" ]
