#!/usr/bin/env python3
"""Basic leg testing script."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import time
import sys


class LegTester(Node):
    """Test node for leg movement."""
    
    def __init__(self):
        super().__init__('leg_tester')
        
        self.publisher = self.create_publisher(
            Float64MultiArray, '/leg_controller/joint_commands', 10)
        
        self.get_logger().info('Leg Tester initialized')
    
    def test_single_joint(self, joint_num, angle):
        """Test a single joint."""
        msg = Float64MultiArray()
        msg.data = [0.0, 0.0, 0.0]
        msg.data[joint_num] = angle
        self.publisher.publish(msg)
        self.get_logger().info(f'Joint {joint_num}: {angle} rad')
    
    def test_home_position(self):
        """Move all joints to home position."""
        msg = Float64MultiArray()
        msg.data = [0.0, 0.0, 0.0]
        self.publisher.publish(msg)
        self.get_logger().info('Moving to home position')
    
    def test_sweep(self, joint_num, min_angle, max_angle, steps=10):
        """Sweep a joint through a range."""
        for i in range(steps + 1):
            angle = min_angle + (max_angle - min_angle) * i / steps
            self.test_single_joint(joint_num, angle)
            time.sleep(0.5)


def main(args=None):
    rclpy.init(args=args)
    tester = LegTester()
    
    try:
        print("\nLeg Test Menu:")
        print("1. Home position")
        print("2. Test hip joint")
        print("3. Test knee joint")
        print("4. Test ankle joint")
        print("5. Test all joints sequentially")
        print("q. Quit")
        
        while rclpy.ok():
            choice = input("\nSelect test: ")
            
            if choice == '1':
                tester.test_home_position()
            elif choice == '2':
                tester.test_sweep(0, -0.5, 0.5)
            elif choice == '3':
                tester.test_sweep(1, -1.0, 0.0)
            elif choice == '4':
                tester.test_sweep(2, -0.3, 0.3)
            elif choice == '5':
                for i in range(3):
                    tester.test_sweep(i, 0.0, 0.5)
                    time.sleep(1)
                    tester.test_home_position()
                    time.sleep(1)
            elif choice == 'q':
                break
            
            rclpy.spin_once(tester, timeout_sec=0.1)
            
    except KeyboardInterrupt:
        pass
    finally:
        tester.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
