# tfg_biped_leg

Bipedal robot leg control using ODrive motor controllers.

## Overview

This package provides control for a 3-DOF bipedal robot leg using:
- **Raspberry Pi** as main controller
- **ODrive v3.6** for motor control
- **TCA9548A** I2C multiplexer
- **AS5600** magnetic encoders for joint position sensing

**Current Status**: Single motor testing phase

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
| ODrive | Official v3.6 | USB connected |
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

## Installation

### 1. Clone the repository

```bash
cd ~/ros2_ws/src
git clone https://github.com/Josama-99/tfg_biped_leg.git
```

### 2. Install Python dependencies

```bash
pip install odrive numpy smbus
```

### 3. Enable I2C on Raspberry Pi

```bash
sudo raspi-config
# → Interface Options → I2C → Enable
sudo apt install i2c-tools python3-smbus
```

### 4. Set up ODrive USB permissions

```bash
sudo chmod 666 /dev/ttyACM0
```

Or create permanent udev rule:

```bash
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666"' | sudo tee /etc/udev/rules.d/50-odrive.rules
sudo udevadm control --reload-rules
```

### 5. Verify I2C devices

```bash
sudo i2cdetect -y 1
```

Expected output:
- `70`: TCA9548A I2C mux
- `36`: AS5600 encoder(s)

## Usage

### Test Single Motor

```bash
python3 scripts/test_single_motor.py
```

### Calibrate Motors

```bash
python3 scripts/calibrate_motors.py
```

### Launch ROS2 Controller

```bash
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
│   └── calibrate_motors.py     # Motor calibration
└── tests/                      # Unit tests
```

## Motor Configuration

Default settings (`config/my_config.json`):

```python
{
    "current_limit": 30,        # A
    "velocity_limit": 5,        # turn/s
    "calibration_current": 10, # A
    "pole_pairs": 7,
    "motor_torque_constant": 8.27/270,  # Nm/A
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

## Chinese ODrive Clones

If using M1 M22015 (Makerbase):
- Device may appear as `/dev/ttyACM1`
- May show "board not genuine" - usually works
- https://github.com/makerbase-mks/ODrive-MKS

## License

MIT License
