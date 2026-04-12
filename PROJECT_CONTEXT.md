# Project Context - tfg_biped_leg

**Last Updated**: 2026-04-12

## Project Overview

- **Project Name**: tfg_biped_leg
- **Purpose**: Control a bipedal robot leg using ODrive motor controllers
- **Type**: Single leg prototype (expandable to full bipedal robot)
- **Hardware**: Raspberry Pi + ODrive v3.6

## GitHub Repository

| Field | Value |
|-------|-------|
| **Username** | Josama-99 |
| **Repo URL** | https://github.com/Josama-99/tfg_biped_leg |
| **Status** | ✅ Pushed to GitHub |

## Key Decisions

| Decision | Value | Date |
|----------|-------|------|
| Project Name | tfg_biped_leg | 2026-04-12 |
| Robot Type | Single leg prototype | 2026-04-12 |
| Motors per Leg | 3-DOF (hip, knee, ankle) | 2026-04-12 |
| ODrive Model | ODrive v3.6 (36V) | 2026-04-12 |
| Programming Language | Python + ROS2 | 2026-04-12 |
| Communication | USB (initial), CAN (future) | 2026-04-12 |
| GitHub Setup | SSH keys | 2026-04-12 |

## Project Status

### Current Status: ✅ Pushed to GitHub

- [x] Project structure created
- [x] All Python modules implemented
- [x] ROS2 integration complete
- [x] Initial commit created (25 files)
- [x] Git repository initialized
- [x] SSH key setup ✅
- [x] Push to GitHub ✅
- [ ] Clone private odrive_smapy repo

### Last Changes (2026-04-12)

1. **Project initialized** - Created complete ROS2 package structure
2. **Files created**:
   - ODrive driver with USB communication
   - Forward/inverse kinematics for 3-DOF leg
   - Trajectory generator for walking gait
   - Motor calibration scripts
   - Unit tests for kinematics
   - Configuration files for hip, knee, ankle joints
3. **Git initialized** - Initial commit `cf37496`
4. **GitHub repo created** - https://github.com/Josama-99/tfg_biped_leg

## Implementation Summary

### Files Created (25 total)

```
tfg_biped_leg/
├── PROJECT_CONTEXT.md      # AI memory - LAST UPDATED 2026-04-12
├── README.md               # Project documentation
├── LICENSE                 # MIT license
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore patterns
├── package.xml             # ROS2 package manifest
├── setup.py                # Python package setup
├── setup.cfg               # Package config
├── config/                 # Motor configurations
│   ├── hip.yaml            # Hip joint config
│   ├── knee.yaml           # Knee joint config
│   └── ankle.yaml          # Ankle joint config
├── launch/                  # ROS2 launch files
│   └── bringup.launch.py   # Main bringup launch
├── msg/                    # ROS2 message definitions
│   ├── JointAngles.msg     # Joint angles message
│   └── LegPose.msg         # Leg pose message
├── srv/                    # ROS2 service definitions
│   └── LegCommand.srv      # Leg command service
├── tfg_biped_leg/          # Main Python package
│   ├── __init__.py
│   ├── odrive_driver.py    # ODrive USB communication
│   ├── leg_kinematics.py   # FK/IK for 3-DOF leg
│   ├── leg_controller.py   # ROS2 controller node
│   └── trajectory_generator.py
├── scripts/                # Utility scripts
│   ├── calibrate_motors.py # Motor calibration
│   └── test_leg.py        # Basic leg testing
├── tests/                  # Unit tests
│   └── test_kinematics.py
├── external/                # Git submodule placeholder
│   └── README.md
└── resource/               # ROS2 resource marker
    └── tfg_biped_leg
```

### Components Implemented

| Component | Status | Description |
|-----------|--------|-------------|
| ODrive Driver | ✅ | USB communication, motor control |
| Forward Kinematics | ✅ | Position from joint angles |
| Inverse Kinematics | ✅ | Joint angles from position |
| Trajectory Generator | ✅ | Walking gait patterns |
| ROS2 Integration | ✅ | Topics, services, launch files |
| Motor Calibration | ✅ | Standalone calibration script |
| Unit Tests | ✅ | Kinematics test suite |

## Motor Configuration

### Joint Definitions
| Joint | Axis | Description | Typical Range |
|-------|------|-------------|---------------|
| Hip | 0 | Yaw rotation (left/right) | ±45° (±0.79 rad) |
| Knee | 1 | Pitch rotation (flex/extend) | -90° to 0° (-1.57 to 0 rad) |
| Ankle | 2 | Pitch rotation (foot angle) | ±30° (±0.52 rad) |

### ODrive Configuration
- **Board**: ODrive v3.6 (36V)
- **Motors**: 3x brushless motors (one per joint)
- **Encoders**: Hall sensors or ABI encoders (CPR: 8192)
- **Connection**: USB to Raspberry Pi

## Reference Repositories

### Private (pending)
- **odrive_smapy** by SergiMuac
  - URL: https://github.com/SergiMuac/odrive_smapy
  - Purpose: Motor control code reference
  - Status: Private, clone as git submodule when accessible

### Public Dependencies
- **ODrive**: https://github.com/odriverobotics/ODrive
- **ros_odrive**: https://github.com/odriverobotics/ros_odrive

## Important Notes

1. **ODrive v3.6 Setup**: `sudo chmod 666 /dev/ttyACM0`
2. **First Use**: Run motor calibration before initial use
3. **Private Repo**: Clone `odrive_smapy` into `external/` when available
4. **Testing**: Start with single joint tests before full leg integration

## User Information

- **Platform**: Raspberry Pi (Linux)
- **Username**: pi
- **Working Directory**: /home/pi/TFG
- **GitHub**: Josama-99

## TODO

### High Priority
- [x] Set up SSH keys for GitHub ✅
- [x] Push to GitHub ✅
- [ ] Clone private odrive_smapy repo

### Medium Priority
- [ ] Calibrate motors
- [ ] Test single joint control
- [ ] Verify kinematics with physical leg

### Low Priority
- [ ] Implement full 3-DOF kinematics validation
- [ ] Create walking gait trajectories
- [ ] Test leg movement
- [ ] Expand to 2-leg (bipedal) configuration

## Change Log

### 2026-04-12
- Project initialized
- All source files created
- Git repository initialized with initial commit
- GitHub repo created (Josama-99/tfg_biped_leg)
- SSH keys generated (ed25519)
- **GitHub push complete** - All files pushed to https://github.com/Josama-99/tfg_biped_leg
