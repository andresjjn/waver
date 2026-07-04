"""SLAM 2D del Wave Rover: rf2o (odometria laser) -> EKF -> slam_toolbox.

Cadena de TF resultante:
  map -> odom          (slam_toolbox)
  odom -> base_link    (EKF de robot_localization; rf2o NO publica TF)
  base_link -> laser_frame, oak_link, ...  (robot_state_publisher, contenedor base)

Requiere: contenedor base (URDF + IMU) y lidar (/scan) corriendo.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    cfg = os.path.join(get_package_share_directory('waver_slam'), 'config')

    rf2o = Node(
        package='rf2o_laser_odometry',
        executable='rf2o_laser_odometry_node',
        name='rf2o_laser_odometry',
        output='screen',
        parameters=[{
            'laser_scan_topic': '/scan',
            'odom_topic': '/odom_rf2o',
            'publish_tf': False,          # el TF odom->base lo publica el EKF
            'base_frame_id': 'base_footprint',
            'odom_frame_id': 'odom',
            'init_pose_from_topic': '',
            'freq': 10.0,
        }],
    )

    ekf = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[os.path.join(cfg, 'ekf.yaml')],
    )

    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[os.path.join(cfg, 'slam_toolbox.yaml')],
    )

    return LaunchDescription([rf2o, ekf, slam])
