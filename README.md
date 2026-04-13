# tfg_biped_leg

Bipedal robot leg control using ODrive motor controllers.

## Overview

This package provides control for a 3-DOF bipedal robot leg using:
- **Raspberry Pi** as main controller
- **ODrive v3.6** for motor control
- **TCA9548A** I2C multiplexer
- **AS5600** magnetic encoders for joint position sensing

**Current Status**: ODrive connected ✅, Single motor testing ✅

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Raspberry Pi                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ ODrive USB   │  │ I2C Mux      │  │ Control Logic            │ │
│  │ (Motor Ctrl) │  │ (Encoders)   │  │ (Position Commands)     │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘ │
└─────────┼──────────────────┼────────────────────┼──────────────────┘
           │                  │                    │
           ▼                  ▼                    │
     ┌──────────┐      ┌──────────┐                │
     │ ODrive   │      │TCA9548A  │◄───────────────┘
     │ v3.6     │      │I2C Mux   │
     └────┬─────┘      └────┬─────┘
          │                 │
          ▼                 ▼
     ┌──────────┐     ┌──────────┬──────────┬──────────┐
     │ D5065    │     │ AS5600   │ AS5600   │ AS5600   │
     │ Motor    │     │ (Hip)    │ (Knee)   │ (Ankle)  │
     └──────────┘     └──────────┴──────────┴──────────┘
```

## Hardware

### Current Test Setup
| Component | Model | Value |
|-----------|-------|-------|
| ODrive | Official v3.6 | USB connected (/dev/ttyACM0) ✅ |
| Motor | D5065 | 270 KV |
| Axis | Axis 1 | Primary test |
| Power | 12V | DC supply |

### Future Requirements (3-DOF Leg)
| Component | Quantity |
|-----------|----------|
| ODrive v3.6 | 3 |
| D5065 Motor | 3 |
| AS5600 Encoder | 3 |
| TCA9548A I2C Mux | 1 |

## Installation (Pi Setup)

### 1. Clone the repository
```bash
cd ~/tfg
git clone git@github.com:Josama-99/tfg_biped_leg.git
```

### 2. Install ROS2 Jazzy
```bash
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu \$(. /etc/os-release && echo \$UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install ros-jazzy-ros-base
```

### 3. Create virtual environment
```bash
cd ~/tfg/tfg_biped_leg
sudo apt install python3.12-venv
python3 -m venv tfg_venv
source tfg_venv/bin/activate
pip install --editable .
pip install odrive numpy smbus2 pyyaml colorama matplotlib
```

### 4. Set up ODrive USB permissions
```bash
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666"' | sudo tee /etc/udev/rules.d/50-odrive.rules
sudo udevadm control --reload-rules
```

### 5. Enable I2C on Raspberry Pi (for encoders)
```bash
sudo raspi-config
# → Interface Options → I2C → Enable
sudo apt install i2c-tools python3-smbus
```

## Usage

### Interactive ODrive Test
```bash
source /opt/ros/jazzy/setup.bash
source ~/tfg/tfg_biped_leg/tfg_venv/bin/activate
sudo /home/pi/tfg/tfg_biped_leg/tfg_venv/bin/python3 /home/pi/tfg/odrive_test.py
```

Or run without sudo (after udev rule is applied):
```bash
source /opt/ros/jazzy/setup.bash
source ~/tfg/tfg_biped_leg/tfg_venv/bin/activate
python3 /home/pi/tfg/odrive_test.py
```

### Test Single Motor (automated)
```bash
source /opt/ros/jazzy/setup.bash
source ~/tfg/tfg_biped_leg/tfg_venv/bin/activate
python3 scripts/test_single_motor.py
```

### Calibrate Motors
```bash
source /opt/ros/jazzy/setup.bash
source ~/tfg/tfg_biped_leg/tfg_venv/bin/activate
python3 scripts/calibrate_motors.py
```

### Launch ROS2 Controller
```bash
source /opt/ros/jazzy/setup.bash
source ~/tfg/tfg_biped_leg/tfg_venv/bin/activate
ros2 launch tfg_biped_leg bringup.launch.py
```

## Package Structure

```
tfg_biped_leg/
├── config/                     # Motor configurations
│   └── my_config.json          # D5065 motor settings
├── launch/                     # ROS2 launch files
├── msg/                        # ROS2 messages
├── srv/                        # ROS2 services
├── src/                        # Low-level drivers (TODO)
│   ├── as5600_encoder.py       # AS5600 driver
│   └── i2c_mux.py             # TCA9548A driver
├── tfg_biped_leg/             # Main Python package
│   ├── odrive_interface.py     # ODrive motor control
│   ├── odrive_enums.py         # ODrive enums
│   ├── odrive_driver.py        # ROS2 ODrive driver
│   ├── leg_kinematics.py       # FK/IK
│   └── trajectory_generator.py  # Gait patterns
├── scripts/                    # Utility scripts
│   ├── test_single_motor.py    # Single motor test
│   ├── calibrate_motors.py     # Motor calibration
│   └── odrive_test.py          # Interactive test menu
└── tests/                      # Unit tests
```

## Motor Configuration

Default settings (`config/my_config.json`):

```json
{
    "current_limit": 30,
    "velocity_limit": 5,
    "calibration_current": 10,
    "pole_pairs": 7,
    "motor_torque_constant": 8.27/270,
    "encoder_cpr": 8192,
}
```

## 3-DOF Joint Configuration

| Joint | Axis | Range | Gearbox |
|-------|------|-------|---------|
| Hip | 0 | ±45° | 16:1 |
| Knee | 1 | -90° to 0° | 16:1 |
| Ankle | 2 | ±30° | 16:1 |

## Encoder Information

### AS5600
- **Type**: Magnetic rotary encoder
- **Resolution**: 12-bit (4096 positions/rev)
- **I2C Address**: 0x36 (all units same)
- **Note**: Requires TCA9548A I2C multiplexer for multiple units

### TCA9548A
- **Channels**: 8 independent I2C buses
- **I2C Address**: 0x70 (default)
- **Purpose**: Enable 3 AS5600 encoders on one Pi I2C bus

## Testing the ODrive

### Interactive Test Menu

Run the test script:
```bash
sudo /home/pi/tfg/tfg_biped_leg/tfg_venv/bin/python3 /home/pi/tfg/odrive_test.py
```

Menu options:
| Option | Description |
|--------|-------------|
| 1 | Print errors |
| 2 | Print current config |
| 3 | Set default config |
| 4 | Set custom config |
| 5 | Save config |
| 6 | Enable closed loop ✅ |
| 7 | Set torque control |
| 8 | Set position control |
| 9 | Set reference (torque/position) |
| 10 | Live position plot |
| 0 | Exit |

### How to Make Motor Turn

1. **Select option 6** → Enable closed loop control
2. **Select option 8** → Set position control
3. **Select option 9** → Enter value (e.g., 0.5 for half turn)

## Chinese ODrive Clones

If using M1 M22015 (Makerbase):
- Device may appear as `/dev/ttyACM1`
- May show "board not genuine" - usually works
- https://github.com/makerbase-mks/ODrive-MKS

## License

MIT License