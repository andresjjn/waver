from setuptools import setup
import os
from glob import glob

package_name = 'waver_base'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools', 'smbus2'],
    zip_safe=True,
    maintainer='Andres',
    maintainer_email='andresjtdev@gmail.com',
    description='Capa base del Wave Rover',
    license='MIT',
    entry_points={
        'console_scripts': [
            'cmd_vel_to_motors = waver_base.cmd_vel_to_motors:main',
            'imu_node = waver_base.imu_node:main',
            'battery_node = waver_base.battery_node:main',
            'battery_manager = waver_base.battery_manager:main',
            'lights_node = waver_base.lights_node:main',
            'display_node = waver_base.display_node:main',
            'mode_manager = waver_base.mode_manager:main',
        ],
    },
)
