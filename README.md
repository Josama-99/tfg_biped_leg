# tfg_biped_leg

Bipedal robot leg control using ODrive motor controllers with ROS2.

## Overview

This package provides ROS2-based control for a 3-DOF bipedal robot leg using ODrive v3.6 motor controllers. It includes forward/inverse kinematics, trajectory generation, and ROS2 integration.

**Current Status**: Single motor testing phase (1 ODrive, 1 motor)

## Hardware

### Current Test Setup
| Component | Model | Notes |
|-----------|-------|-------|
| ODrive | Official v3.6 | USB connected |
| Motor | D5065 270KV | Brushless DC |
| Axis | Axis 1 | Primary test axis |
| Power | 12V | DC supply |

### Future Requirements (3-DOF Leg)
- 3x ODrive v3.6 (or compatible)
- 3x brushless motors (D5065 or similar)
- Raspberry Pi
- USB hub (for multiple ODrives)

## Software Requirements

- ROS2 (Humble or later recommended)
- Python 3.8+
- ODrive Python library

## Installation

### 1. Clone the repository

```bash
cd ~/ros2_ws/src
git clone https://github.com/Josama-99/tfg_biped_leg.git
```

### 2. Install Python dependencies

```bash
pip install odrive numpy
```

### 3. Build the package

```bash
cd ~/ros2_ws
colcon build --packages-select tfg_biped_leg
source install/setup.bash
```

### 4. Set up ODrive USB permissions

```bash
sudo chmod 666 /dev/ttyACM0
```

Or create a permanent udev rule:

```bash
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666"' | sudo tee /etc/udev/rules.d/50-odrive.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Usage

### Single Motor Test

Test single motor control with the official ODrive:

```bash
python3 scripts/test_single_motor.py
```

This script will:
1. Connect to ODrive via USB
2. Run motor calibration
3. Enable closed-loop control
4. Test position control (moves 1 turn)
5. Test torque control

**Note**: Run with `sudo` if you have USB permission issues.

### Calibrate Motors

Before first use, calibrate each motor:

```bash
python3 scripts/calibrate_motors.py
```

### Launch ROS2 Controller

```bash
ros2 launch tfg_biped_leg bringup.launch.py
```

### Test the Leg (ROS2)

```bash
python3 scripts/test_leg.py
```

## Package Structure

```
tfg_biped_leg/
├── config/                 # Motor configurations
│   ├── my_config.json      # D5065 motor settings
│   ├── hip.yaml
│   ├── knee.yaml
│   └── ankle.yaml
├── launch/                 # ROS2 launch files
├── msg/                    # Custom message definitions
├── srv/                    # Service definitions
├── tfg_biped_leg/          # Main Python package
│   ├── odrive_interface.py # IOdrive class (USB motor control)
│   ├── odrive_enums.py     # ODrive state/error enums
│   ├── odrive_driver.py     # ROS2 ODrive driver
│   ├── leg_kinematics.py   # FK/IK for 3-DOF leg
│   ├── leg_controller.py    # ROS2 controller node
│   └── trajectory_generator.py
├── scripts/                # Utility scripts
│   ├── test_single_motor.py # Single motor test
│   ├── calibrate_motors.py  # Motor calibration
│   └── test_leg.py         # Basic leg testing
└── tests/                  # Unit tests
```

## Motor Configuration

Default motor settings (from `config/my_config.json`):

```python
{
    "current_limit": 30,        # A
    "velocity_limit": 5,        # turn/s
    "calibration_current": 10,  # A
    "break_resistor_enabled": True,
    "pole_pairs": 7,
    "motor_torque_constant": 8.27/270,  # Nm/A
    "encoder_cpr": 8192,
}
```

## ROS2 Topics

### Published Topics
- `/leg_controller/joint_states` - Current joint positions
- `/leg_controller/joint_commands` - Joint position commands

### Subscribed Topics
- `/leg_controller/target_pose` - Target position in Cartesian space

## Chinese ODrive Clones

If using a Chinese ODrive clone (e.g., M1 M22015 / Makerbase):
- Device may appear as `/dev/ttyACM1` instead of `/dev/ttyACM0`
- May show "board not genuine" warning - usually still works
- Check: https://github.com/makerbase-mks/ODrive-MKS

## License

MIT License
