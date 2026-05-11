"""Denavit-Hartenberg parameters and forward kinematics for bipedal leg.

Two models:
  1. URDF-based: foot position from actual Onshape assembly transforms
  2. Simplified DH: classic DH parameter table for documentation

Foot tip position includes the shank (0.35m below knee).
"""

import numpy as np


def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0, 0],
                     [0, c, -s, 0],
                     [0, s, c, 0],
                     [0, 0, 0, 1]])


def rot_y(b):
    c, s = np.cos(b), np.sin(b)
    return np.array([[c, 0, s, 0],
                     [0, 1, 0, 0],
                     [-s, 0, c, 0],
                     [0, 0, 0, 1]])


def rot_z(g):
    c, s = np.cos(g), np.sin(g)
    return np.array([[c, -s, 0, 0],
                     [s, c, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]])


def trans(x, y, z):
    return np.array([[1, 0, 0, x],
                     [0, 1, 0, y],
                     [0, 0, 1, z],
                     [0, 0, 0, 1]])


def dh_transform(a, alpha, d, theta):
    """Standard DH: T = R_z(θ) · trans_z(d) · trans_x(a) · R_x(α)"""
    ca, sa = np.cos(alpha), np.sin(alpha)
    ct, st = np.cos(theta), np.sin(theta)
    return np.array([
        [ct, -st*ca,  st*sa, a*ct],
        [st,  ct*ca, -ct*sa, a*st],
        [0,   sa,     ca,    d],
        [0,   0,      0,     1]
    ])


# =========================================================================
# URDF joint data (from Onshape assembly robot.urdf)
# =========================================================================
# Each joint: origin xyz + rpy, and axis = [0,0,1] (URDF convention)

RIGHT_LEG_URDF = [
    {"name": "right_hip1", "xyz": [-0.0625, -0.0195, -0.05],
     "rpy": [-1.5708, -0.0533974, 0],    "limits": (-0.2957, 1.2751)},
    {"name": "right_hip2", "xyz": [0.0305, 0.04, -0.03],
     "rpy": [-1.5708, 1.22173, 1.5708],  "limits": (0, 1.3963)},
    {"name": "right_knee", "xyz": [0, -0.35, 0],
     "rpy": [3.14159, 0, 0],              "limits": (-1.7177, 1.7730)},
]

LEFT_LEG_URDF = [
    {"name": "left_hip1",  "xyz": [0.0625, -0.0195, -0.05],
     "rpy": [-1.5708, -0.000278854, 0],  "limits": (-1.2215, 0.3493)},
    {"name": "left_hip2",  "xyz": [-0.0305, 0.04, -0.03],
     "rpy": [-1.5708, 1.53479, -1.5708], "limits": (-1.0112, 0.3851)},
    {"name": "left_knee",  "xyz": [0, 0.35, 0],
     "rpy": [3.14159, 0, 0],              "limits": (-1.7271, 1.7636)},
]

# Tool offset: shank extends 0.35m from knee joint in the link frame
# In the URDF, the shank extends along local -Y for right leg, +Y for left leg
# (the knee joint translation is (0, ±0.35, 0) for thigh, shank continues same dir)
SHANK_LENGTH = 0.35
RIGHT_TOOL = trans(0, SHANK_LENGTH, 0)    # shank extends along +Y of part_1_4
LEFT_TOOL  = trans(0, -SHANK_LENGTH, 0)   # shank extends along -Y of part_1_7


def urdf_fk(angles, leg, tool_transform=None):
    """Forward kinematics from URDF joint data + optional tool offset.
    
    Args:
        angles: [θ₁, θ₂, θ₃] joint angles in radians
        leg: leg chain data (RIGHT_LEG_URDF or LEFT_LEG_URDF)
        tool_transform: optional 4x4 tool offset from last joint to foot tip
    
    Returns:
        T_base_to_foot (4x4), list of intermediate transforms
    """
    T = np.eye(4)
    stages = [T.copy()]
    for i, j in enumerate(leg):
        Ti = (trans(*j["xyz"])
              @ rot_z(j["rpy"][2])
              @ rot_y(j["rpy"][1])
              @ rot_x(j["rpy"][0])
              @ rot_z(angles[i]))
        T = T @ Ti
        stages.append(T.copy())
    if tool_transform is not None:
        T = T @ tool_transform
        stages.append(T.copy())
    return T, stages


# =========================================================================
# Simplified DH Model (classic DH parameter table)
# =========================================================================
# DH base frame: Z₀=forward (hip abduction axis), X₀=down, Y₀=right
# Physical frame: X=forward, Y=right, Z=down
# Joints: θ₁=hip abduction (Z₀), θ₂=hip flexion (Z₁=lateral), θ₃=knee (Z₂=lateral)
# Link lengths: L0=0.04m (hip1→hip2), L1=0.35m (thigh), L2=0.35m (shank)
#
# Why Z₀=forward: standard DH requires Zᵢ = axis of joint i+1. Hip abduction
# rotates about the forward direction. With Z₀ vertical, no α rotation can
# redirect Z into the forward direction (α only works in the Y-Z plane).
# α₂=-90° rotates Z₂ (lateral) back to Z₃=forward, matching base orientation.

DH_PARAMS = [
    (0.04,   np.pi/2,  0.0,  "θ₁", "Hip abduction (Z₀=forward)"),
    (0.35,   0.0,      0.0,  "θ₂", "Hip flexion (Z₁=lateral)"),
    (0.35,   -np.pi/2, 0.0,  "θ₃", "Knee flexion (Z₂=lateral)"),
]

# Left leg shares the same DH params (mirroring handled by joint limits)
DH_PARAMS_RIGHT = DH_PARAMS
DH_PARAMS_LEFT = DH_PARAMS


def dh_fk(theta, dh_params):
    """Forward kinematics using DH parameters.
    
    Args:
        theta: [θ₁, θ₂, θ₃]
        dh_params: list of (a, α, d, θ_label, name) tuples
    """
    T = np.eye(4)
    idx = 0
    for a, alpha, d, label, _ in dh_params:
        th = theta[idx] if label.startswith("θ") else 0.0
        idx += 1 if label.startswith("θ") else 0
        T = T @ dh_transform(a, alpha, d, th)
    return T


# =========================================================================
# Display helpers
# =========================================================================

def print_dh_table(params, title):
    """Print formatted DH parameter table."""
    print(f"\n{title}")
    print(f"{'i':<5} {'aᵢ₋₁ (m)':<12} {'αᵢ₋₁ (rad)':<14} {'dᵢ (m)':<12} {'θᵢ':<12} {'Description'}")
    print("-" * 70)
    for i, (a, alpha, d, theta_label, name) in enumerate(params):
        print(f"{i:<5} {a:<12.4f} {alpha:<14.4f} {d:<12.4f} {theta_label:<12} {name}")
    print()


def print_T(T, label):
    """Print 4x4 matrix."""
    print(f"{label}:")
    for row in T:
        print(f"  [{row[0]:8.4f} {row[1]:8.4f} {row[2]:8.4f} {row[3]:8.4f}]")


# =========================================================================
# Main
# =========================================================================

def main():
    np.set_printoptions(precision=4, suppress=True)
    
    print("=" * 72)
    print("  DENAVIT-HARTENBERG PARAMETERS & FOOT POSITION")
    print("  Bipedal Robot — 3-DOF Leg (from Onshape URDF)")
    print("=" * 72)
    
    # ── DH Table ──────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  DH PARAMETER TABLES")
    print("  DH base: Z₀=forward (abduction), X₀=down, Y₀=right")
    print("  Physical: X=forward, Y=right, Z=down")
    print(f"  Lengths: L0=0.04m (hip1→hip2), L1=0.35m (thigh), L2=0.35m (shank)")
    print("─" * 72)
    
    print_dh_table(DH_PARAMS_RIGHT, "RIGHT LEG:")
    print_dh_table(DH_PARAMS_LEFT,  "LEFT LEG:")
    
    # ── Foot Positions ────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  FOOT POSITIONS FOR STANDARD POSES")
    print("─" * 72)
    
    test_poses = [
        ("Home (standing straight)", [0.0, 0.0, 0.0]),
        ("Hip abduction (10°)",      [0.175, 0.0, 0.0]),
        ("Hip flexion (30°)",        [0.0, 0.524, 0.0]),
        ("Slight crouch",            [0.0, 0.3, -0.6]),
        ("Deep squat (~60° hip, 90° knee)", [0.0, 0.5, -1.2]),
        ("Wide stance",              [0.3, 0.0, 0.0]),
    ]
    
    for pose_name, angles in test_poses:
        T_r, _ = urdf_fk(angles, RIGHT_LEG_URDF, RIGHT_TOOL)
        T_l, _ = urdf_fk(angles, LEFT_LEG_URDF, LEFT_TOOL)
        p_r, p_l = T_r[:3, 3], T_l[:3, 3]
        dist_r = np.linalg.norm(p_r)
        dist_l = np.linalg.norm(p_l)
        
        print(f"\n  {pose_name}")
        print(f"    θ₁={angles[0]:+.3f}  θ₂={angles[1]:+.3f}  θ₃={angles[2]:+.3f} rad")
        print(f"    Right foot:  x={p_r[0]:+.4f}  y={p_r[1]:+.4f}  z={p_r[2]:+.4f}  "
              f"(from hip: {dist_r:.4f}m)")
        print(f"    Left foot:   x={p_l[0]:+.4f}  y={p_l[1]:+.4f}  z={p_l[2]:+.4f}  "
              f"(from hip: {dist_l:.4f}m)")
        print(f"    Stance width: {np.linalg.norm(p_r[:2] - p_l[:2]):.4f}m")
    
    # ── Full transform at home ────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  HOMOGENEOUS TRANSFORMATION: Base → Right Foot (standing straight)")
    print(f"{'─' * 72}")
    T_home, stages = urdf_fk([0, 0, 0], RIGHT_LEG_URDF, RIGHT_TOOL)
    p_home = T_home[:3, 3]
    print_T(T_home, "T_base→foot (4×4)")
    
    print(f"\n  Cumulative positions through kinematic chain:")
    labels = ["Base", "After Hip1", "After Hip2", "After Knee", "Foot tip"]
    for i, label in enumerate(labels):
        p = stages[i][:3, 3]
        print(f"    {label:<15} ({p[0]:+.4f}, {p[1]:+.4f}, {p[2]:+.4f})")
    
    # ── DH Model Comparison ───────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  COMPARISON: URDF vs Simplified DH Model (at home)")
    print(f"{'─' * 72}")
    
    T_dh = dh_fk([0, 0, 0], DH_PARAMS_RIGHT)
    p_dh = T_dh[:3, 3]
    print(f"  Simplified DH:   ({p_dh[0]:+.4f}, {p_dh[1]:+.4f}, {p_dh[2]:+.4f})  "
          f"dist={np.linalg.norm(p_dh):.4f}m")
    print(f"  DH -> physical:  X_fwd={p_dh[2]:+.4f}  Y_right={p_dh[1]:+.4f}  "
          f"Z_down={p_dh[0]:+.4f}")
    print(f"  URDF (Onshape):  ({p_home[0]:+.4f}, {p_home[1]:+.4f}, {p_home[2]:+.4f})  "
          f"dist={np.linalg.norm(p_home):.4f}m  (includes hip offsets + frame rotations)")
    print(f"  URDF->physical:  X_fwd={p_home[0]:+.4f}  Y_left={p_home[1]:+.4f}  "
          f"Z_up={p_home[2]:+.4f}")
    
    # ── Interactive mode ──────────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  INTERACTIVE: Enter joint angles to compute foot position")
    print("  Format: θ₁ θ₂ θ₃  (radians)")
    print(f"{'─' * 72}")
    
    while True:
        try:
            inp = input("  > ").strip()
            if not inp or inp.lower() in ('q', 'quit', 'exit'):
                break
            vals = [float(x) for x in inp.split()]
            if len(vals) < 3:
                print("  Need 3 angles, e.g. 0 0.5 -1.2")
                continue
            
            Tr, _ = urdf_fk(vals[:3], RIGHT_LEG_URDF, RIGHT_TOOL)
            Tl, _ = urdf_fk(vals[:3], LEFT_LEG_URDF, LEFT_TOOL)
            pr, pl = Tr[:3, 3], Tl[:3, 3]
            
            print(f"  Right: ({pr[0]:+.4f}, {pr[1]:+.4f}, {pr[2]:+.4f})  "
                  f"Left: ({pl[0]:+.4f}, {pl[1]:+.4f}, {pl[2]:+.4f})  "
                  f"Stance: {np.linalg.norm(pr[:2]-pl[:2]):.4f}m")
        except (ValueError, EOFError, KeyboardInterrupt):
            break
    
    print("\nDone.")


if __name__ == "__main__":
    main()
