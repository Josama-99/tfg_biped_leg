from typing import List
from enum import IntFlag

class AxisState:
    UNDEFINED = 0
    IDLE = 1
    STARTUP_SEQUENCE = 2
    AXIS_STATE_FULL_CALIBRATION_SEQUENCE = 3
    MOTOR_CALIBRATION = 4
    SENSORLESS_CONTROL = 5
    ENCODER_INDEX_SEARCH = 6
    ENCODER_OFFSET_CALIBRATION = 7
    AXIS_STATE_CLOSED_LOOP_CONTROL = 8
    LOCKIN_SPIN = 9
    ENCODER_DIR_FIND = 10
    HOMING = 11

class ControlMode:
    VOLTAGE_CONTROL = 0
    TORQUE_CONTROL = 1
    VELOCITY_CONTROL = 2
    POSITION_CONTROL = 3

class ODriveError(IntFlag):
    NONE = 0
    INITIALIZATION_ERROR = 0x00000001
    SYSTEM_LEVEL = 0x00000002
    TIMING_ERROR = 0x00000004
    MISSING_ESTIMATOR = 0x00000008
    BAD_CONFIG = 0x00000010
    DRV_FAULT = 0x00000020
    UNKNOWN_ERROR = 0x80000000


class AxisError(IntFlag):
    NONE = 0
    INVALID_STATE = 0x00000001
    DC_BUS_UNDER_VOLTAGE = 0x00000002
    DC_BUS_OVER_VOLTAGE = 0x00000004
    CURRENT_MEASUREMENT_TIMEOUT = 0x00000008
    BRAKE_RESISTOR_DISARMED = 0x00000010
    MOTOR_DISARMED = 0x00000020
    MOTOR_FAILED = 0x00000040
    SENSORLESS_ESTIMATOR_FAILED = 0x00000080
    ENCODER_FAILED = 0x00000100
    CONTROLLER_FAILED = 0x00000200
    POS_CTRL_DURING_SENSORLESS = 0x00000400
    WATCHDOG_TIMER_EXPIRED = 0x00000800
    MIN_ENDSTOP_PRESSED = 0x00001000
    MAX_ENDSTOP_PRESSED = 0x00002000
    ESTOP_REQUESTED = 0x00004000
    HOMING_WITHOUT_ENDSTOP = 0x00008000
    OVER_TEMP = 0x00010000


class MotorError(IntFlag):
    NONE = 0
    PHASE_RESISTANCE_OUT_OF_RANGE = 0x00000001
    PHASE_INDUCTANCE_OUT_OF_RANGE = 0x00000002
    ADC_FAILED = 0x00000004
    DRV_FAULT = 0x00000008
    CONTROL_DEADLINE_MISSED = 0x00000010
    NOT_IMPLEMENTED_MOTOR_TYPE = 0x00000020
    BRAKE_CURRENT_OUT_OF_RANGE = 0x00000040
    MODULATION_MAGNITUDE = 0x00000080
    BRAKE_DEADTIME_VIOLATION = 0x00000100
    CURRENT_SENSE_SATURATION = 0x00000200
    CURRENT_LIMIT_VIOLATION = 0x00000400
    MODULATION_IS_NAN = 0x00000800
    MOTOR_THERMISTOR_OVER_TEMP = 0x00001000
    FET_THERMISTOR_OVER_TEMP = 0x00002000
    TIMER_UPDATE_MISSED = 0x00004000
    CURRENT_MEASUREMENT_UNAVAILABLE = 0x00008000
    CONTROLLER_FAILED = 0x00010000
    I_BUS_OUT_OF_RANGE = 0x00020000
    BRAKE_RESISTOR_DISARMED = 0x00040000
    SYSTEM_LEVEL = 0x00080000
    BAD_TIMING = 0x00100000
    UNKNOWN_ERROR = 0x80000000


class EncoderError(IntFlag):
    NONE = 0
    UNSTABLE_GAIN = 0x00000001
    CPR_POLEPAIRS_MISMATCH = 0x00000002
    NO_RESPONSE = 0x00000004
    UNSUPPORTED_ENCODER_MODE = 0x00000008
    ILLEGAL_HALL_STATE = 0x00000010
    INDEX_NOT_FOUND_YET = 0x00000020
    ABS_SPI_TIMEOUT = 0x00000040
    ABS_SPI_COM_FAIL = 0x00000080
    ABS_SPI_NOT_READY = 0x00000100
    HALL_NOT_CALIBRATED_YET = 0x00000200


class ControllerError(IntFlag):
    NONE = 0
    OVERSPEED = 0x00000001


from enum import IntFlag
from typing import List
from colorama import init, Fore, Style

init(autoreset=True)


def decode_error_enum(error_code: int, error_enum: IntFlag) -> List[str]:
    """
    Decodes a bitmask error field into human-readable strings with color.

    :param error_code: Integer value of the error field
    :param error_enum: Enum class (e.g., AxisError)
    :return: List of colored string messages for each error
    """
    if error_code == 0:
        return [Fore.GREEN + "No error" + Style.RESET_ALL]

    decoded_errors = []
    for member in type(error_enum):
        if member != member.NONE and (error_code & member):
            name = member.name.replace("_", " ").title()
            decoded_errors.append(Fore.RED + name + Style.RESET_ALL)

    return decoded_errors

from IPython.display import display, HTML

def display_error_enum_nb(error_code: int, error_enum: IntFlag, title: str) -> None:
    """
    Displays color-coded ODrive error messages using HTML (for Jupyter).

    :param error_code: Integer error value.
    :param error_enum: Enum class for decoding (e.g., AxisError).
    :param title: Section title to display.
    """
    if error_code == 0:
        color = "green"
        messages = ["No error"]
    else:
        color = "red"
        messages = [
            member.name.replace("_", " ").title()
            for member in type(error_enum)
            if member != member.NONE and (error_code & member)
        ]

    html_lines = [f"<b>{title}:</b>"]
    for msg in messages:
        html_lines.append(f"<span style='color: {color}'>{msg}</span>")
    display(HTML("<br>".join(html_lines)))

