# Project Context - tfg_biped_leg

**Last Updated**: 2026-04-13 (ODrive connected and testing!)

## Project Overview

- **Project Name**: tfg_biped_leg
- **Purpose**: Control a bipedal robot leg using ODrive motor controllers
- **Type**: Single leg prototype (3-DOF, expandable to full bipedal robot)
- **Hardware**: Raspberry Pi + ODrive v3.6 + AS5600 Encoders + TCA9548A Mux
- **Status**: ODrive connected ✅, Motor testing in progress ✅

---

## GitHub Repository

| Field | Value |
|-------|-------|
| **Username** | Josama-99 |
| **Repo URL** | https://github.com/Josama-99/tfg_biped_leg |
| **Status** | ✅ Synced with local |

---

## Architecture

### Current Setup: Pi + ODrive (USB)

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

### Control Stack

| Level | Component | Purpose |
|-------|-----------|---------|
| 1 | ODrive v3.6 | Closed-loop motor control (current, velocity, position) |
| 2 | USB | Communication Pi → ODrive |
| 3 | Raspberry Pi | High-level control, kinematics, trajectories |
| 4 | TCA9548A | I2C multiplexer for 3 encoders |
| 5 | AS5600 ×3 | Joint position sensing (after gearbox) |

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
| SSH Access | ed25519 | 2026-04-13 | jordisanchezmartori@gmail.com |
| Virtual Env | tfg_venv | 2026-04-13 | Python 3.12 |
| ROS2 Distro | Jazzy | 2026-04-13 | Ubuntu 24.04 |

---

## Hardware Configuration

### Current Test Setup (Single Motor)

| Component | Model | Value | Status |
|-----------|-------|-------|--------|
| ODrive | Official v3.6 | USB connected (/dev/ttyACM0) | ✅ Ready |
| Motor | D5065 | 270 KV | 🔌 Connected to Axis 1 |
| Axis | Axis 1 | Primary test | ✅ Working |
| Power | 12V | DC supply | ⚡ Powered |
| Serial | 35790927514957 | ODrive S/N | ✅ Connected |
| Calibration | axis1 | Auto-calibrated | ✅ Complete |

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

### Current Status: 🚧 Motor Testing in Progress

- [x] Project structure created ✅
- [x] All Python modules implemented ✅
- [x] ROS2 integration complete ✅
- [x] Initial commit created ✅
- [x] Git repository initialized ✅
- [x] SSH key setup ✅
- [x] Push to GitHub ✅
- [x] Code copied from USB (odrive_smapy) ✅
- [x] Test script created ✅
- [x] ODrive connected via USB ✅
- [x] Virtual environment set up ✅
- [x] ROS2 Jazzy installed ✅
- [x] Python dependencies installed ✅
- [x] ODrive calibration complete ✅
- [ ] Test encoder reading (future)
- [ ] Integrate encoder with motor control (future)
- [ ] Add more motors (expand to 3-DOF)

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
| Single Motor Test | ✅ | Script ready, ODrive connected |
| Interactive Test | ✅ | odrive_test.py |
| Unit Tests | ✅ | Kinematics tests |
| EncoderInterface (Base) | ✅ | Abstract base class |
| TCA9548A Driver | ✅ | I2C mux helper |
| PiAS5600Encoder | ✅ | Pi I2C implementation (future) |
| SerialEncoder | ✅ | Placeholder for future |
| EncoderManager | ✅ | Factory for multiple encoders |

---

## Pi Setup Completed

### Virtual Environment
```bash
cd ~/tfg/tfg_biped_leg
python3 -m venv tfg_venv
source tfg_venv/bin/activate
pip install -e .
pip install odrive numpy smbus2 pyyaml colorama matplotlib
```

### ODrive USB Permissions
```bash
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666"' | sudo tee /etc/udev/rules.d/50-odrive.rules
sudo udevadm control --reload-rules
```

### Running Tests
```bash
# Interactive test
sudo /home/pi/tfg/tfg_biped_leg/tfg_venv/bin/python3 /home/pi/tfg/odrive_test.py
```

---

## TODO

### High Priority
- [x] Test single motor with official ODrive v3.6 ✅
- [x] ODrive USB connected ✅
- [x] Calibration complete ✅
- [ ] Test encoder reading (future)
- [ ] Integrate encoder with motor control (future)

### Medium Priority
- [ ] Verify kinematics with physical leg
- [ ] Add 2 more motors (expand to 3-DOF)
- [ ] Implement closed-loop position control with encoder feedback

### Low Priority
- [ ] Create walking gait trajectories
- [ ] Test leg movement
- [ ] Expand to 2-leg (bipedal) configuration

---

## First Use Checklist

1. [x] Project setup (code downloaded)
2. [x] Set ODrive USB permissions
3. [ ] Enable I2C on Pi (`sudo raspi-config` → Interface → I2C)
4. [x] Install dependencies (pip install odrive numpy smbus2 pyyaml)
5. [x] Connect ODrive via USB
6. [x] Run motor calibration
7. [x] Test single motor
8. [ ] Connect TCA9548A and verify with `sudo i2cdetect -y 1`
9. [ ] Connect AS5600 encoders to mux channels (0=Hip, 1=Knee, 2=Ankle)
10. [ ] Test encoder reading (`python3 scripts/test_encoders.py`)
11. [ ] Integrate encoder feedback with motor control

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

## User Information

- **Platform**: Raspberry Pi (Ubuntu 24.04)
- **Username**: pi
- **Working Directory**: /home/pi/tfg/
- **GitHub**: Josama-99
- **Email**: jordisanchezmartori@gmail.com

---

## Change Log

### 2026-04-13
- ODrive v3.6 connected via USB
- Serial number: 35790927514957
- Virtual environment tfg_venv created
- ROS2 Jazzy installed
- Python dependencies (odrive, numpy, smbus2, pyyaml, colorama, matplotlib) installed
- odrive_test.py interactive script created
- Motor calibration successful (axis1)
- Motor testing in progress

### 2026-04-12
- Project initialized
- All source files created
- Git repository initialized with initial commit
- GitHub repo created (Josama-99/tfg_biped_leg)
- SSH keys generated (ed25519)
- GitHub push complete
- Code copied from USB (odrive_smapy-main)