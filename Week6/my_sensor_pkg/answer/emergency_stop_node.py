#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Best Effort LiDAR subscriber for the Week 6 emergency-stop warning."""

import math
import os

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class EmergencyStopNode(Node):
    """Warn when a valid obstacle is within 1 m in the front +/-20 degrees."""

    def __init__(self):
        super().__init__('emergency_stop_node')
        self.front_half_angle = math.radians(20.0)
        self.stop_distance = 1.0
        # SensorDataQoS: BEST_EFFORT, VOLATILE, KEEP_LAST, depth=5.
        self.scan_subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data
        )
        self.get_logger().info(
            '전방 긴급 정지 경고 노드 시작: /scan, Best Effort, 정면 ±20도, 거리 ≤1.0m'
        )

    def scan_callback(self, msg: LaserScan):
        """Check only finite, in-range measurements in the forward sector."""
        closest_distance = math.inf

        for index, distance in enumerate(msg.ranges):
            # LaserScan's forward direction is 0 rad, not the middle array index.
            angle = msg.angle_min + index * msg.angle_increment
            if not abs(angle) <= self.front_half_angle:
                continue
            # Ignore NaN, infinity, zero and measurements outside sensor limits.
            if not math.isfinite(distance) or distance <= 0.0:
                continue
            if not msg.range_min <= distance <= msg.range_max:
                continue
            if distance < closest_distance:
                closest_distance = distance

        if closest_distance <= self.stop_distance:
            # Color the message explicitly, independent of ROS severity colors.
            self.get_logger().error(
                '\033[31m[EMERGENCY_STOP] 전방 장애물 감지!\033[0m'
            )


def main(args=None):
    """Enable colored logs and run the emergency-stop warning subscriber."""
    os.environ.setdefault('RCUTILS_COLORIZED_OUTPUT', '1')
    rclpy.init(args=args)
    node = EmergencyStopNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
