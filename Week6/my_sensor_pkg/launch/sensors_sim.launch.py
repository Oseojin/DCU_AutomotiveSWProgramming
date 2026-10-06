#!/usr/bin/env python3
"""Launch the Week 6 sensor vehicle, Gazebo, bridges, listener and RViz."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    """Build the sensor simulation using installed package resources."""
    sensor_share = get_package_share_directory('my_sensor_pkg')
    gazebo_share = get_package_share_directory('ros_gz_sim')
    robot_description = xacro.process_file(
        os.path.join(sensor_share, 'urdf', 'sensor_vehicle.urdf.xacro')
    ).toxml()
    sim_time = {'use_sim_time': True}

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(sensor_share, 'worlds', 'sensors_track.sdf'),
            description='World containing Sensors and Imu system plugins',
        ),
        DeclareLaunchArgument(
            'bridge_config',
            default_value=os.path.join(sensor_share, 'config', 'sensor_bridge.yaml'),
        ),
        DeclareLaunchArgument(
            'rviz', default_value='true', description='Start RViz sensor dashboard',
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(sensor_share, 'config', 'sensors.rviz'),
        ),
        DeclareLaunchArgument(
            'sensor_reliability', default_value='best_effort',
            choices=['best_effort', 'reliable'],
            description='Use reliable only for the QoS mismatch experiment',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_share, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={
                'gz_args': ['-r "', LaunchConfiguration('world'), '"'],
                'on_exit_shutdown': 'true',
            }.items(),
        ),
        Node(
            package='robot_state_publisher', executable='robot_state_publisher',
            parameters=[sim_time, {'robot_description': robot_description}],
            output='screen',
        ),
        # Publish resting wheel joint positions for the stationary sensor lab.
        Node(
            package='joint_state_publisher', executable='joint_state_publisher',
            parameters=[sim_time, {'robot_description': robot_description}],
        ),
        Node(
            package='ros_gz_sim', executable='create', name='spawn_sensor_vehicle',
            arguments=[
                '-name', 'auto_vehicle', '-topic', '/robot_description',
                '-x', '0.0', '-y', '-4.0', '-z', '0.15',
            ],
            parameters=[sim_time], output='screen',
        ),
        Node(
            package='ros_gz_bridge', executable='parameter_bridge',
            name='sensor_parameter_bridge',
            parameters=[sim_time, {'config_file': LaunchConfiguration('bridge_config')}],
            output='screen',
        ),
        Node(
            package='my_sensor_pkg', executable='sensor_listener',
            name='sensor_listener_node',
            parameters=[sim_time, {
                'sensor_reliability': LaunchConfiguration('sensor_reliability'),
            }],
            output='screen',
        ),
        Node(
            package='my_sensor_pkg', executable='emergency_stop_node.py',
            name='emergency_stop_node', parameters=[sim_time],
            output='screen', emulate_tty=True,
            additional_env={'RCUTILS_COLORIZED_OUTPUT': '1'},
        ),
        Node(
            package='rviz2', executable='rviz2',
            arguments=['-d', LaunchConfiguration('rviz_config')],
            parameters=[sim_time], condition=IfCondition(LaunchConfiguration('rviz')),
            output='screen',
        ),
    ])
