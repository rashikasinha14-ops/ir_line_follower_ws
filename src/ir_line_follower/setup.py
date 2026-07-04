from setuptools import setup
import os
from glob import glob

package_name = 'ir_line_follower'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.py'))),
        (os.path.join('share', package_name, 'worlds'), glob(os.path.join('worlds', '*.sdf'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
        (os.path.join('share', package_name, 'models', 'ir_robot'), glob(os.path.join('models', 'ir_robot', '*'))),
    ],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'ir_sensor_node = ir_line_follower.ir_sensor_node:main',
            'ir_controller_node = ir_line_follower.ir_controller_node:main',
        ],
    },
)
