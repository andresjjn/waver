"""Nav2 del Wave Rover — nodos nucleo con lifecycle manager.

Lanzado a mano (sin nav2_bringup) para controlar los remaps:
  - TODOS los controladores publican cmd_vel -> remapeado a /nav_vel
    (rama de prioridad 10 del twist_mux: joy y web siempre pueden pisarla,
    y el lock_nav del mode_manager/battery_manager la veta).

Requiere: base (URDF, twist_mux), lidar (/scan) y slam (map->odom + /map).
"""
from launch import LaunchDescription
from launch_ros.actions import Node

PARAMS = '/nav2_params.yaml'
CMD_VEL_REMAP = [('cmd_vel', 'nav_vel')]

NODES = [
    ('nav2_controller', 'controller_server', CMD_VEL_REMAP),
    ('nav2_planner', 'planner_server', []),
    ('nav2_behaviors', 'behavior_server', CMD_VEL_REMAP),
    ('nav2_bt_navigator', 'bt_navigator', []),
    ('nav2_waypoint_follower', 'waypoint_follower', []),
]


def generate_launch_description():
    nodes = [
        Node(package=pkg, executable=exe, name=exe, output='screen',
             parameters=[PARAMS], remappings=remaps)
        for pkg, exe, remaps in NODES
    ]
    nodes.append(Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_navigation', output='screen',
        parameters=[{
            'autostart': True,
            'node_names': [exe for _, exe, _ in NODES],
        }]))
    return LaunchDescription(nodes)
