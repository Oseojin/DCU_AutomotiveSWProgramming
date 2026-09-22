#!/usr/bin/env python3
"""
==================================================================
스크립트: display.launch.py
설명: 3주차 차량 로봇 모델(URDF/Xacro)을 RViz2에서 시각화하기 위한
      ROS 2 런치 파일입니다.
동작 흐름:
  1. vehicle.urdf.xacro 파일을 읽어 Xacro 전처리기로 파싱
  2. robot_state_publisher 노드에 모델 XML 문자열 주입 및 실행
  3. joint_state_publisher_gui 노드를 실행하여 슬라이더 GUI 제공
  4. RViz2 노드를 실행하여 3D 로봇 모델 및 TF 좌표축 렌더링
사용법:
  - 직접 실행: ros2 launch code03/launch/display.launch.py
  - 패키지 빌드 후 실행: ros2 launch my_vehicle_description display.launch.py
==================================================================
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# xacro 모듈을 통해 파이썬 코드 내에서 직접 Xacro를 파싱합니다.
import xacro


def generate_launch_description():
    # 1. 파일 경로 계산
    # 본 launch 파일의 위치(code03/launch/)를 기준으로 code03/urdf/vehicle.urdf.xacro를 찾습니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pkg_dir = os.path.dirname(current_dir)
    xacro_path = os.path.join(pkg_dir, 'urdf', 'vehicle.urdf.xacro')

    # 2. Xacro 전처리 엔진 구동
    # Xacro 매크로와 변수, 수식을 모두 해석하여 순수 URDF XML 텍스트로 변환합니다.
    doc = xacro.process_file(xacro_path)
    robot_description_raw = doc.toxml()

    # 3. robot_state_publisher 노드 정의
    # 로봇의 기구학 트리를 메모리에 로드하고, 관절 각도(/joint_states)를 구독하여
    # 3차원 위치 변환 정보(/tf, /tf_static)를 브로드캐스팅합니다.
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_raw,
            'use_sim_time': False
        }]
    )

    # 4. joint_state_publisher_gui 노드 정의
    # 가동 관절(revolute, continuous)들의 위치를 마우스 슬라이더로 조작할 수 있는
    # 그래픽 유저 인터페이스(GUI)를 실행하고, 조작된 각도를 /joint_states로 발행합니다.
    node_joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # 5. RViz2 노드 정의
    # 3D 렌더링 화면을 띄워 로봇의 외형과 좌표축 움직임을 시각적으로 확인합니다.
    node_rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    # 런치 시스템에 노드들을 등록하여 반환
    return LaunchDescription([
        node_robot_state_publisher,
        node_joint_state_publisher_gui,
        node_rviz2
    ])
