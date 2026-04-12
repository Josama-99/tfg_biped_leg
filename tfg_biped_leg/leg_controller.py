"""Leg controller node for ROS2 integration."""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState

from .odrive_driver import ODriveDriver
from .leg_kinematics import LegKinematics
from .trajectory_generator import TrajectoryGenerator


class LegController(Node):
    """High-level controller for 3-DOF leg."""
    
    def __init__(self):
        super().__init__('leg_controller')
        
        self.declare_parameter('odrive_device', '/dev/ttyACM0')
        self.declare_parameter('upper_leg_length', 0.3)
        self.declare_parameter('lower_leg_length', 0.3)
        self.declare_parameter('control_rate', 100.0)
        
        device = self.get_parameter('odrive_device').value
        upper_len = self.get_parameter('upper_leg_length').value
        lower_len = self.get_parameter('lower_leg_length').value
        rate = self.get_parameter('control_rate').value
        
        self.odrive = ODriveDriver()
        self.kinematics = LegKinematics(upper_leg_length=upper_len, 
                                        lower_leg_length=lower_len)
        self.trajectory = TrajectoryGenerator(self.kinematics)
        
        self.connected = self.odrive.connect(device)
        if self.connected:
            self.odrive.set_closed_loop_control(0)
            self.odrive.set_closed_loop_control(1)
            self.odrive.set_closed_loop_control(2)
        
        self.joint_pub = self.create_publisher(Float64MultiArray, 'joint_commands', 10)
        self.joint_states_pub = self.create_publisher(JointState, 'joint_states', 10)
        
        self.target_sub = self.create_subscription(
            Pose, 'target_pose', self.target_callback, 10)
        
        self.timer = self.create_timer(1.0/rate, self.control_loop)
        
        self.current_angles = [0.0, 0.0, 0.0]
        self.target_angles = [0.0, 0.0, 0.0]
        
        self.get_logger().info('Leg Controller initialized')
    
    def target_callback(self, msg: Pose):
        """Handle incoming target pose.
        
        Args:
            msg: Target position in Cartesian space
        """
        try:
            angles = self.kinematics.inverse_kinematics(
                msg.position.x, msg.position.y, msg.position.z)
            
            if self.kinematics.joint_limits_check(*angles):
                self.target_angles = list(angles)
                self.get_logger().debug(f'Target angles: {angles}')
            else:
                self.get_logger().warn('Target outside joint limits')
                
        except Exception as e:
            self.get_logger().error(f'IK error: {str(e)}')
    
    def control_loop(self):
        """Main control loop."""
        if not self.connected:
            return
        
        for i, angle in enumerate(self.target_angles):
            self.odrive.set_position(i, angle)
            self.current_angles[i] = self.odrive.get_position(i)
        
        self.publish_joint_states()
    
    def publish_joint_states(self):
        """Publish current joint states."""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['hip', 'knee', 'ankle']
        msg.position = self.current_angles
        msg.velocity = [0.0, 0.0, 0.0]
        msg.effort = [0.0, 0.0, 0.0]
        self.joint_states_pub.publish(msg)
    
    def execute_trajectory(self, trajectory_points):
        """Execute a list of joint angle targets.
        
        Args:
            trajectory_points: List of (hip, knee, ankle) angle tuples
        """
        for angles in trajectory_points:
            self.target_angles = list(angles)
            rclpy.spin_once(self, timeout_sec=0.01)
    
    def shutdown(self):
        """Clean shutdown."""
        if self.connected:
            self.odrive.set_idle_state(0)
            self.odrive.set_idle_state(1)
            self.odrive.set_idle_state(2)
        self.get_logger().info('Leg Controller shutdown complete')


def main(args=None):
    rclpy.init(args=args)
    controller = LegController()
    
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.shutdown()
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
