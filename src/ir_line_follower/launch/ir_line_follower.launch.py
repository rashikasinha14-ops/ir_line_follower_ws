import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('ir_line_follower')
    world = os.path.join(pkg, 'worlds', 'ir_words.sdf')
    models = os.path.join(pkg, 'models')
    bridge_cfg = os.path.join(pkg, 'config', 'bridge.yaml')

    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models),
        ExecuteProcess(cmd=['gz', 'sim', '-r', world], output='screen'),
        TimerAction(period=3.0, actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                name='gz_bridge',
                arguments=['--ros-args', '-p', f'config_file:={bridge_cfg}'],
                output='screen',
            ),
        ]),
        TimerAction(period=5.0, actions=[
            Node(
                package='ir_line_follower',
                executable='ir_sensor_node',
                name='ir_sensor_node',
                output='screen',
                parameters=[{'black_threshold': 80, 'patch_size': 12}],
            ),
        ]),
        TimerAction(period=5.5, actions=[
            Node(
                package='ir_line_follower',
                executable='ir_controller_node',
                name='ir_controller_node',
                output='screen',
                parameters=[{
                    'linear_speed': 0.15,
                    'turn_speed_soft': 0.4,
                    'turn_speed_hard': 0.8,
                    'search_speed': 0.5,
                }],
            ),
        ]),
    ])
