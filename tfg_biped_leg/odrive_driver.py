"""ODrive driver for motor control communication."""

import rclpy
from rclpy.node import Node
import odrive
from odrive.enums import *
import time
from typing import Optional, Dict, Any


class ODriveDriver(Node):
    """Driver class for communicating with ODrive motor controllers."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize ODrive driver.
        
        Args:
            config_path: Path to ODrive configuration YAML file
        """
        super().__init__('odrive_driver')
        
        self.odrive: Optional[odrive.ODrive] = None
        self.axis_configs: Dict[int, Dict[str, Any]] = {}
        
        self.get_logger().info('ODrive Driver initialized')
    
    def connect(self, device_path: str = "/dev/ttyACM0") -> bool:
        """Connect to ODrive device.
        
        Args:
            device_path: USB device path for ODrive
            
        Returns:
            True if connection successful
        """
        try:
            self.get_logger().info(f'Connecting to ODrive at {device_path}...')
            self.odrive = odrive.find_any(path=device_path)
            
            if self.odrive:
                self.get_logger().info('Connected to ODrive successfully')
                return True
            else:
                self.get_logger().error('Failed to connect to ODrive')
                return False
                
        except Exception as e:
            self.get_logger().error(f'Connection error: {str(e)}')
            return False
    
    def configure_axis(self, axis_num: int, config: Dict[str, Any]) -> bool:
        """Configure a specific axis.
        
        Args:
            axis_num: Axis number (0 or 1)
            config: Configuration dictionary
            
        Returns:
            True if configuration successful
        """
        if not self.odrive:
            return False
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            
            if 'motor' in config:
                motor_config = config['motor']
                axis.motor.config.current_lim = motor_config.get('current_lim', 20.0)
                axis.motor.config.torque_constant = motor_config.get('torque_constant', 8.27)
                axis.motor.config.pole_pairs = motor_config.get('poles', 12)
            
            if 'encoder' in config:
                encoder_config = config['encoder']
                axis.encoder.config.cpr = encoder_config.get('cpr', 8192)
                axis.encoder.config.direction = encoder_config.get('direction', 1)
            
            if 'controller' in config:
                ctrl_config = config['controller']
                axis.controller.config.pos_gain = ctrl_config.get('pos_gain', 100.0)
                axis.controller.config.vel_gain = ctrl_config.get('vel_gain', 0.5)
            
            if 'limits' in config:
                limits = config['limits']
                axis.controller.config.vel_limit = limits.get('vel_limit', 100.0)
                axis.motor.config.current_lim = limits.get('vel_limit', 100.0)
            
            self.get_logger().info(f'Axis {axis_num} configured successfully')
            return True
            
        except Exception as e:
            self.get_logger().error(f'Failed to configure axis {axis_num}: {str(e)}')
            return False
    
    def calibrate_axis(self, axis_num: int, wait_for_completion: bool = True) -> bool:
        """Run motor calibration for an axis.
        
        Args:
            axis_num: Axis number to calibrate
            wait_for_completion: Wait for calibration to complete
            
        Returns:
            True if calibration successful
        """
        if not self.odrive:
            return False
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            
            self.get_logger().info(f'Starting calibration for axis {axis_num}...')
            axis.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
            
            if wait_for_completion:
                timeout = 30
                start_time = time.time()
                while axis.current_state != AXIS_STATE_IDLE:
                    if time.time() - start_time > timeout:
                        self.get_logger().error('Calibration timed out')
                        return False
                    time.sleep(0.1)
                
                if axis.error == 0:
                    self.get_logger().info(f'Axis {axis_num} calibrated successfully')
                    return True
                else:
                    self.get_logger().error(f'Calibration failed with error: {axis.error}')
                    return False
            
            return True
            
        except Exception as e:
            self.get_logger().error(f'Calibration error: {str(e)}')
            return False
    
    def set_position(self, axis_num: int, position: float) -> None:
        """Set motor position.
        
        Args:
            axis_num: Axis number (0 or 1)
            position: Target position in turns
        """
        if not self.odrive:
            return
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            axis.controller.input_pos = position
        except Exception as e:
            self.get_logger().error(f'Failed to set position: {str(e)}')
    
    def set_velocity(self, axis_num: int, velocity: float) -> None:
        """Set motor velocity.
        
        Args:
            axis_num: Axis number (0 or 1)
            velocity: Target velocity in turns/second
        """
        if not self.odrive:
            return
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            axis.controller.input_vel = velocity
        except Exception as e:
            self.get_logger().error(f'Failed to set velocity: {str(e)}')
    
    def set_torque(self, axis_num: int, torque: float) -> None:
        """Set motor torque.
        
        Args:
            axis_num: Axis number (0 or 1)
            torque: Target torque in Nm
        """
        if not self.odrive:
            return
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            axis.controller.input_torque = torque
        except Exception as e:
            self.get_logger().error(f'Failed to set torque: {str(e)}')
    
    def get_position(self, axis_num: int) -> float:
        """Get current motor position.
        
        Args:
            axis_num: Axis number
            
        Returns:
            Current position in turns
        """
        if not self.odrive:
            return 0.0
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            return axis.encoder.pos_estimate
        except Exception as e:
            self.get_logger().error(f'Failed to get position: {str(e)}')
            return 0.0
    
    def get_velocity(self, axis_num: int) -> float:
        """Get current motor velocity.
        
        Args:
            axis_num: Axis number
            
        Returns:
            Current velocity in turns/second
        """
        if not self.odrive:
            return 0.0
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            return axis.encoder.vel_estimate
        except Exception as e:
            self.get_logger().error(f'Failed to get velocity: {str(e)}')
            return 0.0
    
    def set_idle_state(self, axis_num: int) -> None:
        """Set axis to idle state.
        
        Args:
            axis_num: Axis number
        """
        if not self.odrive:
            return
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            axis.requested_state = AXIS_STATE_IDLE
        except Exception as e:
            self.get_logger().error(f'Failed to set idle state: {str(e)}')
    
    def set_closed_loop_control(self, axis_num: int) -> None:
        """Set axis to closed loop control mode.
        
        Args:
            axis_num: Axis number
        """
        if not self.odrive:
            return
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        except Exception as e:
            self.get_logger().error(f'Failed to set closed loop control: {str(e)}')
    
    def get_errors(self, axis_num: int) -> Dict[str, Any]:
        """Get error states for an axis.
        
        Args:
            axis_num: Axis number
            
        Returns:
            Dictionary of error states
        """
        if not self.odrive:
            return {}
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            return {
                'axis_error': axis.error,
                'motor_error': axis.motor.error,
                'encoder_error': axis.encoder.error,
                'controller_error': axis.controller.error,
            }
        except Exception as e:
            self.get_logger().error(f'Failed to get errors: {str(e)}')
            return {}
    
    def clear_errors(self, axis_num: int) -> bool:
        """Clear errors for an axis.
        
        Args:
            axis_num: Axis number
            
        Returns:
            True if successful
        """
        if not self.odrive:
            return False
            
        try:
            axis = getattr(self.odrive, f'axis{axis_num}')
            axis.error = 0
            axis.motor.error = 0
            axis.encoder.error = 0
            axis.controller.error = 0
            return True
        except Exception as e:
            self.get_logger().error(f'Failed to clear errors: {str(e)}')
            return False


def main(args=None):
    rclpy.init(args=args)
    driver = ODriveDriver()
    
    try:
        if driver.connect():
            driver.set_closed_loop_control(0)
            driver.set_closed_loop_control(1)
            rclpy.spin(driver)
    except KeyboardInterrupt:
        pass
    finally:
        driver.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
