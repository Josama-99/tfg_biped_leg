#!/usr/bin/env python3
"""Motor calibration script for ODrive."""

import odrive
from odrive.enums import *
import time
import sys


def calibrate_motor(odrv, axis_num, name):
    """Calibrate a single motor."""
    print(f"\n{'='*50}")
    print(f"Calibrating {name} (Axis {axis_num})")
    print(f"{'='*50}")
    
    axis = getattr(odrv, f'axis{axis_num}')
    
    print(f"Current state: {axis.current_state}")
    print(f"Current error: {axis.error}")
    
    print(f"\nClearing errors...")
    axis.error = 0
    axis.motor.error = 0
    axis.encoder.error = 0
    axis.controller.error = 0
    
    print(f"Starting calibration sequence...")
    axis.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    
    print(f"Waiting for calibration to complete...")
    start_time = time.time()
    timeout = 60
    
    while axis.current_state != AXIS_STATE_IDLE:
        time.sleep(0.1)
        if time.time() - start_time > timeout:
            print(f"ERROR: Calibration timed out!")
            return False
        
        if axis.error != 0:
            print(f"ERROR: Axis error during calibration: {axis.error}")
            return False
    
    print(f"\nCalibration completed!")
    print(f"Motor error: {axis.motor.error}")
    print(f"Encoder error: {axis.encoder.error}")
    
    if axis.motor.error == 0 and axis.encoder.error == 0:
        print(f"{name} calibrated successfully!")
        
        print(f"\nSaving configuration...")
        try:
            odrv.save_configuration()
            print(f"Configuration saved!")
        except Exception as e:
            print(f"Warning: Could not save configuration: {e}")
        
        return True
    else:
        print(f"{name} calibration FAILED!")
        return False


def main():
    """Main calibration routine."""
    print("ODrive Motor Calibration Script")
    print("="*50)
    
    print("\nSearching for ODrive...")
    try:
        odrv = odrive.find_any()
        print(f"Found ODrive: {odrv}")
        print(f"Serial number: {odrv.serial_number}")
    except Exception as e:
        print(f"ERROR: Could not find ODrive: {e}")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("FIRMWARE INFORMATION")
    print("="*50)
    print(f"Vbus voltage: {odrv.vbus_voltage:.2f}V")
    print(f"Firmware version: {odrv.fw_version}")
    
    results = []
    
    results.append(calibrate_motor(odrv, 0, "Hip Motor"))
    results.append(calibrate_motor(odrv, 1, "Knee Motor"))
    results.append(calibrate_motor(odrv, 2, "Ankle Motor"))
    
    print("\n" + "="*50)
    print("CALIBRATION SUMMARY")
    print("="*50)
    print(f"Hip:   {'SUCCESS' if results[0] else 'FAILED'}")
    print(f"Knee:  {'SUCCESS' if results[1] else 'FAILED'}")
    print(f"Ankle: {'SUCCESS' if results[2] else 'FAILED'}")
    
    if all(results):
        print("\nAll motors calibrated successfully!")
        
        print("\nEntering closed loop control mode...")
        for i, name in enumerate(["Hip", "Knee", "Ankle"]):
            axis = getattr(odrv, f'axis{i}')
            axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            print(f"{name} - Entered closed loop control")
        
        print("\nTest complete. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
                for i, name in enumerate(["Hip", "Knee", "Ankle"]):
                    axis = getattr(odrv, f'axis{i}')
                    print(f"{name}: pos={axis.encoder.pos_estimate:.3f}, vel={axis.encoder.vel_estimate:.3f}")
        except KeyboardInterrupt:
            print("\nExiting...")
            for i in range(3):
                axis = getattr(odrv, f'axis{i}')
                axis.requested_state = AXIS_STATE_IDLE
    else:
        print("\nCalibration failed. Check connections and try again.")
        sys.exit(1)


if __name__ == '__main__':
    main()
