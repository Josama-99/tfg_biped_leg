# Project Context - tfg_biped_leg

**Last Updated**: 2026-04-27 (Created TFG_PROMPT.md for LaTeX document generation)

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

### Current Setup: Pi + Dual ODrive (USB)

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
       │ Motor    │     │ Motors   │      │ (Hip1)   │ (Hip2)   │ (Knee)   │
       └──────────┘     └──────────┘      └──────────┴──────────┴──────────┘
```

### Control Stack

| Level | Component | Purpose |
|-------|-----------|---------|
| 1 | Official ODrive v3.6 | 1 motor closed-loop control |
| 1 | Makerbase M1 M22015 | 2 motors closed-loop control |
| 2 | USB | Communication Pi → ODrives |
| 3 | Raspberry Pi | High-level control, kinematics, trajectories |
| 4 | TCA9548A | I2C multiplexer for 3 encoders |
| 5 | AS5600 ×3 | Joint position sensing (after gearbox) |

---

## Key Decisions

| Decision | Value | Date | Notes |
|----------|-------|------|-------|
| Project Name | tfg_biped_leg | 2026-04-12 | |
| Robot Type | Single leg prototype | 2026-04-12 | Expandable to bipedal |
| Motors per Leg | 3-DOF | 2026-04-12 | Hip 1, Hip 2, Knee (no ankle) |
| ODrive Model | Official v3.6 + Makerbase M1 M22015 | 2026-04-24 | Official: 1 motor, Makerbase: 2 motors |
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

### Current Test Setup (Dual ODrive, 3 Motors)

| Component | Model | Value | Status |
|-----------|-------|-------|--------|
| Official ODrive | ODrive v3.6 | USB connected (/dev/ttyACM0) | ✅ Ready |
| Makerbase ODrive | M1 M22015 | USB DFU mode (0483:df11) | ⚠️ Needs firmware fix |
| Motors | D5065 | 270 KV | 🔌 Connected |
| Power | 12V | DC supply | ⚡ Powered |
| Serial (Official) | 35790927514957 | ODrive S/N | ✅ Connected |

### Current Hardware (3-DOF Leg - 3 Motors)

| Component | Quantity | Model | Purpose |
|-----------|----------|-------|---------|
| Official ODrive v3.6 | 1 | Official v3.6 | 1 motor control |
| Makerbase ODrive M1 M22015 | 1 | Chinese clone | 2 motors control |
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

### Encoder-based Homing (Virtual End Switches)

The AS5600 absolute encoder replaces physical limit switches:

**Why it works:**
- AS5600 is absolute (remembers position after power cycle)
- 12-bit resolution = 4096 positions per revolution
- Each joint's mechanical range fits within one revolution (16:1 gearbox means 1 joint rev = 16 motor revs)
- So each AS5600 value maps uniquely to a joint angle with no ambiguity

**Procedure:**
1. **Calibration** (one-time): Manually move each joint to its mechanical limits, record AS5600 raw values
2. **Homing** (every startup): Read AS5600 → map to joint angle via stored limits → set ODrive position setpoint (robot knows its pose without moving)
3. **Virtual end stops** (runtime): Clamp all position targets within the recorded limits

---

## Joint Definitions

### 3-DOF Leg Configuration (No Ankle, Ball Foot)
Coordinate system (right leg): +X = Front, +Y = Left, +Z = Up. Fully extended leg points in -Z.

| Joint | Rotation Axis | ODrive | Motor Axis | Z Offset (from Hip Mount) | Encoder | Typical Range | Gearbox |
|-------|---------------|-------|------------|---------------------------|---------|---------------|---------|
| Hip 1 (Abduction/Adduction) | X-axis | Official ODrive | 0 | 0mm (0m) | AS5600 #1 | ±45° (±0.79 rad) | 16:1 |
| Hip 2 (Flexion/Extension) | Y-axis | Makerbase ODrive | 0 | -40mm (-0.04m) | AS5600 #2 | ±30° (±0.52 rad) | 16:1 |
| Knee (Flexion/Extension) | Y-axis | Makerbase ODrive | 1 | -390mm (-0.39m) | AS5600 #3 | -90° to 0° (-1.57 to 0 rad) | 16:1 |
| Ball Foot | - | - | - | -740mm (-0.74m) | - | - | - |

Link lengths: L1=0.04m (Hip1→Hip2), L2=0.35m (Hip2→Knee), L3=0.35m (Knee→Foot), Total hip-to-foot: 0.74m.

> **Note**: Joint assignments verified. Official ODrive controls 1 motor (Hip1), Makerbase controls 2 motors (Hip2 + Knee).

### Gearbox Conversion

```
joint_turns = motor_turns / 16  (16:1 reduction)
motor_turns = joint_turns × 16
```

---

## Project Status

### Current Status: 🚧 Makerbase Bricked - Continue with Official ODrive

- [x] Project structure created ✅
- [x] All Python modules implemented ✅
- [x] ROS2 integration complete ✅
- [x] Initial commit created ✅
- [x] Git repository initialized ✅
- [x] SSH key setup ✅
- [x] Push to GitHub ✅
- [x] Code copied from USB (odrive_smapy) ✅
- [x] Test script created ✅
- [x] Official ODrive connected via USB ✅
- [x] Virtual environment set up ✅
- [x] ROS2 Jazzy installed ✅
- [x] Python dependencies installed ✅
- [x] Official ODrive calibration complete ✅
- [x] Makerbase ODrive acquired ✅
- [x] Makerbase connected via USB (DFU mode) ✅
- [x] dfu-util installed ✅
- [x] Firmware downloaded ✅
- [x] Multiple firmware flash attempts - board bricked ⚠️
- [ ] Recover Makerbase ODrive (needs ST-Link)
- [x] Test encoder reading ✅ (2026-05-08)
- [ ] Integrate encoder with motor control (future)
- [ ] Add more motors (expand to 3-DOF)

### Components Status

| Component | Status | Notes |
|-----------|--------|-------|
| ODrive ODrive Class | ✅ | USB motor control (Official) |
| ODrive Enums | ✅ | State/error definitions |
| ODrive Driver (ROS2) | ✅ | ROS2 wrapper |
| Forward Kinematics | ✅ | Position from angles |
| Inverse Kinematics | ✅ | Angles from position |
| Trajectory Generator | ✅ | Walking gait patterns |
| ROS2 Integration | ✅ | Topics, services, launch |
| Motor Calibration | ✅ | Script ready |
| Single Motor Test | ✅ | Script ready, Official ODrive connected |
| Interactive Test | ✅ | odrive_test.py |
| Unit Tests | ✅ | Kinematics tests |
| EncoderInterface (Base) | ✅ | Abstract base class |
| TCA9548A Driver | ✅ | I2C mux helper |
| PiAS5600Encoder | ✅ | Pi I2C implementation (working on ch5) |
| SerialEncoder | ✅ | Placeholder for future |
| EncoderManager | ✅ | Factory for multiple encoders |
| Makerbase ODrive Support | 🔧 In Progress | Needs testing |

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
- [x] Official ODrive USB connected ✅
- [x] Calibration complete (Official ODrive) ✅
- [ ] Connect Makerbase ODrive via USB
- [ ] Test Makerbase connection and verify device path
- [ ] Check Makerbase firmware version
- [x] Test encoder reading ✅
- [ ] Integrate encoder with motor control (future)

### Medium Priority
- [ ] Verify kinematics with physical leg
- [ ] Add motors and expand to 3-DOF
- [ ] Implement closed-loop position control with encoder feedback

### Low Priority
- [ ] Create walking gait trajectories
- [ ] Test leg movement
- [ ] Expand to 2-leg (bipedal) configuration

---

## First Use Checklist

1. [x] Project setup (code downloaded)
2. [x] Set ODrive USB permissions
 3. [x] Enable I2C on Pi (`sudo raspi-config` → Interface → I2C) ✅
4. [x] Install dependencies (pip install odrive numpy smbus2 pyyaml)
5. [x] Connect Official ODrive via USB
6. [x] Run motor calibration
7. [x] Test single motor
8. [ ] Connect Makerbase ODrive via USB
9. [ ] Verify Makerbase device path (dmesg | grep tty)
10. [ ] Test Makerbase connection
11. [x] Connect TCA9548A and verify with `sudo i2cdetect -y 1` ✅
12. [x] Connect AS5600 encoder to mux channel 5 ✅
13. [x] Test encoder reading (`python3 scripts/test_encoders.py --channels 5`) ✅
14. [ ] Integrate encoder feedback with motor control

---

## Makerbase ODrive M1 M22015 - Status: BRICKED

The Chinese Makerbase ODrive M1 M22015 clone is **bricked** and currently unusable. All firmware flash attempts have failed to bring the board into normal operation mode.

| Parameter | Value |
|-----------|-------|
| Model | M1 M22015 |
| Manufacturer | Makerbase |
| Motors Controlled | 2 (Axis 0 and Axis 1) |
| USB Device (DFU) | `0483:df11` detected ✅ |
| USB Device (RUN) | No device detected ❌ |
| Firmware Status | ⚠️ BRICKED - needs ST-Link recovery |

### USB Detection by Mode

| Switch Mode | lsusb | Status |
|-------------|-------|--------|
| DFU | `0483:df11` (STM32 BOOTLOADER) | ✅ Detected |
| RUN | No device | ❌ NOT detected |

### Firmwares Tried

| Firmware | Size | Result |
|----------|------|--------|
| ODriveFirmware_v3.6-56V.hex (Makerbase) | 649KB | Flash OK, no RUN mode |
| ODriveFirmware_v3.6-56V.elf (Official v0.5.6) | 6.4MB | Flash failed (file too large) |
| ODriveFirmware_v3.6-24V.hex (Makerbase) | 649KB | Flash OK, no RUN mode |

### Root Cause

- Board detected as v3.4 hardware (odrivetool 0.5.4)
- Official .elf firmware too large for board flash memory
- .hex firmware flashes successfully but board won't boot into normal mode
- Bootloader may be corrupted or incompatible with available firmware

### Recovery Options

1. **ST-Link Programmer** - Required to recover (not available)
2. **Contact Makerbase Support** - Provide serial `345331733432`
3. **Source Original Firmware** - Teacher doesn't remember which firmware
4. **Replace Board** - Order new Makerbase M1 M22015 or official ODrive

### Current Workaround

Continue development with official ODrive v3.6 (1 motor).
Makerbase board on hold until recovery solution found.

See also: https://github.com/makerbase-mks/ODrive-MKS

### Resources
- ODrive v0.5.6 `odrivetool` docs (firmware update & troubleshooting): https://docs.odriverobotics.com/v/0.5.6/odrivetool.html#troubleshooting

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
- **ODrive v0.5.6 Firmware Update Docs**: https://docs.odriverobotics.com/v/0.5.6/odrivetool.html#device-firmware-update
  - Troubleshooting, forcing DFU mode, alternative DFU tools, ST-Link flashing

---

## User Information

- **Platform**: Raspberry Pi (Ubuntu 24.04)
- **Username**: pi
- **Working Directory**: /home/pi/tfg/
- **GitHub**: Josama-99
- **Email**: jordisanchezmartori@gmail.com

---

## Change Log

### 2026-05-08
- Fixed AS5600 CORDIC toggle (215° chip-level jumps) → median-3 + jump threshold filter
- Fixed periodic I2C bursts (~400 count drops every ~15s) → same filter catches both
- Encoder readings now stable and clean
- Recordings saved to recordings/ with timestamped files

### 2026-05-08 (earlier)
- TCA9548A I2C multiplexer verified working
- AS5600 encoder tested on mux channel 5
- Live plotting script created (plot_encoder.py)
- Encoder reads angle + magnet status successfully via smbus2
- Encoder skips detected (likely magnet misalignment - needs investigation)

### 2026-04-27 (continued)
- Board remains bricked: detected in DFU mode but not in RUN mode
- Tried firmware variants: ODriveFirmware_v3.6-56V.hex, ODriveFirmware_v3.6-56V.elf, ODriveFirmware_v3.6-24V.hex
- .elf files too large for board flash memory
- .hex files flash successfully but board won't boot into normal mode
- Board switch toggles between DFU/RUN but RUN mode shows no USB device
- **Board needs ST-Link programmer to recover** or replacement firmware from Makerbase
- Teacher does not have original firmware
- Next step: Contact Makerbase support or order replacement board

### 2026-04-27
- Acquired Makerbase M1 M22015 Chinese ODrive clone
- Updated project to use dual ODrive configuration:
  - Official ODrive v3.6: 1 motor (Hip - TBD)
  - Makerbase ODrive: 2 motors (Hip 2 + Knee - TBD)
- Documentation updated to reflect dual ODrive setup
- Makerbase firmware flashing attempts:
  - Installed dfu-util
  - Downloaded MKS ODrive_S-fw-v0.5.1 firmware
  - Downloaded ODriveFirmware_v3.6-56V firmware
  - Flash of MKS firmware succeeded but board stuck in DFU mode
  - Flash of 56V firmware succeeded but board stuck in DFU mode
- Board persists in DFU mode (0483:df11) instead of normal mode (0483:5740)
- Next step: Get original working firmware from teacher

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