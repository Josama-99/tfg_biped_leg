# tfg_biped_leg

Bipedal robot leg control using ODrive motor controllers.

## Overview

This package provides control for a 3-DOF bipedal robot leg using:
- **Raspberry Pi** as main controller
- **ODrive v3.6** for motor control
- **TCA9548A** I2C multiplexer
- **AS5600** magnetic encoders for joint position sensing

**Current Status**: Official ODrive working ✅, TCA9548A + AS5600 encoder reading ✅, Makerbase BRICKED ⚠️

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              Raspberry Pi                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Official     │  │ Makerbase    │  │ I2C Mux      │  │ Control Logic    │ │
│  │ ODrive v3.6  │  │ M1 M22015    │  │              │  │                  │ │
│  │ (1 motor)    │  │ (2 motors)   │  │ (Encoders)   │  │                  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
└─────────┼──────────────────┼──────────────────┼─────────────────┼──────────┘
           │                  │                  │                  │
           ▼                  ▼                  ▼                  │
      ┌──────────┐      ┌──────────┐      ┌──────────┐            │
      │ Official │      │ Makerbase│      │TCA9548A  │◄───────────┘
      │ ODrive   │      │ ODrive   │      │I2C Mux   │
      └────┬─────┘      └────┬─────┘      └────┬─────┘
           │                 │                 │
           ▼                 ▼                 ▼
       ┌──────────┐     ┌──────────┐      ┌──────────┬──────────┬──────────┐
       │ D5065    │     │ D5065    │      │ AS5600   │ AS5600   │ AS5600   │
       │ (Hip1)   │     │ (Hip2 +  │      │ (Hip1)   │ (Hip2)   │ (Knee)   │
       │          │     │  Knee)   │      │          │          │          │
       └──────────┘     └──────────┘      └──────────┴──────────┴──────────┘
```

## Hardware

### Current Test Setup (Dual ODrive, 3 Motors)
| Component | Model | Value | Status |
|-----------|-------|-------|--------|
| Official ODrive | ODrive v3.6 | USB connected (/dev/ttyACM0) | ✅ Working |
| Makerbase ODrive | M1 M22015 | USB DFU mode (0483:df11) | ⚠️ Needs firmware |
| Motors | D5065 | 270 KV | 🔌 Connected |

### Motor Distribution
| ODrive | Motors | Joints |
|--------|--------|--------|
| Official ODrive v3.6 | 1 | Hip 1 (Abduction/Adduction, X-axis) |
| Makerbase M1 M22015 | 2 | Hip 2 (Flexion/Extension, Y-axis) + Knee (Flexion/Extension, Y-axis) |

### Joint Configuration (No Ankle, Ball Foot)
Coordinate system (right leg): +X = Front, +Y = Left, +Z = Up. Fully extended leg points in -Z.
| Joint | Rotation Axis | ODrive | ODrive Axis | Z Offset (from Hip Mount) | Range | Gearbox |
|-------|---------------|-------|-------------|---------------------------|-------|---------|
| Hip 1 (Abduction/Adduction) | X-axis | Official ODrive | 0 | 0mm (0m) | ±45° (±0.79 rad) | 16:1 |
| Hip 2 (Flexion/Extension) | Y-axis | Makerbase ODrive | 0 | -40mm (-0.04m) | ±30° (±0.52 rad) | 16:1 |
| Knee (Flexion/Extension) | Y-axis | Makerbase ODrive | 1 | -390mm (-0.39m) | -90° to 0° (-1.57 to 0 rad) | 16:1 |
| Ball Foot | - | - | - | -740mm (-0.74m) | - | - |

Link lengths: L1=0.04m (Hip1→Hip2), L2=0.35m (Hip2→Knee), L3=0.35m (Knee→Foot), Total hip-to-foot: 0.74m.

### Future Requirements (Full Bipedal Robot - 2 Legs)
| Component | Quantity |
|-----------|----------|
| Official ODrive v3.6 | 2 |
| Makerbase ODrive M1 M22015 | 2 |
| D5065 Motor | 6 |
| AS5600 Encoder | 6 |
| TCA9548A I2C Mux | 2 |

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

## 3-DOF Joint Configuration (No Ankle)

| Joint | Rotation Axis | ODrive Axis | Z Offset | Range | Gearbox |
|-------|---------------|-------------|----------|-------|---------|
| Hip 1 (Abduction/Adduction) | X-axis | 0 | 0mm | ±45° (±0.79 rad) | 16:1 |
| Hip 2 (Flexion/Extension) | Y-axis | 0 (Makerbase) | -40mm | ±30° (±0.52 rad) | 16:1 |
| Knee (Flexion/Extension) | Y-axis | 1 (Makerbase) | -390mm | -90° to 0° (-1.57 to 0 rad) | 16:1 |
| Ball Foot | - | - | -740mm | - | - |

Link lengths: L1=0.04m, L2=0.35m, L3=0.35m, Total: 0.74m hip-to-foot.

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

### Encoder-based Homing (Virtual End Switches)
The AS5600 is an **absolute encoder** (12-bit, 0-4096 per revolution). Since each joint's mechanical range fits within one revolution (due to the 16:1 gearbox), the AS5600 can serve as a virtual end stop — eliminating the need for physical limit switches.

**Calibration (one-time, per joint):**
1. Manually move joint to mechanical limit A, record AS5600 raw → `limit_min`
2. Manually move joint to mechanical limit B, record AS5600 raw → `limit_max`
3. Store limits in a config file

**Homing (every startup):**
1. Read AS5600 raw value for each joint
2. Map to joint angle:
   ```
   joint_deg = (raw - limit_min) / (limit_max - limit_min) * range_deg + range_start
   ```
3. Convert to ODrive motor turns: `motor_turns = joint_deg / 360 * GEAR_RATIO`
4. Set ODrive position setpoint to current position — the robot knows its pose without moving

**Virtual end stops (during operation):**
- Before every move, clamp target position within recorded limits
- No physical limit switches needed

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

## Chinese ODrive (Makerbase M1 M22015) - Firmware Issue

The Makerbase ODrive clone controls 2 motors but is currently stuck in DFU mode.

| Parameter | Value |
|-----------|-------|
| Model | M1 M22015 |
| Motors Controlled | 2 (Axis 0 and Axis 1) |
| USB Device | None (stuck in DFU mode) |
| Firmware Status | ⚠️ Flash attempted - stuck in DFU mode |

### Issue Description

The board shows as `0483:df11` (STM32 BOOTLOADER) instead of `0483:5740` (ODrive normal mode).
Firmware flashes complete successfully but the board won't boot into normal mode.

### Firmware Attempted

1. **ODriveFirmware_v3.6-56V.hex** (Makerbase) - Flash succeeded, stuck in DFU
2. **ODriveFirmware_v3.6-56V.elf** (Official v0.5.6) - Flash failed (file too large)
3. **ODriveFirmware_v3.6-24V.hex** (Makerbase) - Flash succeeded, stuck in DFU

### Board Status (2026-04-27)

| Mode | lsusb Result | Status |
|------|--------------|--------|
| DFU | `0483:df11` | ✅ Detected |
| RUN | No device | ❌ Not detected |

**Board is bricked** - needs ST-Link programmer to recover or original Makerbase firmware.

### Firmware Files (2026-04-27)

Downloaded to `/home/pi/tfg/`:
- `ODriveFirmware_v3.6-56V.hex` - Makerbase firmware (649KB)
- `ODriveFirmware_v3.6-56V.elf` - Official ODrive v0.5.6 (6.4MB)

Board detected as **v3.4 or earlier** by odrivetool 0.5.4. Serial: `345331733432`

### Current Status

The Makerbase M1 M22015 board is **bricked**:
- Detected in DFU mode (`0483:df11`) ✅
- NOT detected in RUN mode ❌
- Board serial: `345331733432`
- Board detected as v3.4 hardware

### Recovery Options

1. **ST-Link Programmer** (required for recovery)
2. **Contact Makerbase Support** with serial number
3. **Source original firmware** from teacher
4. **Replace board** with new Makerbase or official ODrive

### Flashing Commands (Legacy - Board Bricked)

These commands are for reference only - the board is currently bricked and cannot be recovered without ST-Link.

```bash
# Install dfu-util
sudo apt-get install dfu-util

# Download firmware (if not already downloaded)
wget https://github.com/makerbase-mks/ODrive-MKS/raw/main/02_Makerbase%20ODrive%20related%20documents/ODriveFirmware_v3.6-56V.hex

# Flash Makerbase firmware (in DFU mode)
sudo dfu-util -a 0 -s 0x08000000:leave -D ODriveFirmware_v3.6-56V.hex

# Download official ODrive firmware
wget https://github.com/odriverobotics/ODrive/releases/download/fw-v0.5.6/ODriveFirmware_v3.6-56V.elf

# Flash official firmware
sudo dfu-util -a 0 -s 0x08000000:leave -D ODriveFirmware_v3.6-56V.elf

# After flash, toggle to RUN mode and check:
lsusb | grep 0483
# Should show 0483:5740 for normal ODrive mode
```

### Reference
- Makerbase GitHub: https://github.com/makerbase-mks/ODrive-MKS
- ODrive Official: https://github.com/odriverobotics/ODrive

## License

MIT License