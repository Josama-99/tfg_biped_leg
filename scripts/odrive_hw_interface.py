"""
Connects to an ODrive V3.6 motor controller using the official ODrive Python library.
Requires the 'odrive' package to be installed (`pip install odrive`).
"""

import odrive
from odrive_enums import *
import time

CURRENT_LIMIT = 10 # A
VEL_LIMIT = 2 # turn/s
STATIONARY_CURRENT = 10 # A

CONTROL_MODE = "torque"

def connect_to_odrive():
    """
    Connects to the first available ODrive device over USB.

    :return: An instance of the connected ODrive device.
    :raises: Exception if no device is found.
    """
    print("Searching for ODrive...")
    odrv = odrive.find_any()
    print(f"Connected to ODrive with serial number: {odrv.serial_number}")
    return odrv

if __name__ == "__main__":
    odrv0 = connect_to_odrive()
    odrv0.clear_errors()
    print(f"Current Voltage: {odrv0.vbus_voltage}")
    odrv0.axis1.motor.config.current_lim = CURRENT_LIMIT
    odrv0.axis1.controller.config.vel_limit = VEL_LIMIT
    odrv0.axis1.motor.config.calibration_current = STATIONARY_CURRENT

    # Enable break resistor to absorb the parasite current generated when breaking
    odrv0.config.enable_brake_resistor = True
    # If needed change the default value for the resistor, value in Ohms
    # odrv0.config.brake_resistance = X # Ohms

    # Configure the number of pole pairs (the following values are for the official Odrive motor)
    odrv0.axis1.motor.config.pole_pairs = 7
    motor_kv = 270
    odrv0.axis1.motor.config.torque_constant = 8.27/motor_kv # El 8.27 es numero magico del fabricante

    # Configure encoder Counts Per Revolution (CPR) if needed, values bellow for default ODrive encoder
    odrv0.axis1.encoder.config.cpr = 8192 # CPR = PPR * 4

    # Before start controlling the motor, run a full calibration
    odrv0.axis1.requested_state = AxisState.AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    time.sleep(5)
    # Start closed loop control
    odrv0.axis0.requested_state = AxisState.AXIS_STATE_CLOSED_LOOP_CONTROL

    if CONTROL_MODE == "position":
        odrv0.axis1.controller.config.control_mode = ControlMode.POSITION_CONTROL
    elif CONTROL_MODE == "torque":
        odrv0.axis1.controller.config.control_mode = ControlMode.TORQUE_CONTROL
    
    # Define position reference
    if CONTROL_MODE == "position":
        odrv0.axis1.controller.input_pos = 2 # turns
        time.sleep(2)
        odrv0.axis1.controller.input_pos = 0 # turns
    
    # Define torque reference
    elif CONTROL_MODE == "torque":
        odrv0.axis1.controller.input_torque = 0.1 # Nm