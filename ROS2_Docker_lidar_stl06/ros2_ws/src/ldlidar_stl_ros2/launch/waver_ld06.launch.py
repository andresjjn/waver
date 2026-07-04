#!/usr/bin/env python3
"""Launch del LD06/STL-06 para el Wave Rover.

Igual que ld06.launch.py de fabrica pero:
  - frame_id = laser_frame (el TF base_link->laser_frame ya lo publica el
    robot_state_publisher desde el URDF de waver_description; aqui NO se
    publica ningun static_transform para no duplicarlo).
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    ldlidar_node = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='ldlidar',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_LD06'},
            {'topic_name': 'scan'},
            {'frame_id': 'laser_frame'},
            {'port_name': '/dev/ttyUSB0'},
            {'port_baudrate': 230400},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': False},
            {'angle_crop_min': 135.0},
            {'angle_crop_max': 225.0},
        ],
    )

    ld = LaunchDescription()
    ld.add_action(ldlidar_node)
    return ld
