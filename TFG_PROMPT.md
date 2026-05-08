# Prompt for TFG LaTeX Document Generation

## Context
You are helping a university student (TFG - Trabajo de Fin de Grado / Final Degree Project) create a LaTeX document (memoria) for a bipedal robot leg control project. Below is all the project information.

---

## Project Title (Suggestion)
Control de una pierna robótica bípeda de 3-DOF usando controladores ODrive

(Control of a 3-DOF bipedal robot leg using ODrive motor controllers)

## Student Information
- **GitHub**: https://github.com/Josama-99
- **Email**: jordisanchezmartori@gmail.com
- **Platform**: Raspberry Pi (Ubuntu 24.04)
- **Hostname**: robopi

---

## Project Overview

**Purpose**: Control a bipedal robot leg using ODrive motor controllers  
**Type**: Single leg prototype (3-DOF, expandable to full bipedal robot)  
**Status**: Official ODrive working, Makerbase ODrive needs firmware fix

### Hardware Components

| Component | Model | Quantity | Purpose |
|-----------|-------|----------|---------|
| Official ODrive | v3.6 | 1 | 1 motor control |
| Makerbase ODrive | M1 M22015 | 1 | 2 motors control (Chinese clone) |
| Motor | D5065 270KV | 3 | Actuation |
| Encoder | AS5600 | 3 | Magnetic joint position sensing |
| I2C Mux | TCA9548A | 1 | Encoder multiplexing |
| Main Controller | Raspberry Pi | 1 | High-level control |

### Component Mass Table (Per Leg, 8kg Total Robot)
| Component | Qty (per leg) | Mass (per unit, g) | Total Mass (per leg, g) | Material/Model |
|-----------|----------------|---------------------|-------------------------|----------------|
| Brushless Motor (D5065 270KV) | 3 | 420 | 1260 | D5065 270kv |
| Bearing (680 series) | 15 | 10 | 150 | 10x19x5mm |
| 2GT Belt (10×200mm) | 6 | 8 | 48 | Polyurethane |
| Magnetic Encoder (AS5600) | 3 | 2 | 6 | AS5600 + Magnet |
| ODrive v3.6 Controller | 2 | 50 | 100 | Official/Makerbase |
| Raspberry Pi CM4 | 0.5 | 120 | 60 | Split between legs |
| LiPo 6S Battery | 0.5 | 620 | 310 | Split between legs |
| 3D Printed PETG Structure | 1 | 900 | 900 | PETG Filament |
| M3/M4 Bolts | 25 | 1 | 25 | Stainless Steel |
| Wiring/Connectors | 1 | 50 | 50 | Misc |
| **Total Per Leg** | - | - | **2909g (~2.9kg)** | - |
| **Payload (Torso/Electronics)** | - | 1100g | 1100g | - |
| **Total Per Leg (with Payload)** | - | - | **4kg** | Matches 8kg total |

### Motor Specifications (D5065 270KV)

| Parameter | Value |
|-----------|-------|
| KV Rating | 270 RPM/V |
| Pole Pairs | 7 |
| Torque Constant | 8.27/270 Nm/A (≈0.0306 Nm/A) |
| Encoder CPR | 8192 |
| Current Limit | 30A |
| Velocity Limit | 5 turn/s |

### Encoder Specifications (AS5600)

| Parameter | Value |
|-----------|-------|
| Type | Magnetic rotary encoder |
| Resolution | 12-bit (4096 positions/rev) |
| I2C Address | 0x36 |
| Communication | I2C (requires TCA9548A mux for multiple) |

### I2C Multiplexer (TCA9548A)

| Parameter | Value |
|-----------|-------|
| Channels | 8 independent I2C buses |
| I2C Address | 0x70 |

### Joint Configuration (3-DOF Leg, No Ankle)
Coordinate system (right leg): +X = Front, +Y = Left, +Z = Up. Fully extended leg points in -Z.
| Joint | Rotation Axis | ODrive | ODrive Axis | Z Offset (from Hip Mount) | Range | Gearbox | Encoder |
|-------|---------------|-------|-------------|---------------------------|-------|---------|---------|
| Hip 1 (Abduction/Adduction) | X-axis | Official ODrive | 0 | 0mm (0m) | ±45° (±0.79 rad) | 16:1 | AS5600 #1 |
| Hip 2 (Flexion/Extension) | Y-axis | Makerbase ODrive | 0 | -40mm (-0.04m) | ±30° (±0.52 rad) | 16:1 | AS5600 #2 |
| Knee (Flexion/Extension) | Y-axis | Makerbase ODrive | 1 | -390mm (-0.39m) | -90° to 0° (-1.57 to 0 rad) | 16:1 | AS5600 #3 |
| Ball Foot | - | - | - | -740mm (-0.74m) | - | - | - |

Link lengths: L1=0.04m (Hip1→Hip2), L2=0.35m (Hip2→Knee), L3=0.35m (Knee→Foot), Total hip-to-foot: 0.74m.

---

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

## Software Architecture

### Technology Stack
- **Programming Language**: Python 3.12
- **Robot Operating System**: ROS2 Jazzy
- **Motor Control**: ODrive (USB)
- **Encoder Interface**: I2C (via smbus2)
- **Virtual Environment**: tfg_venv

### Key Python Modules

1. **odrive_interface.py** (`tfg_biped_leg/`)
   - `IOdrive` class for ODrive communication
   - Supports torque, position, and velocity control modes
   - Calibration and configuration management
   - Live encoder plotting with matplotlib
   - Default motor config: current_limit=30A, vel_limit=5 turn/s, pole_pairs=7

2. **leg_kinematics.py** (`tfg_biped_leg/`)
   - `LegKinematics` class
   - Forward kinematics (angles → position)
   - Inverse kinematics (position → angles)
   - Jacobian matrix calculation
   - Joint limits checking
   - Foot trajectory generation
   - Default leg lengths: L1=0.3m, L2=0.3m

3. **trajectory_generator.py** (`tfg_biped_leg/`)
   - `TrajectoryGenerator` class
   - Step trajectory generation
   - Walking cycle generation
   - Circular trajectory generation
   - Trajectory smoothing
   - Trajectory interpolation

4. **odrive_driver.py** (ROS2 wrapper)

### ROS2 Integration
- Topics, services, launch files
- Package structure following ROS2 conventions

### Scripts
- `odrive_test.py` - Interactive test menu
- `test_single_motor.py` - Single motor test
- `calibrate_motors.py` - Motor calibration

---

## Key Technical Concepts to Cover

### 1. ODrive Motor Controller
- What is ODrive and how it works
- FOC (Field Oriented Control) for BLDC motors
- USB communication protocol
- Calibration process
- Control modes (torque, velocity, position)

### 2. Kinematics
- Forward kinematics equations
- Inverse kinematics using law of cosines
- 3-DOF leg geometry
- Jacobian matrix for velocity mapping

### 3. Trajectory Generation
- Walking gait patterns
- Bezier curves for smooth motion
- Step height/length parameters

### 4. I2C and Encoders
- AS5600 magnetic encoder working principle
- I2C protocol
- TCA9548A multiplexer for multi-sensor reading
- Position sensing after gearbox

### 5. ROS2 Integration
- Why ROS2 for robot control
- Topics and services architecture
- Launch files

---

## Reference Repositories

| Repository | URL | Purpose |
|------------|-----|---------|
| Project Repo | https://github.com/Josama-99/tfg_biped_leg | Main project code |
| ODrive (Official) | https://github.com/odriverobotics/ODrive | Firmware v0.5.x |
| ros_odrive | https://github.com/odriverobotics/ros_odrive | ROS2 integration |
| Makerbase ODrive | https://github.com/makerbase-mks/ODrive-MKS | Chinese clone firmware |
| odrive_smapy | https://github.com/SergiMuac/odrive_smapy | Private motor control reference |

---

## Current Issues (as of 2026-04-27)

### Makerbase ODrive Firmware Issue
The Makerbase ODrive clone (M1 M22015) is stuck in DFU mode:
- Shows as `0483:df11` instead of `0483:5740`
- Board serial: `345331733432`
- Board detected as v3.4 or earlier
- Multiple firmware flash attempts failed

### Firmware Files Downloaded
- `/home/pi/tfg/ODriveFirmware_v3.6-56V.hex` (Makerbase, 649KB)
- `/home/pi/tfg/ODriveFirmware_v3.6-56V.elf` (Official ODrive v0.5.6, 6.4MB)

---

## Future Work
- [ ] Fix Makerbase ODrive firmware
- [x] Test encoder reading ✅
- [ ] Integrate encoder feedback with motor control
- [ ] Verify kinematics with physical leg
- [ ] Add more motors (expand to 3-DOF)
- [ ] Test leg movement
- [ ] Expand to 2-leg (bipedal) configuration

---

## Suggested LaTeX Document Structure

```
1. Introducción
   - Motivación
   - Objetivos del proyecto
   - Estado del arte

2. Marco Teórico
   - Motores BLDC y control FOC
   - Controladores ODrive
   - Cinemática de piernas robóticas
   - Generadores de trayectorias

3. Diseño del Sistema
   - Hardware seleccionado
   - Diagrama de arquitectura
   - Selección de componentes

4. Implementación
   - Estructura del software
   - Comunicación con ODrive
   - Cinemática directa e inversa
   - Generación de trayectorias
   - Integración ROS2

5. Resultados
   - Pruebas de motores
   - Verificación de cinemática
   - Pruebas de trayectorias

6. Conclusiones y Trabajo Futuro

7. Anexos
   - Datasheets
   - Código fuente
   - Diagramas esquemáticos
```

---

## Recommended LaTeX Packages

```latex
\usepackage[spanish]{babel}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{geometry}
\usepackage{booktabs}
\usepackage{siunitx}
```

---

## Bibliography Suggestions

1. ODrive Documentation: https://docs.odriverobotics.com/
2. ROS2 Documentation: https://docs.ros.org/
3. Siciliano et al. - "Robotics: Modelling, Planning and Control"
4. Makerbase ODrive GitHub: https://github.com/makerbase-mks/ODrive-MKS

---

## Questions to Clarify with Student
1. University and degree program
2. Specific sections required by the university
3. Word count or page requirements
4. Deadline
5. Any specific LaTeX template to follow

---

## LaTeX Content: Joint Torque Calculations (Squatting Scenario)

### \subsection{Joint Torque Calculations}

To calculate the torque required at each joint, a worst-case scenario is considered where the robot performs a bilateral squat (both feet on the ground) with a total mass of \SI{8}{kg}, resulting in \SI{4}{kg} (\SI{39.24}{N}) per leg. The robot features a 3-DOF leg with no ankle joint, using a ball foot for ground contact.

#### Robot Configuration and Dimensions

The coordinate system for the right leg is defined as: +X = Front, +Y = Left, +Z = Up. The fully extended leg points in the -Z direction.

\begin{table}[h]
\centering
\caption{Joint Configuration and Dimensions}
\label{tab:joint_config}
\begin{tabular}{llllll}
\toprule
\textbf{Joint} & \textbf{Rotation Axis} & \textbf{Z Offset (m)} & \textbf{Link Length (m)} & \textbf{Range (rad)} & \textbf{Gearbox} \\
\midrule
Hip 1 (Abd/Add) & X-axis & 0 & 0.04 & $\pm$0.79 & 16:1 \\
Hip 2 (Flex/Ext) & Y-axis & -0.04 & 0.35 & $\pm$0.52 & 16:1 \\
Knee (Flex/Ext) & Y-axis & -0.39 & 0.35 & -1.57 to 0 & 16:1 \\
Ball Foot & - & -0.74 & - & - & - \\
\bottomrule
\end{tabular}
\end{table}

#### Component Mass Distribution (Per Leg)

\begin{table}[h]
\centering
\caption{Component Masses (Per Leg, 8kg Total Robot)}
\label{tab:component_masses}
\begin{tabular}{llll}
\toprule
\textbf{Component} & \textbf{Qty} & \textbf{Mass (g)} & \textbf{Material/Model} \\
\midrule
Brushless Motor (D5065 270KV) & 3 & 1260 & 420g each \\
Bearing (680 series) & 15 & 150 & 10g each \\
2GT Belt (10$\times$200mm) & 6 & 48 & 8g each \\
Magnetic Encoder (AS5600) & 3 & 6 & 2g each \\
ODrive v3.6 Controller & 2 & 100 & 50g each \\
Raspberry Pi CM4 (split) & 0.5 & 60 & 120g total \\
LiPo 6S Battery (split) & 0.5 & 310 & 620g total \\
3D PETG Structure & 1 & 900 & Printed parts \\
M3/M4 Bolts & 25 & 25 & 1g each \\
Wiring/Connectors & 1 & 50 & Misc \\
\textbf{Total Per Leg} & - & \textbf{2909} & \textbf{~2.9kg} \\
Payload (Torso/Electronics) & - & 1100 & - \\
\textbf{Total With Payload} & - & \textbf{4000} & \textbf{4kg per leg} \\
\bottomrule
\end{tabular}
\end{table}

#### Squatting Pose Assumptions

For the squatting torque calculation, the following pose is assumed (bilateral squat, equal weight distribution):

\begin{itemize}
\item Hip 1 (X-axis abduction): 0° = 0 rad (symmetric, no side load)
    \item Hip 2 (Y-axis flexion): 60° = 1.047 rad
    \item Knee (Y-axis flexion): 90° = 1.571 rad
\item Link centers of mass: At midpoint of each link (0.02m, 0.175m, 0.175m from proximal joint)
\item Ground contact: Ball foot at 0.74m below hip mount
\end{itemize}

#### Torque Calculations

The torque at each joint is calculated using static equilibrium: $\tau = \sum m_i \cdot g \cdot d_{i,\perp}$, where $d_{i,\perp}$ is the horizontal distance from the joint to each load's center of mass (perpendicular to gravity).

\textbf{Knee Joint (Y-axis):}
\begin{align*}
d_{\text{ground}} &= 0.175\,\text{m} \quad \text{(CoM at link midpoint)} \\
\tau_{\text{ground}} &= 39.24\,\text{N} \times 0.175\,\text{m} = 6.87\,\text{Nm} \\
\tau_{\text{calf}} &= 0.99\,\text{kg} \times 9.81\,\text{m/s}^2 \times 0.0875\,\text{m} = 0.85\,\text{Nm} \\
\tau_{\text{Knee}} &= 6.87 + 0.85 = \mathbf{7.72\,\text{Nm}}
\end{align*}

\textbf{Hip 2 (Y-axis, Abduction/Adduction):}
\begin{align*}
\tau_{\text{Hip 2}} &= 0\,\text{Nm} \quad \text{(symmetric squat, no frontal plane load)}
\end{align*}

\textbf{Hip 1 (X-axis, Flexion/Extension):}
\begin{align*}
d_{\text{ground}} &= 0.04 + 0.35 \times \sin(90^\circ) + 0.175 = 0.565\,\text{m} \\
\tau_{\text{distal}} &= 39.24\,\text{N} \times 0.565\,\text{m} = 22.17\,\text{Nm} \\
\tau_{\text{thigh}} &= 1.49\,\text{kg} \times 9.81\,\text{m/s}^2 \times 0.02\,\text{m} = 0.29\,\text{Nm} \\
\tau_{\text{Hip 1}} &= 22.17 + 0.29 = \mathbf{22.46\,\text{Nm}}
\end{align*}

#### Results and ODrive Capacity

\begin{table}[h]
\centering
\caption{Joint Torque Results vs ODrive Capacity}
\label{tab:torque_results}
\begin{tabular}{lccc}
\toprule
\textbf{Joint} & \textbf{Required Torque} & \textbf{ODrive Capacity (16:1)} & \textbf{Status} \\
\midrule
Hip 1 (X-axis, Abd/Add) & 0 Nm & 14.7 Nm & \textcolor{green}{Sufficient} \\
Hip 2 (Y-axis, Flex/Ext) & 22.46 Nm & 14.7 Nm & \textcolor{red}{Insufficient} \\
Knee (Y-axis, Flex/Ext) & 7.72 Nm & 14.7 Nm & \textcolor{green}{Sufficient} \\
\bottomrule
\end{tabular}
\end{table}

\textbf{Note:} The Hip 2 (Y-axis, Flexion/Extension) joint exceeds the ODrive capacity (22.46 Nm required vs 14.7 Nm available). Hip 1 (X-axis, Abduction/Adduction) is sufficient with 0 Nm in symmetric squat. For a single-leg squat (8kg on one leg), torques would double, making Hip 2 and potentially Knee insufficient. Solutions include increasing the gearbox ratio to 25:1 or reducing the payload/squat depth.