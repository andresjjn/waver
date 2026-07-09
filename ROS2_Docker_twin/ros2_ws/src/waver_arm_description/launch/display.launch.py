"""Visualiza el gemelo digital en RViz con sliders para cada joint.

Uso:
  ros2 launch waver_arm_description display.launch.py                     # CRAB completo
  ros2 launch waver_arm_description display.launch.py model:=arm_standalone.urdf.xacro
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('waver_arm_description')

    model_arg = DeclareLaunchArgument(
        'model',
        default_value='waver_crab.urdf.xacro',
        description='Archivo xacro dentro de urdf/ a visualizar',
    )
    rviz_arg = DeclareLaunchArgument(
        'rviz', default_value='true', description='Abrir RViz2'
    )

    robot_description = ParameterValue(
        Command([
            'xacro ',
            PathJoinSubstitution([pkg_share, 'urdf', LaunchConfiguration('model')]),
        ]),
        value_type=str,
    )

    return LaunchDescription([
        model_arg,
        rviz_arg,
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
        # Sliders para mover cada joint a mano (los mimic se mueven solos)
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(pkg_share, 'rviz', 'twin.rviz')],
            condition=None,
        ),
    ])
