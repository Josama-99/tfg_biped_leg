# Project Context - tfg_biped_leg

**Last Updated**: 2026-04-12 (Encoder Implementation Complete)

## Project Overview

- **Project Name**: tfg_biped_leg
- **Purpose**: Control a bipedal robot leg using ODrive motor controllers
- **Type**: Single leg prototype (3-DOF, expandable to full bipedal robot)
- **Hardware**: Raspberry Pi + ODrive v3.6 + AS5600 Encoders + TCA9548A Mux

## GitHub Repository

| Field | Value |
|-------|-------|
| **Username** | Josama-99 |
| **Repo URL** | https://github.com/Josama-99/tfg_biped_leg |
| **Status** | ✅ Pushed to GitHub |

---

## Architecture

### Selected Architecture: Pi-Only with I2C Multiplexer

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Raspberry Pi                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ ODrive USB   │  │ I2C Mux      │  │ Control Logic            │ │
│  │ (Motor Ctrl) │  │ (Encoders)   │  │ (Position Commands)      │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘ │
└─────────┼──────────────────┼────────────────────┼──────────────────┘
          │                  │                    │
          ▼                  ▼                    │
    ┌──────────┐      ┌──────────┐                │
    │ ODrive   │      │TCA9548A  │                │
    │ v3.6     │      │I2C Mux   │◄───────────────┘
    └────┬─────┘      └────┬─────┘
         │                 │
         ▼                 ▼
    ┌──────────┐     ┌──────────┬──────────┬──────────┐
    │ D5065    │     │ AS5600   │ AS5600   │ AS5600   │
    │ Motor    │     │ (Hip)    │ (Knee)   │ (Ankle)  │
    └──────────┘     └──────────┴──────────┴──────────┘
```

### Control Stack

| Level | Component | Purpose |
|-------|-----------|---------|
| 1 | ODrive v3.6 | Closed-loop motor control (current, velocity, position) |
| 2 | USB | Communication Pi → ODrive |
| 3 | Raspberry Pi | High-level control, kinematics, trajectories |
| 4 | TCA9548A | I2C multiplexer for 3 encoders |
| 5 | AS5600 ×3 | Joint position sensing (after gearbox) |

### Why This Architecture?

- **Simple**: No extra microcontroller needed
- **Robust**: ODrive handles real-time motor control
- **Scalable**: Easy to add more ODrives for full robot
- **Tested**: Based on odrive_smapy approach

---

## Key Decisions

| Decision | Value | Date | Notes |
|----------|-------|------|-------|
| Project Name | tfg_biped_leg | 2026-04-12 | |
| Robot Type | Single leg prototype | 2026-04-12 | Expandable to bipedal |
| Motors per Leg | 3-DOF | 2026-04-12 | Hip, knee, ankle |
| ODrive Model | Official v3.6 | 2026-04-12 | + Clone for future |
| Encoder Type | AS5600 | 2026-04-12 | Magnetic, 12-bit |
| I2C Mux | TCA9548A | 2026-04-12 | Needed for 3 encoders |
| Control Method | Pi direct | 2026-04-12 | No Teensy |
| Communication | USB (ODrive) + I2C (Encoders) | 2026-04-12 | |
| Programming | Python | 2026-04-12 | + ROS2 structure |

---

## Hardware Configuration

### Current Test Setup (Single Motor)

| Component | Model | Value | Status |
|-----------|-------|-------|--------|
| ODrive | Official v3.6 | USB connected | ✅ Ready |
| Motor | D5065 | 270 KV | ✅ Ready |
| Axis | Axis 1 | Primary test | ✅ Ready |
| Power | 12V | DC supply | ⚡ Powered |
| Encoder CPR | 8192 | Built-in | ✅ Working |

### Future Hardware (3-DOF Leg)

| Component | Quantity | Model | Purpose |
|-----------|----------|-------|---------|
| ODrive v3.6 | 3 | Official or Clone | Motor control |
| Motor | 3 | D5065 270KV | Actuation |
| AS5600 | 3 | Magnetic encoder | Joint position |
| TCA9548A | 1 | I2C Mux | Encoder multiplexing |
| Raspberry Pi | 1 | Any | Main controller |

### Motor Specifications (D5065 270KV)

| Parameter | Value |
|-----------|-------|
| KV Rating | 270 RPM/V |
| Pole Pairs | 7 |
| Torque Constant | 8.27/270 Nm/A (≈0.0306 Nm/A) |
| Encoder CPR | 8192 (built-in) |
| Current Limit | 30A |
| Velocity Limit | 5 turn/s |

### AS5600 Encoder Specifications

| Parameter | Value |
|-----------|-------|
| Type | Magnetic rotary encoder |
| Resolution | 12-bit (4096 positions/rev) |
| I2C Address | 0x36 (all units same) |
| Communication | I2C (requires mux for multiple) |

### TCA9548A I2C Multiplexer

| Parameter | Value |
|-----------|-------|
| Channels | 8 independent I2C buses |
| I2C Address | 0x70 (default) |
| Purpose | Enable multiple AS5600 on one bus |

---

## Joint Definitions

### 3-DOF Leg Configuration

| Joint | Motor Axis | Encoder | Typical Range | Gearbox |
|-------|------------|---------|---------------|---------|
| Hip | 0 | AS5600 #1 | ±45° (±0.79 rad) | 16:1 |
| Knee | 1 | AS5600 #2 | -90° to 0° (-1.57 to 0) | 16:1 |
| Ankle | 2 | AS5600 #3 | ±30° (±0.52 rad) | 16:1 |

### Gearbox Conversion

```
joint_turns = motor_turns / 16  (16:1 reduction)
motor_turns = joint_turns × 16
```

---

## Project Status

### Current Status: 🚧 Encoder Implementation Complete, Motor Test Pending

- [x] Project structure created
- [x] All Python modules implemented
- [x] ROS2 integration complete
- [x] Initial commit created
- [x] Git repository initialized
- [x] SSH key setup
- [x] Push to GitHub
- [x] Code copied from USB (odrive_smapy)
- [x] Test script created
- [ ] Test single motor with ODrive
- [x] I2C mux + AS5600 code implemented ✅
- [ ] Test encoder reading
- [ ] Integrate encoder with motor control

### Components Status

| Component | Status | Notes |
|-----------|--------|-------|
| ODrive IOdrive Class | ✅ | USB motor control |
| ODrive Enums | ✅ | State/error definitions |
| ODrive Driver (ROS2) | ✅ | ROS2 wrapper |
| Forward Kinematics | ✅ | Position from angles |
| Inverse Kinematics | ✅ | Angles from position |
| Trajectory Generator | ✅ | Walking gait patterns |
| ROS2 Integration | ✅ | Topics, services, launch |
| Motor Calibration | ✅ | Script ready |
| Single Motor Test | ✅ | Script ready |
| Unit Tests | ✅ | Kinematics tests |
| EncoderInterface (Base) | ✅ | Abstract base class |
| TCA9548A Driver | ✅ | I2C mux helper |
| PiAS5600Encoder | ✅ | Pi I2C implementation |
| SerialEncoder | ✅ | Placeholder for future |
| EncoderManager | ✅ | Factory for multiple encoders |
| Encoder Config | ✅ | YAML configuration |
| Encoder Test Script | ✅ | scripts/test_encoders.py |

---

## Files Created (35+ files)

```
tfg_biped_leg/
├── PROJECT_CONTEXT.md          # AI memory - UPDATED 2026-04-12
├── README.md                  # Project documentation
├── LICENSE                    # MIT license
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore patterns
├── package.xml                # ROS2 package manifest
├── setup.py                   # Python package setup
├── setup.cfg                  # Package config
│
├── config/                    # Motor configurations
│   ├── hip.yaml               # Hip joint config
│   ├── knee.yaml              # Knee joint config
│   ├── ankle.yaml             # Ankle joint config
│   ├── my_config.json         # D5065 motor config
│   └── encoder.yaml           # AS5600 encoder config (NEW)
│
├── launch/                     # ROS2 launch files
│   └── bringup.launch.py      # Main bringup launch
│
├── msg/                       # ROS2 message definitions
│   ├── JointAngles.msg        # Joint angles message
│   └── LegPose.msg            # Leg pose message
│
├── srv/                       # ROS2 service definitions
│   └── LegCommand.srv         # Leg command service
│
├── tfg_biped_leg/             # Main Python package
│   ├── __init__.py
│   ├── odrive_interface.py    # IOdrive class (from odrive_smapy)
│   ├── odrive_enums.py        # ODrive enums (from odrive_smapy)
│   ├── odrive_driver.py       # ODrive USB communication
│   ├── leg_kinematics.py      # FK/IK for 3-DOF leg
│   ├── leg_controller.py      # ROS2 controller node
│   └── trajectory_generator.py # Walking gait patterns
│
├── scripts/                    # Utility scripts
│   ├── calibrate_motors.py    # Motor calibration
│   ├── test_leg.py           # Basic leg testing
│   ├── test_single_motor.py  # Single motor test
│   ├── test_encoders.py      # Encoder test (NEW)
│   └── odrive_hw_interface.py # Hardware interface (from odrive_smapy)
│
├── src/                       # Low-level drivers
│   ├── __init__.py           # Package init (NEW)
│   ├── encoder_interface.py   # Abstract base class (NEW)
│   ├── tca9548a.py           # TCA9548A driver (NEW)
│   ├── pi_as5600_encoder.py  # Pi AS5600 implementation (NEW)
│   ├── serial_encoder.py      # Serial placeholder for future (NEW)
│   └── encoder_manager.py     # Multi-encoder manager (NEW)
│
├── tests/                     # Unit tests
│   └── test_kinematics.py
│
├── external/                  # Git submodule placeholder
│   └── README.md
│
└── resource/                 # ROS2 resource marker
    └── tfg_biped_leg
```

---

## Encoder Architecture

### Modular Design (Pi or Microcontroller)

The encoder system uses an abstraction layer that allows switching between implementations without rewriting high-level code:

```
┌─────────────────────────────────────────────────────────────┐
│                    leg_controller.py                          │
│                  (Uses EncoderInterface)                      │
│                                                              │
│   get_joint_angle() ───────▶ encoder.read_angle()           │
│   set_zero()         ───────▶ encoder.zero()               │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
      ┌────────────┐  ┌────────────┐  ┌────────────┐
      │PiAS5600   │  │SerialEnc  │  │CANEncoder │
      │ Encoder   │  │ (Future)  │  │ (Future)  │
      │ (I2C/Mux) │  │ (UART)    │  │           │
      └────────────┘  └────────────┘  └────────────┘
```

### Current Implementation (Pi I2C)

```
Raspberry Pi        TCA9548A Mux       AS5600 Encoders
     │                    │                   │
     │ I2C (SDA/SCL)     │                   │
     │───────────────────▶│ Channel 0 ────────▶│ Hip Encoder
     │                    │ Channel 1 ────────▶│ Knee Encoder
     │                    │ Channel 2 ────────▶│ Ankle Encoder
```

### Future: Microcontroller (Serial)

```
Microcontroller        Raspberry Pi        ODrive
     │                    │                   │
     │ I2C (own)         │                   │
     │──────▶ AS5600s     │ Serial            │ USB
     │                    │──────▶ ODrive ◀───┘
     │                    │
     │ Position Data      │
     └────────────────────┘
```

### Usage Example

```python
# Current (Pi)
from src import EncoderManager

manager = EncoderManager(encoder_type='pi', config={
    'hip': {'channel': 0},
    'knee': {'channel': 1},
    'ankle': {'channel': 2}
})
angles = manager.read_all()

# Future (Microcontroller) - just change config
manager = EncoderManager(encoder_type='serial', config={
    'hip': {'port': '/dev/ttyUSB0'},
    ...
})
```

### Test Commands

```bash
# Scan I2C bus
python3 scripts/test_encoders.py --scan

# Test TCA9548A
python3 scripts/test_encoders.py --mux

# Test all encoders
python3 scripts/test_encoders.py --encoders

# Continuous read (10 seconds)
python3 scripts/test_encoders.py --continuous 10
```

---

## TODO

### High Priority
- [ ] Test single motor with official ODrive v3.6
- [x] I2C mux driver (TCA9548A) ✅
- [x] AS5600 encoder driver ✅
- [ ] Test encoder reading
- [ ] Integrate encoder with motor control
- [ ] Test Chinese ODrive clone (M1 M22015)

### Medium Priority
- [ ] Calibrate motors
- [ ] Verify kinematics with physical leg
- [ ] Add 2 more motors (expand to 3-DOF)
- [ ] Implement closed-loop position control with encoder feedback

### Low Priority
- [ ] Create walking gait trajectories
- [ ] Test leg movement
- [ ] Expand to 2-leg (bipedal) configuration
- [ ] Switch to microcontroller (SerialEncoder placeholder ready)
- [ ] Clone private odrive_smapy repo

---

## Important Notes

### ODrive Setup
```bash
# USB permissions
sudo chmod 666 /dev/ttyACM0

# Or create permanent udev rule
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666"' | sudo tee /etc/udev/rules.d/50-odrive.rules
sudo udevadm control --reload-rules
```

### I2C Setup on Pi
```bash
# Enable I2C in raspi-config
sudo raspi-config
# → Interface Options → I2C → Enable

# Install i2c tools
sudo apt install i2c-tools python3-smbus

# Check devices
sudo i2cdetect -y 1
```

### AS5600 Address Issue
All AS5600 encoders share address **0x36**. Must use TCA9548A I2C multiplexer to read multiple encoders.

### First Use Checklist
1. [x] Project setup (code downloaded)
2. [ ] Set ODrive USB permissions (`sudo chmod 666 /dev/ttyACM0`)
3. [ ] Enable I2C on Pi (`sudo raspi-config` → Interface → I2C)
4. [ ] Install dependencies (`pip install smbus2 pyyaml odrive numpy`)
5. [ ] Connect TCA9548A and verify with `sudo i2cdetect -y 1`
6. [ ] Connect AS5600 encoders to mux channels (0=Hip, 1=Knee, 2=Ankle)
7. [ ] Test encoder reading (`python3 scripts/test_encoders.py`)
8. [ ] Run motor calibration (`python3 scripts/calibrate_motors.py`)
9. [ ] Test single motor (`python3 scripts/test_single_motor.py`)
10. [ ] Integrate encoder feedback with motor control

---

## Reference Repositories

### Private (pending)
- **odrive_smapy** by SergiMuac
  - URL: https://github.com/SergiMuac/odrive_smapy
  - Purpose: Motor control code reference
  - Status: Private, clone as git submodule when accessible

### Public Dependencies
- **ODrive**: https://github.com/odriverobotics/ODrive
  - Firmware v0.5.x compatible
- **ros_odrive**: https://github.com/odriverobotics/ros_odrive
  - ROS2 integration
- **Makerbase ODrive**: https://github.com/makerbase-mks/ODrive-MKS
  - Chinese clone firmware

---

## Chinese ODrive Clone Notes

### M1 M22015 (Makerbase)
- **Status**: Not yet tested
- **Device Name**: May appear as `dev0` instead of `odrv0`
- **Compatibility**: Works with official firmware (mostly)
- **Warning**: May show "board not genuine" - usually still works
- **Firmware**: Can flash official 0.5.x via ST-Link if needed

---

## User Information

- **Platform**: Raspberry Pi (Linux)
- **Username**: pi
- **Working Directory**: /home/pi/TFG
- **GitHub**: Josama-99

---

## Change Log

### 2026-04-12
- Project initialized
- All source files created
- Git repository initialized with initial commit
- GitHub repo created (Josama-99/tfg_biped_leg)
- SSH keys generated (ed25519)
- GitHub push complete
- Code copied from USB (odrive_smapy-main):
  - odrive_interface.py → tfg_biped_leg/
  - odrive_enums.py → tfg_biped_leg/
  - odrive_hw_interface.py → scripts/
  - my_config.json → config/
- Test script created: scripts/test_single_motor.py

### 2026-04-12 (Architecture Update)
- Architecture finalized: Pi + ODrive + TCA9548A + AS5600
- Added complete hardware specifications
- Added AS5600 encoder details
- Added TCA9548A multiplexer info
- Added I2C setup instructions
- Added joint definitions with gearbox conversion
- Updated TODO list with encoder integration tasks
  - Added source directory structure for new drivers

### 2026-04-12 (Encoder Implementation)
- Modular encoder architecture implemented:
  - encoder_interface.py: Abstract base class
  - tca9548a.py: TCA9548A I2C multiplexer driver
  - pi_as5600_encoder.py: Pi I2C implementation
  - serial_encoder.py: Serial placeholder for future microcontroller
  - encoder_manager.py: Factory for multiple encoders
  - encoder.yaml: Configuration file
  - test_encoders.py: Test script
- Abstraction layer allows switching between Pi and microcontroller
- Error handling: EncoderError, EncoderTimeoutError, EncoderNotFoundError
- ROS2 compatible: EncoderManager integrates with leg_controller
