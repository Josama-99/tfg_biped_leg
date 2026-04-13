import time
import odrive
import asyncio
from .odrive_enums import (
    AxisState, ControlMode, 
    decode_error_enum, display_error_enum_nb, 
    ODriveError, AxisError, MotorError, 
    EncoderError, ControllerError)

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from typing import Callable


def _is_ipython():
    try:
        get_ipython()
        return True
    except NameError:
        return False


def _find_odrive_async(sn=None):
    """
    Async version to find ODrive, works in Jupyter notebooks.
    """
    async def _find():
        if sn is None:
            return await odrive.find_any()
        else:
            return await odrive.find_any(serial_number=sn)
    
    try:
        loop = asyncio.get_running_loop()
        coro = _find()
        return asyncio.run_coroutine_threadsafe(coro, loop).result()
    except RuntimeError:
        return asyncio.run(_find())


class IOdrive:
    default_config = {
        "current_limit": 30, # A
        "velocity_limit": 5, # turn/s
        "calibration_current": 10, # A
        "break_resistor_enabled": True,
        "pole_pairs": 7,
        "motor_torque_constant": 8.27/270, # 8.27 / motor_kv //// default odrive motor_kv = 270
        "encoder_cpr": 8192,
    }

    def __init__(self, serial_number=None):
        self.__control_mode = ControlMode.TORQUE_CONTROL
        self.odrv = self.connect_to_odrive(serial_number)
        self.odrv.clear_errors()
        self.calibrate()

    def connect_to_odrive(self, sn=None):
        """
        Connects to the first available ODrive device over USB.

        :return: An instance of the connected ODrive device.
        :raises: Exception if no device is found.
        """
        print("Searching for ODrive...")
        try:
            asyncio.get_running_loop()
            odrv = _find_odrive_async(sn)
        except RuntimeError:
            if sn is None:
                odrv = odrive.find_any()
            else:
                odrv = odrive.find_any(serial_number=sn)

        print(f"Connected to ODrive with serial number: {odrv.serial_number}")
        return odrv
    
    def calibrate(self):
        self.odrv.axis1.requested_state = AxisState.AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        axis_name = "axis1"
        self.wait_for_idle(axis_name)
        print(f"{axis_name} calibration completed.")

    def enable_closed_loop(self):
        self.odrv.axis1.requested_state = AxisState.AXIS_STATE_CLOSED_LOOP_CONTROL

    def print_odrive_errors(self):
        """
        Recursively prints error fields from the ODrive, its axes, and subcomponents.

        :param odrv: An instance of the connected ODrive device.
        """
        print(f"ODrive Error: {decode_error_enum(self.odrv.error, ODriveError)}")
        
        for axis_id in [0, 1]:
            axis = getattr(self.odrv, f"axis{axis_id}")
            print(f"Axis{axis_id} Error: {decode_error_enum(axis.error, AxisError)}")
            print(f"  Motor Error: {decode_error_enum(axis.motor.error, MotorError)}")
            print(f"  Encoder Error: {decode_error_enum(axis.encoder.error, EncoderError)}")
            print(f"  Controller Error: {decode_error_enum(axis.controller.error, ControllerError)}")
    
    def print_odrive_errors_nb(self):
        """
        Recursively prints error fields from the ODrive, its axes, and subcomponents.

        :param odrv: An instance of the connected ODrive device.
        """
        print(f"ODrive Error: {display_error_enum_nb(self.odrv.error, ODriveError, 'Odrive')}")
        
        for axis_id in [0, 1]:
            axis = getattr(self.odrv, f"axis{axis_id}")
            print(f"Axis{axis_id} Error: {display_error_enum_nb(axis.error, AxisError, 'Axis')}")
            print(f"  Motor Error: {display_error_enum_nb(axis.motor.error, MotorError, 'Motor')}")
            print(f"  Encoder Error: {display_error_enum_nb(axis.encoder.error, EncoderError, 'Encoder')}")
            print(f"  Controller Error: {display_error_enum_nb(axis.controller.error, ControllerError, 'Controller')}")

    def wait_for_idle(self, axis_name: str = "axis0", poll_interval: float = 0.1) -> None:
        """
        Waits until the given axis returns to IDLE state after an operation.

        :param axis_name: Name of the axis ('axis0' or 'axis1')
        :param poll_interval: Time (in seconds) between status checks
        """
        axis = getattr(self.odrv, axis_name)
        while axis.current_state != AxisState.IDLE:
            time.sleep(poll_interval)

    def set_default_config(self):
        self.set_config(self.default_config)
        
    def set_config(self, config):
        self.odrv.axis1.motor.config.current_lim = config["current_limit"]
        self.odrv.axis1.controller.config.vel_limit = config["velocity_limit"]
        self.odrv.axis1.motor.config.calibration_current = config["calibration_current"]

        # Enable break resistor to absorb the parasite current generated when breaking
        self.odrv.config.enable_brake_resistor = config["break_resistor_enabled"]
        # If needed change the default value for the resistor, value in Ohms
        # self.odrv.config.brake_resistance = X # Ohms

        # Configure the number of pole pairs (the following values are for the official Odrive motor)
        self.odrv.axis1.motor.config.pole_pairs = config["pole_pairs"]
        self.odrv.axis1.motor.config.torque_constant = config["motor_torque_constant"] # El 8.27 es numero magico del fabricante

        # Configure encoder Counts Per Revolution (CPR) if needed, values bellow for default ODrive encoder
        self.odrv.axis1.encoder.config.cpr = config["encoder_cpr"] # CPR = PPR * 4
        self.print_config()

    def get_config(self):
        return {
            "current_limit": self.odrv.axis1.motor.config.current_lim, # A
            "velocity_limit": self.odrv.axis1.controller.config.vel_limit, # turn/s
            "calibration_current": self.odrv.axis1.motor.config.calibration_current, # A
            "break_resistor_enabled": self.odrv.config.enable_brake_resistor,
            "pole_pairs": self.odrv.axis1.motor.config.pole_pairs,
            "motor_torque_constant": self.odrv.axis1.motor.config.torque_constant, # 8.27 / motor_kv
            "encoder_cpr": self.odrv.axis1.encoder.config.cpr,
        }

    def save_config(self):
        try:
            self.odrv.save_configuration()
        except:
            self.odrv = self.connect_to_odrive()
            self.odrv.clear_errors()
            self.calibrate()

    def print_config(self):
        print(f"Current configuration:\
              \n\t Current limit: {self.odrv.axis1.motor.config.current_lim}\
              \n\t Velocity limit: {self.odrv.axis1.controller.config.vel_limit}\
              \n\t Calibration Current: {self.odrv.axis1.motor.config.calibration_current}\
              \n\t Break Resistor enabled: {self.odrv.config.enable_brake_resistor}\
              \n\t Pole Pairs: {self.odrv.axis1.motor.config.pole_pairs}\
              \n\t Motor Torque constant: {self.odrv.axis1.motor.config.torque_constant}\
              \n\t Encoder Counts Per Revolution (CPR): {self.odrv.axis1.encoder.config.cpr}")

    def get_current_torque(self):
        current_torque = self.odrv.axis1.motor.current_control.Iq_setpoint * self.odrv.axis1.motor.config.torque_constant # Torque [Nm]
        return current_torque

    def get_current_vel(self):
        current_vel = self.odrv.axis0.encoder.vel_estimate*60 # turns/s to rpm
        return current_vel
    
    def get_current_pos(self):
        current_pos = self.odrv.axis1.encoder.pos_estimate
        return current_pos

    def start_encoder_live_plot(
        self,
        get_value: Callable[[], float],
        interval: float = 50,
        num_points: int = 500
    ) -> None:
        """
        Starts a real-time encoder live plot using matplotlib animation.

        :param get_value: Callable returning a float (e.g., encoder position).
        :param interval: Update interval in milliseconds.
        :param num_points: Number of points to retain/display.
        """
        fig, ax = plt.subplots()
        x_data: list[float] = []
        y_data: list[float] = []
        line, = ax.plot([], [], label="Encoder Position")
        ax.set_title("Live Encoder Position")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Position")
        ax.grid(True)
        ax.legend()

        start_time = time.time()

        def init():
            ax.set_xlim(0, 10)
            ax.set_ylim(-1, 1)
            return line,

        def update(frame):
            now = time.time() - start_time
            y = get_value()

            x_data.append(now)
            y_data.append(y)

            if len(x_data) > num_points:
                x_data.pop(0)
                y_data.pop(0)

            line.set_data(x_data, y_data)

            ax.set_xlim(max(0, now - num_points * interval / 1000), now)
            ax.set_ylim(min(y_data) - 0.1, max(y_data) + 0.1)

            return line,

        ani = animation.FuncAnimation(
            fig,
            update,
            init_func=init,
            interval=interval,
            blit=True
        )

        plt.show()


    @property
    def control_mode(self) -> str:
        """
        Gets the current motor speed.
        """
        cm = {ControlMode.TORQUE_CONTROL: "Torque Control",
              ControlMode.POSITION_CONTROL: "Position Control",
              ControlMode.VELOCITY_CONTROL: "Velocity Control"}
        return cm[self.__control_mode]

    @control_mode.setter
    def control_mode(self, value: int) -> None:
        """
        Sets the motor control mode.
        """
        cm = {ControlMode.TORQUE_CONTROL: "Torque Control",
              ControlMode.POSITION_CONTROL: "Position Control",
              ControlMode.VELOCITY_CONTROL: "Velocity Control"}
        if value in cm:
            self.odrv.axis1.controller.input_pos = 0
            self.odrv.axis1.controller.input_vel = 0
            self.odrv.axis1.controller.input_torque = 0
            self.__control_mode = value
            self.odrv.axis1.controller.config.control_mode = value
        else:
            raise ValueError("Invalid control mode.")
        

    @property
    def reference(self):
        if self.__control_mode == ControlMode.TORQUE_CONTROL:
            print(f"Current torque [Nm] reference: {self.odrv.axis1.controller.input_torque}")
        elif self.__control_mode == ControlMode.POSITION_CONTROL:
            print(f"Current position [turns] reference: {self.odrv.axis1.controller.input_pos}")
        elif self.__control_mode == ControlMode.VELOCITY_CONTROL:
            print(f"Current velocity [turns/s] reference: {self.odrv.axis1.controller.input_vel}")
    
    @reference.setter
    def reference(self, value):
        if self.__control_mode == ControlMode.TORQUE_CONTROL:
            self.odrv.axis1.controller.input_torque = value
            print(f"Torque reference set to {value} Nm")
        elif self.__control_mode == ControlMode.POSITION_CONTROL:
            self.odrv.axis1.controller.input_pos = value
            print(f"Position reference set to {value} turns")
        elif self.__control_mode == ControlMode.VELOCITY_CONTROL:
            self.odrv.axis1.controller.input_vel = value
            print(f"Velocity reference set to {value} turns/s")
