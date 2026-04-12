# Project Context - tfg_biped_leg

**Last Updated**: 2026-04-12

## Project Overview

- **Project Name**: tfg_biped_leg
- **Purpose**: Control a bipedal robot leg using ODrive motor controllers
- **Type**: Single leg prototype (expandable to full bipedal robot)
- **Hardware**: Raspberry Pi + ODrive v3.6

## Key Decisions

| Decision | Value | Date |
|----------|-------|------|
| Project Name | tfg_biped_leg | 2026-04-12 |
| Robot Type | Single leg prototype | 2026-04-12 |
| Motors per Leg | 3-DOF (hip, knee, ankle) | 2026-04-12 |
| ODrive Model | ODrive v3.6 (36V) | 2026-04-12 |
| Programming Language | Python + ROS2 | 2026-04-12 |
| Communication | USB (initial), CAN (future) | 2026-04-12 |
| GitHub | New repo to be created | 2026-04-12 |

## Implementation Status (2026-04-12)

### Files Created

```
tfg_biped_leg/
├── PROJECT_CONTEXT.md      # This file - AI memory
├── README.md              # Project documentation
├── LICENSE                # MIT license
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore patterns
├── package.xml            # ROS2 package manifest
├── setup.py               # Python package setup
├── setup.cfg              # Package config
├── config/                # Motor configurations
│   ├── hip.yaml
│   ├── knee.yaml
│   └── ankle.yaml
├── launch/                # ROS2 launch files
│   └── bringup.launch.py
├── msg/                   # ROS2 message definitions
│   ├── JointAngles.msg
│   └── LegPose.msg
├── srv/                   # ROS2 service definitions
│   └── LegCommand.srv
├── tfg_biped_leg/         # Main Python package
│   ├── __init__.py
│   ├── odrive_driver.py   # ODrive USB communication
│   ├── leg_kinematics.py  # FK/IK for 3-DOF leg
│   ├── leg_controller.py  # ROS2 controller node
│   └── trajectory_generator.py
├── scripts/               # Utility scripts
│   ├── calibrate_motors.py
│   └── test_leg.py
├── tests/                 # Unit tests
│   └── test_kinematics.py
└── external/              # Git submodule placeholder
    └── README.md
```

### Implementation Complete
- [x] PROJECT_CONTEXT.md created
- [x] ROS2 package structure created
- [x] ODrive configuration files created
- [x] Python modules created (odrive_driver, kinematics, controller, trajectory)
- [x] ROS2 messages and services created
- [x] Launch files and scripts created
- [x] README, requirements.txt, .gitignore, LICENSE created
- [x] Git initialized, ready for GitHub upload

### Pending Tasks
- [ ] Clone private odrive_smapy repo as submodule (when accessible)
- [ ] Create GitHub repository
- [ ] Push to GitHub

## Motor Configuration

### Joint Definitions
| Joint | Axis | Description | Typical Range |
|-------|------|-------------|---------------|
| Hip | 0 | Yaw rotation (left/right) | ±45° (±0.79 rad) |
| Knee | 1 | Pitch rotation (flex/extend) | -90° to 0° (-1.57 to 0 rad) |
| Ankle | 2 | Pitch rotation (foot angle) | ±30° (±0.52 rad) |

### ODrive Configuration
- **Board**: ODrive v3.6
- **Motors**: 3x brushless motors (one per joint)
- **Encoders**: Hall sensors or ABI encoders (CPR: 8192)
- **Connection**: USB to Raspberry Pi

## Reference Repositories

### Private (not accessible yet)
- **odrive_smapy** by SergiMuac
  - URL: https://github.com/SergiMuac/odrive_smapy
  - Purpose: Motor control code
  - Status: Private, will clone as git submodule
  - **ACTION**: Clone into `external/odrive_smapy` when available

### Public Dependencies
- **ODrive**: https://github.com/odriverobotics/ODrive
  - Firmware v0.5.x compatible
- **ros_odrive**: https://github.com/odriverobotics/ros_odrive
  - ROS2 integration

## Important Notes

1. **ODrive v3.6 Setup**: Requires USB connection, run `sudo chmod 666 /dev/ttyACM0`
2. **Motor Calibration**: Must run calibration sequence before first use
3. **Private Repo**: Clone `odrive_smapy` into `external/` when accessible
4. **Testing**: Start with single joint tests before full leg integration

## User Information

- **Platform**: Raspberry Pi (Linux)
- **Username**: pi
- **Working Directory**: /home/pi/TFG

## TODO

- [ ] Clone private odrive_smapy repo
- [ ] Calibrate motors
- [ ] Test single joint control
- [ ] Implement full 3-DOF kinematics
- [ ] Create walking gait trajectories
- [ ] Test leg movement
- [ ] Expand to 2-leg (bipedal) configuration
