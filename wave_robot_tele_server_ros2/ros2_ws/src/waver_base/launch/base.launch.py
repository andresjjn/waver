"""Levanta la capa base completa del Wave Rover.

  motor_controller (C++ existente, I2C reg 0x00)
  cmd_vel_to_motors -> /motor_commands
  twist_mux (joy_vel/web_vel/nav_vel -> /cmd_vel)
  imu_node, battery_node, lights_node, mode_manager
  joy + teleop_twist_joy opcionales (use_joy:=true si hay mando en la Pi)
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('waver_base')
    twist_mux_config = os.path.join(pkg_share, 'config', 'twist_mux.yaml')

    use_joy = LaunchConfiguration('use_joy')

    description_launch = os.path.join(
        get_package_share_directory('waver_description'),
        'launch', 'description.launch.py')

    return LaunchDescription([
        DeclareLaunchArgument('use_joy', default_value='false',
                              description='Mando fisico conectado a la Pi'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(description_launch)),

        Node(package='waver_motor_driver', executable='motor_controller_node',
             name='motor_controller', output='screen'),

        Node(package='waver_base', executable='cmd_vel_to_motors',
             name='cmd_vel_to_motors', output='screen',
             # calibrado 2026-07-04: 2.4 m en pulso de 3 s a PWM 255
             parameters=[{'max_linear_speed': 0.8}]),

        Node(package='twist_mux', executable='twist_mux', name='twist_mux',
             parameters=[twist_mux_config],
             remappings=[('cmd_vel_out', 'cmd_vel')], output='screen'),

        Node(package='waver_base', executable='imu_node',
             name='imu_node', output='screen'),

        Node(package='waver_base', executable='display_node',
             name='display_node', output='screen',
             parameters=[{'rate_hz': 2.0}]),

        # 5 Hz para que OLED/dashboard respondan agiles; el debounce del
        # manager se escala a 25 lecturas para seguir siendo ~5 s sostenidos
        Node(package='waver_base', executable='battery_node',
             name='battery_node', output='screen',
             parameters=[{'rate_hz': 5.0}]),

        Node(package='waver_base', executable='battery_manager',
             name='battery_manager', output='screen',
             parameters=[{'debounce_n': 25}]),

        Node(package='waver_base', executable='lights_node',
             name='lights_node', output='screen'),

        Node(package='waver_base', executable='mode_manager',
             name='mode_manager', output='screen'),

        Node(package='joy', executable='joy_node', name='joy_node',
             condition=IfCondition(use_joy), output='screen'),

        Node(package='teleop_twist_joy', executable='teleop_node',
             name='teleop_twist_joy', condition=IfCondition(use_joy),
             parameters=[{
                 'axis_linear.x': 1,
                 'scale_linear.x': 0.8,
                 'axis_angular.yaw': 0,
                 'scale_angular.yaw': 3.0,
                 'enable_button': 4,       # LB como hombre-muerto
                 'require_enable_button': True,
             }],
             remappings=[('cmd_vel', 'joy_vel')], output='screen'),
    ])
