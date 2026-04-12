"""Forward and inverse kinematics for 3-DOF leg."""

import numpy as np
from typing import Tuple, List


class LegKinematics:
    """Kinematics solver for 3-DOF bipedal leg."""
    
    def __init__(self, hip_offset: float = 0.0, 
                 upper_leg_length: float = 0.3,
                 lower_leg_length: float = 0.3):
        """Initialize leg kinematics.
        
        Args:
            hip_offset: Hip joint offset from base
            upper_leg_length: Length of upper leg segment (meters)
            lower_leg_length: Length of lower leg segment (meters)
        """
        self.hip_offset = hip_offset
        self.L1 = upper_leg_length
        self.L2 = lower_leg_length
    
    def forward_kinematics(self, hip_angle: float, knee_angle: float, 
                          ankle_angle: float) -> Tuple[float, float, float]:
        """Calculate end effector position from joint angles.
        
        Args:
            hip_angle: Hip joint angle (radians)
            knee_angle: Knee joint angle (radians)
            ankle_angle: Ankle joint angle (radians)
            
        Returns:
            (x, y, z) position of foot in base frame
        """
        hip_x = self.hip_offset * np.cos(hip_angle)
        hip_y = self.hip_offset * np.sin(hip_angle)
        hip_z = 0.0
        
        knee_total = hip_angle + knee_angle
        knee_x = hip_x + self.L1 * np.cos(knee_total)
        knee_y = hip_y + self.L1 * np.sin(knee_total)
        knee_z = 0.0
        
        ankle_total = knee_total + ankle_angle
        foot_x = knee_x + self.L2 * np.cos(ankle_total)
        foot_y = knee_y + self.L2 * np.sin(ankle_total)
        foot_z = 0.0
        
        return (foot_x, foot_y, foot_z)
    
    def inverse_kinematics(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Calculate joint angles from end effector position.
        
        Args:
            x: Foot position x-coordinate
            y: Foot position y-coordinate
            z: Foot position z-coordinate
            
        Returns:
            (hip_angle, knee_angle, ankle_angle) in radians
        """
        hip_angle = np.arctan2(y, x)
        
        rel_x = x - self.hip_offset * np.cos(hip_angle)
        rel_y = y - self.hip_offset * np.sin(hip_angle)
        
        r = np.sqrt(rel_x**2 + rel_y**2)
        
        cos_knee = (r**2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
        cos_knee = np.clip(cos_knee, -1.0, 1.0)
        knee_angle = np.arccos(cos_knee)
        
        alpha = np.arctan2(rel_y, rel_x)
        beta = np.arctan2(self.L2 * np.sin(knee_angle), 
                          self.L1 + self.L2 * np.cos(knee_angle))
        ankle_angle = alpha - beta - hip_angle
        
        return (hip_angle, -knee_angle, ankle_angle)
    
    def joint_limits_check(self, hip: float, knee: float, ankle: float,
                          hip_limits: Tuple[float, float] = (-0.79, 0.79),
                          knee_limits: Tuple[float, float] = (-1.57, 0.0),
                          ankle_limits: Tuple[float, float] = (-0.52, 0.52)) -> bool:
        """Check if joint angles are within safe limits.
        
        Args:
            hip: Hip angle
            knee: Knee angle
            ankle: Ankle angle
            hip_limits: (min, max) hip limits in radians
            knee_limits: (min, max) knee limits in radians
            ankle_limits: (min, max) ankle limits in radians
            
        Returns:
            True if all angles within limits
        """
        return (hip_limits[0] <= hip <= hip_limits[1] and
                knee_limits[0] <= knee <= knee_limits[1] and
                ankle_limits[0] <= ankle <= ankle_limits[1])
    
    def feet_positions_for_gait(self, step_height: float, step_length: float,
                                num_points: int = 10) -> List[Tuple[float, float, float]]:
        """Generate foot trajectory points for walking gait.
        
        Args:
            step_height: Maximum foot height during swing (meters)
            step_length: Forward distance covered per step (meters)
            num_points: Number of trajectory points
            
        Returns:
            List of (x, y, z) positions
        """
        trajectory = []
        
        for i in range(num_points):
            t = i / (num_points - 1)
            
            x = 0.0
            y = step_length * t
            
            if t < 0.5:
                z = step_height * np.sin(2 * np.pi * t)
            else:
                z = 0.0
            
            trajectory.append((x, y, z))
        
        return trajectory
    
    def jacobian(self, hip_angle: float, knee_angle: float, 
                 ankle_angle: float) -> np.ndarray:
        """Calculate Jacobian matrix for velocity mapping.
        
        Args:
            hip_angle: Hip joint angle (radians)
            knee_angle: Knee joint angle (radians)
            ankle_angle: Ankle joint angle (radians)
            
        Returns:
            3x3 Jacobian matrix
        """
        J = np.zeros((3, 3))
        
        hip_total = hip_angle
        knee_total = hip_angle + knee_angle
        ankle_total = knee_total + ankle_angle
        
        J[0, 0] = -self.hip_offset * np.sin(hip_total) - self.L1 * np.sin(knee_total) - self.L2 * np.sin(ankle_total)
        J[0, 1] = -self.L1 * np.sin(knee_total) - self.L2 * np.sin(ankle_total)
        J[0, 2] = -self.L2 * np.sin(ankle_total)
        
        J[1, 0] = self.hip_offset * np.cos(hip_total) + self.L1 * np.cos(knee_total) + self.L2 * np.cos(ankle_total)
        J[1, 1] = self.L1 * np.cos(knee_total) + self.L2 * np.cos(ankle_total)
        J[1, 2] = self.L2 * np.cos(ankle_total)
        
        J[2, 0] = 0.0
        J[2, 1] = 0.0
        J[2, 2] = 0.0
        
        return J
