# 6주차 센서 실습 실행 안내

`week06.pdf`의 실습 6.1~6.10(뷰어 기준 17~26쪽, 슬라이드 번호 16~25)에 해당합니다.
뷰어 기준 16쪽은 실습 섹션 표지입니다. 이후 과제와 다음 주차 차량 제어는 포함하지 않습니다.

## 1. 패키지 준비 및 빌드

ROS 2와 Gazebo Sim이 설치된 Ubuntu에서 실행합니다. 예시는 ROS 2 Jazzy + Gazebo Harmonic 기준입니다.
`my_sensor_pkg`와 `my_vehicle_gazebo` 두 폴더를 `~/ros2_ws/src/` 아래에 둡니다.
차체와 바퀴는 `my_vehicle_gazebo`에서 가져오므로 두 패키지가 모두 필요합니다.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
rosdep install --from-paths src/my_sensor_pkg src/my_vehicle_gazebo --ignore-src -r -y
colcon build --symlink-install --packages-select my_vehicle_gazebo my_sensor_pkg
source install/setup.bash
ros2 launch my_sensor_pkg sensors_sim.launch.py
```

`rosdep`이 아직 초기화되지 않았다면 먼저 사용 중인 ROS 환경의 rosdep 초기화를 완료합니다.
다른 ROS 배포판을 쓰는 경우 첫 줄의 `jazzy`를 해당 이름으로 바꿉니다.

런치는 Gazebo 트랙, 센서를 포함한 차량 스폰, TF, 가상 시계 브릿지, 센서 브릿지,
멀티스레드 리스너, RViz를 함께 시작합니다. 기존 `spawn_car.launch.py`를 별도로 실행할 필요가 없습니다.
차량은 정지 상태이며, `joint_state_publisher`는 RViz에서 바퀴까지 표시하도록 기본 관절 위치를 발행합니다.

RViz 없이 시작하려면:

```bash
ros2 launch my_sensor_pkg sensors_sim.launch.py rviz:=false
```

## 2. 센서와 RViz 확인

| 센서 | ROS 토픽 | 설정 | 메시지 프레임 |
| --- | --- | --- | --- |
| LiDAR | `/scan` | 10Hz, 360샘플, 0.15~12m | `lidar_link` |
| 카메라 | `/camera/image_raw` | 30Hz, 640×480 RGB, 약 80도 FOV | `camera_optical_frame` |
| IMU | `/imu/data` | 50Hz | `imu_link` |

`config/sensors.rviz`에 Fixed Frame=`base_link`, RobotModel, TF, LaserScan,
Image, IMU 표시와 센서 구독의 Best Effort QoS를 저장했습니다.
IMU 표시는 추가 패키지 `rviz_imu_plugin`이 필요하며 `package.xml`에 의존성으로 선언되어 있습니다.
IMU 표시가 없으면 설치를 확인합니다:

```bash
sudo apt install ros-${ROS_DISTRO}-rviz-imu-plugin
```

이 플러그인은 IMU 자세 축과 가속도 벡터를 표시합니다.
각속도 수치는 아래의 `ros2 topic echo`로 확인할 수 있습니다.
LiDAR는 전방위 최소 유효 거리를 출력하고 1m 미만일 때 경고합니다.
IMU는 Roll/Pitch가 10도를 넘으면 경고하며, 카메라는 30프레임마다 수신 정보를 출력합니다.

## 3. 발행 주기·대역폭 측정 (실습 6.8)

새 터미널마다 환경을 적용한 뒤, 측정 명령은 각각 별도 터미널에서 실행합니다.

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 topic hz /scan
ros2 topic hz /camera/image_raw
ros2 topic bw /camera/image_raw
ros2 topic hz /imu/data
```

목표는 LiDAR 약 10Hz, 카메라 약 30Hz, IMU 약 50Hz입니다.
RGB 픽셀 데이터는 프레임당 921,600바이트, 30fps에서 약 27.65MB/s이며,
실측값에는 메시지 부가 정보, 측정 도구의 단위, PC 성능과 시뮬레이션 속도가 영향을 줍니다.
목표 주파수는 시뮬레이션 시간 기준이며 실시간 계수가 떨어지면 벽시계 기준 측정값도 낮아집니다.

```bash
ros2 topic echo /scan --once --qos-reliability best_effort
ros2 topic echo /imu/data --once --qos-reliability best_effort
```

## 4. QoS 확인 및 불일치 실험 (실습 6.9)

```bash
ros2 topic info /scan --verbose
ros2 topic info /camera/image_raw --verbose
ros2 topic info /imu/data --verbose
```

센서 브릿지의 발행자와 리스너·RViz의 구독자는 `BEST_EFFORT`, `VOLATILE`로 확인합니다.
센서 YAML에는 `qos_profile: SENSOR_DATA`를 명시했습니다.
배포판의 오래된 `ros_gz_bridge`에서 이 설정을 지원하지 않으면 해당 패키지를 업데이트한 뒤
`topic info --verbose`로 실제 적용 여부를 다시 확인합니다.

기존 런치를 Ctrl+C로 종료한 뒤, 리스너만 Reliable로 바꿔서 다시 실행합니다:

```bash
ros2 launch my_sensor_pkg sensors_sim.launch.py sensor_reliability:=reliable
```

Best Effort 발행자와 Reliable 리스너 사이에 QoS 불일치가 발생해 리스너의 센서 수신이 중단되어야 합니다.
RViz는 계속 Best Effort이므로 표시를 유지할 수 있습니다.
실험 후에는 종료하고 기본 런치 명령으로 다시 실행합니다.

## 5. 문제 확인 순서 (실습 6.10)

1. Gazebo 센서 데이터부터 확인합니다.

   ```bash
   gz topic -l
   gz topic -e -t /scan
   gz topic -e -t /camera/image_raw
   gz topic -e -t /imu/data
   ```

2. Gazebo 데이터가 있으면 ROS 브릿지와 QoS를 확인합니다.

   ```bash
   ros2 topic info /scan --verbose
   ros2 topic echo /clock --once
   ros2 run tf2_ros tf2_echo base_link lidar_link
   ```

3. ROS 데이터까지 있으면 RViz의 Fixed Frame=`base_link`, 센서 Topic,
   Reliability Policy=`Best Effort`, 디스플레이 Status를 확인합니다.

검은 카메라 화면은 Gazebo 실행 상태, GPU 렌더링 오류, 조명과 렌즈 앞 장애물을 확인합니다.
기본 `sensors_track.sdf`에는 Sun, Sensors(Ogre2), Imu 시스템 플러그인을 포함했습니다.
IMU 프레임은 회전 없는 고정 조인트로 X 전방, Y 좌측, Z 상향을 유지합니다.
카메라 영상에는 별도의 ROS optical frame을 사용합니다.

`world:=...`로 다른 월드를 사용할 때는 해당 월드에도 Sensors·Imu 플러그인이 있어야 합니다.
월드 이름이 `car_track_world`와 다르면 `sensor_bridge.yaml`의 Gazebo clock 경로도 수정한
파일을 `bridge_config:=...`로 지정합니다.

## 참고 자료와 실행 확인 범위

- [Gazebo Harmonic 센서 시스템](https://gazebosim.org/docs/harmonic/sensors/)
- [ros_gz_bridge YAML·QoS 설정](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [RViz IMU 플러그인](https://github.com/CCNYRoboticsLab/imu_tools/tree/jazzy/rviz_imu_plugin)

이 Windows 작업 환경에서는 ROS 2/Gazebo 실행 및 토픽 수신을 검증하지 않았습니다.
실제 빌드, 화면 표시, 주파수와 QoS 확인은 위 명령으로 실습 환경에서 수행합니다.
