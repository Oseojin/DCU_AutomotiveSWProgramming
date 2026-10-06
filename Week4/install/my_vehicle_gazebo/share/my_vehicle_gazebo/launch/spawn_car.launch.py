#!/usr/bin/env python3
"""
==================================================================
스크립트: spawn_car.launch.py
설명: Gazebo Sim 물리 시뮬레이션 환경을 실행하고, 3주차에 제작한
      4륜 차량 URDF 모델을 가상 월드에 스폰(Spawn)하며,
      ros_gz_bridge와 robot_state_publisher를 연동하는 통합 런치 파일입니다.
구동 단계:
  1. code04/worlds/car_track.sdf 월드 파일 위치 계산
  2. code03/urdf/vehicle.urdf.xacro 로봇 모델을 Xacro 엔진으로 파싱
  3. gz sim 명령 프로세스 기동 (물리 시뮬레이터 및 3D GUI 팝업)
  4. ros_gz_sim의 create 노드를 통해 월드에 로봇 엔티티 동적 생성
  5. ros_gz_bridge 노드를 통해 bridge.yaml에 정의된 양방향 토픽 중계
  6. robot_state_publisher 노드를 통해 시뮬레이션 시간(use_sim_time: True) 동기화
==================================================================
"""

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    # -------------------------------------------------------------
    # 1. 파일 및 디렉터리 경로 계산
    # -------------------------------------------------------------
    # 현재 launch 파일 디렉터리 (code04/launch)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    course_root = os.path.dirname(current_dir)
    
    print(course_root)
    # 대상 파일들의 절대 경로
    world_file = os.path.join(course_root, 'worlds', 'car_track.sdf')
    bridge_yaml = os.path.join(course_root, 'config', 'bridge.yaml')
    xacro_file = os.path.join(course_root, 'urdf', 'vehicle.urdf.xacro')

    # -------------------------------------------------------------
    # 2. Xacro 전처리 및 URDF XML 문자열 추출
    # -------------------------------------------------------------
    # vehicle.urdf.xacro가 존재하지 않을 경우를 대비한 안전 점검
    if os.path.exists(xacro_file):
        doc = xacro.process_file(xacro_file)
        robot_description_content = doc.toxml()
    else:
        robot_description_content = ""
        print(f"[경고] Xacro 파일을 찾을 수 없습니다: {xacro_file}")

    # -------------------------------------------------------------
    # 3. Gazebo Sim 프로세스 기동 (gz sim -r world_file)
    # -r 플래그는 시뮬레이션을 일시정지 상태가 아니라 즉시 실행(Run) 상태로 시작시킵니다.
    # -------------------------------------------------------------
    gz_sim_process = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen'
    )

    # -------------------------------------------------------------
    # 4. ros_gz_sim의 'create' 노드를 통한 모델 동적 스폰
    # Gazebo 내부의 /world/car_track_world/create 서비스를 호출하여
    # 월드 상의 지정된 좌표 (x=0, y=-4, z=0.15)에 차량을 생성합니다.
    # -------------------------------------------------------------
    spawn_car_node = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_car',
        output='screen',
        arguments=[
            '-name', 'auto_vehicle',
            '-string', robot_description_content,
            '-x', '0.0',
            '-y', '-4.0',
            '-z', '0.15'
        ]
    )

    # -------------------------------------------------------------
    # 5. ros_gz_bridge 노드 (이기종 토픽 중계 브릿지)
    # bridge.yaml 설정에 따라 /clock, /cmd_vel, /odom 등을 양방향 중계합니다.
    # -------------------------------------------------------------
    gz_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        parameters=[{
            'config_file': bridge_yaml
        }]
    )

    # -------------------------------------------------------------
    # 6. robot_state_publisher 노드
    # 시뮬레이션 환경이므로 use_sim_time: True를 지정하여
    # /clock 토픽의 가상 시간을 기준으로 TF 변환을 계산합니다.
    # -------------------------------------------------------------
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True
        }]
    )

    return LaunchDescription([
        gz_sim_process,
        spawn_car_node,
        gz_bridge_node,
        robot_state_publisher_node
    ])
