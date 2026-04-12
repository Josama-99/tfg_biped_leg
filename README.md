# tfg_biped_leg

Bipedal robot leg control using ODrive motor controllers with ROS2.

## Overview

This package provides ROS2-based control for a 3-DOF bipedal robot leg using ODrive v3.6 motor controllers. It includes forward/inverse kinematics, trajectory generation, and ROS2 integration.

## Hardware Requirements

- Raspberry Pi (or similar SBC)
- ODrive v3.6 motor controller
- 3x brushless motors with encoders
- USB connection to ODrive

## Software Requirements

- ROS2 (Humble or later recommended)
- Python 3.8+
- ODrive firmware v0.5.x

## Installation

### 1. Clone the repository

```bash
cd ~/ros2_ws/src
git clone https://github.com/YOUR_USERNAME/tfg_biped_leg.git
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

### 4. Set up ODrive permissions

```bash
sudo chmod 666 /dev/ttyACM0
```

Or create a udev rule:

```bash
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666"' | sudo tee /etc/udev/rules.d/50-odrive.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Usage

### Calibrate Motors

Before first use, calibrate each motor:

```bash
python3 scripts/calibrate_motors.py
```

### Launch the Controller

```bash
ros2 launch tfg_biped_leg bringup.launch.py
```

### Test the Leg

```bash
python3 scripts/test_leg.py
```

## Package Structure

```
tfg_biped_leg/
├── config/           # Motor configuration files
├── launch/           # ROS2 launch files
├── msg/              # Custom message definitions
├── srv/              # Service definitions
├── tfg_biped_leg/    # Main Python package
│   ├── odrive_driver.py
│   ├── leg_kinematics.py
│   ├── leg_controller.py
│   └── trajectory_generator.py
├── scripts/          # Utility scripts
└── tests/            # Unit tests
```

## Configuration

Motor parameters are stored in `config/*.yaml`:

- `hip.yaml` - Hip joint configuration
- `knee.yaml` - Knee joint configuration
- `ankle.yaml` - Ankle joint configuration

## ROS2 Topics

### Published Topics

- `/leg_controller/joint_states` - Current joint positions
- `/leg_controller/joint_commands` - Joint position commands

### Subscribed Topics

- `/leg_controller/target_pose` - Target position in Cartesian space

## License

MIT License

## Author

pi@raspberrypi
