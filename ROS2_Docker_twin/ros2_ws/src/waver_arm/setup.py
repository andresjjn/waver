import os
from glob import glob

from setuptools import setup

package_name = 'waver_arm'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Andres Jejen',
    maintainer_email='andresjt93@gmail.com',
    description='Controlador PCA9685 (mock/real) de brazos + torso del CRAB',
    license='MIT',
    entry_points={
        'console_scripts': [
            'arm_controller = waver_arm.arm_controller_node:main',
        ],
    },
)
