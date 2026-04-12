#!/usr/bin/env python3
"""
Test script for single motor control via ODrive USB.

Hardware:
- ODrive v3.6 (Official)
- Motor: D5065 270KV
- Axis: 1
- Power: 12V

Usage:
    python3 scripts/test_single_motor.py

Note: Run with sudo if you have USB permission issues.
"""

import sys
import time
sys.path.insert(0, '/home/pi/TFG')

from tfg_biped_leg.odrive_interface import IOdrive
from tfg_biped_leg.odrive_enums import AxisState, ControlMode


def test_position_control(iodrv: IOdrive, target_pos: float = 1.0):
    """Test position control mode."""
    print("\n=== Testing Position Control ===")
    
    iodrv.control_mode = ControlMode.POSITION_CONTROL
    iodrv.reference = target_pos
    print(f"Moving to position: {target_pos} turns")
    
    time.sleep(2)
    current_pos = iodrv.get_current_pos()
    print(f"Current position: {current_pos:.3f} turns")
    
    print("Returning to home (0 turns)")
    iodrv.reference = 0.0
    time.sleep(2)


def test_torque_control(iodrv: IOdrive, torque: float = 0.05):
    """Test torque control mode."""
    print("\n=== Testing Torque Control ===")
    
    iodrv.control_mode = ControlMode.TORQUE_CONTROL
    iodrv.reference = torque
    print(f"Applying torque: {torque} Nm")
    
    time.sleep(2)
    current_torque = iodrv.get_current_torque()
    print(f"Current torque: {current_torque:.4f} Nm")
    
    print("Releasing motor (0 Nm)")
    iodrv.reference = 0.0
    time.sleep(1)


def main():
    print("=" * 50)
    print("Single Motor Test - ODrive v3.6 + D5065 270KV")
    print("=" * 50)
    
    print("\nConnecting to ODrive...")
    try:
        iodrv = IOdrive()
    except Exception as e:
        print(f"ERROR: Could not connect to ODrive: {e}")
        print("\nTroubleshooting:")
        print("1. Check USB connection")
        print("2. Check ODrive power (12V)")
        print("3. Run: sudo chmod 666 /dev/ttyACM0")
        sys.exit(1)
    
    print("\nConfiguration:")
    iodrv.print_config()
    
    print("\nWaiting for calibration to complete...")
    time.sleep(1)
    
    print("\nEnabling closed-loop control...")
    iodrv.enable_closed_loop()
    
    print("\n" + "=" * 50)
    print("Motor is ready! Controls:")
    print("- Position mode: moves motor to target position")
    print("- Torque mode: applies constant torque")
    print("=" * 50)
    
    try:
        test_position_control(iodrv, target_pos=1.0)
        time.sleep(1)
        test_torque_control(iodrv, torque=0.05)
        
        print("\n=== Test Complete ===")
        print("Motor returned to idle state.")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        iodrv.odrv.axis1.requested_state = AxisState.IDLE
        print("Motor stopped.")


if __name__ == "__main__":
    main()
