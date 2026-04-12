"""Trajectory generation for walking gait."""

import numpy as np
from typing import List, Tuple, Callable
from .leg_kinematics import LegKinematics


class TrajectoryGenerator:
    """Generate trajectories for leg movement."""
    
    def __init__(self, kinematics: LegKinematics):
        """Initialize trajectory generator.
        
        Args:
            kinematics: LegKinematics instance
        """
        self.kinematics = kinematics
    
    def generate_step_trajectory(self, start_pos: Tuple[float, float, float],
                                end_pos: Tuple[float, float, float],
                                step_height: float = 0.1,
                                num_points: int = 20) -> List[Tuple[float, float, float]]:
        """Generate foot trajectory for a single step.
        
        Args:
            start_pos: Starting foot position
            end_pos: Ending foot position
            step_height: Maximum swing height
            num_points: Number of trajectory points
            
        Returns:
            List of (hip, knee, ankle) angle tuples
        """
        trajectory = []
        
        for i in range(num_points):
            t = i / (num_points - 1)
            
            x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
            
            if t < 0.5:
                z = start_pos[2] + step_height * np.sin(2 * np.pi * t)
            else:
                z = start_pos[2] + (end_pos[2] - start_pos[2]) * (t - 0.5) * 2
            
            try:
                angles = self.kinematics.inverse_kinematics(x, y, z)
                trajectory.append(angles)
            except ValueError:
                continue
        
        return trajectory
    
    def generate_walking_cycle(self, step_length: float = 0.15,
                              step_height: float = 0.1,
                              steps_per_cycle: int = 2) -> List[List[Tuple[float, float, float]]]:
        """Generate full walking cycle trajectory for two legs.
        
        Args:
            step_length: Forward distance per step
            step_height: Maximum swing height
            steps_per_cycle: Number of steps in one cycle
            
        Returns:
            List of trajectories for each leg
        """
        left_trajectory = []
        right_trajectory = []
        
        for step in range(steps_per_cycle):
            y_start = step * step_length
            y_end = (step + 1) * step_length
            
            left = self.generate_step_trajectory(
                (0.0, y_start, 0.0),
                (0.0, y_end, 0.0),
                step_height
            )
            left_trajectory.extend(left)
            
            right = self.generate_step_trajectory(
                (0.0, y_end, 0.0),
                (0.0, y_start, 0.0),
                0.0
            )
            right_trajectory.extend(right)
        
        return [left_trajectory, right_trajectory]
    
    def generate_circular_trajectory(self, radius: float = 0.1,
                                     center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                                     num_points: int = 36) -> List[Tuple[float, float, float]]:
        """Generate circular foot trajectory.
        
        Args:
            radius: Circle radius
            center: Circle center position
            num_points: Number of points on circle
            
        Returns:
            List of (hip, knee, ankle) angle tuples
        """
        trajectory = []
        
        for i in range(num_points):
            theta = 2 * np.pi * i / num_points
            
            x = center[0] + radius * np.cos(theta)
            y = center[1] + radius * np.sin(theta)
            z = center[2]
            
            try:
                angles = self.kinematics.inverse_kinematics(x, y, z)
                trajectory.append(angles)
            except ValueError:
                continue
        
        return trajectory
    
    def smooth_trajectory(self, trajectory: List[Tuple[float, float, float]],
                         smoothing_factor: float = 0.2) -> List[Tuple[float, float, float]]:
        """Apply smoothing to trajectory using moving average.
        
        Args:
            trajectory: Input trajectory
            smoothing_factor: Smoothing strength (0-1)
            
        Returns:
            Smoothed trajectory
        """
        if len(trajectory) < 3:
            return trajectory
        
        smoothed = []
        window_size = max(3, int(len(trajectory) * smoothing_factor))
        
        for i in range(len(trajectory)):
            start = max(0, i - window_size // 2)
            end = min(len(trajectory), i + window_size // 2 + 1)
            
            avg = [0.0, 0.0, 0.0]
            for j in range(start, end):
                for k in range(3):
                    avg[k] += trajectory[j][k]
            
            count = end - start
            smoothed.append(tuple(a / count for a in avg))
        
        return smoothed
    
    def interpolate_trajectory(self, trajectory: List[Tuple[float, float, float]],
                              target_length: int) -> List[Tuple[float, float, float]]:
        """Interpolate trajectory to different length.
        
        Args:
            trajectory: Input trajectory
            target_length: Desired number of points
            
        Returns:
            Interpolated trajectory
        """
        if len(trajectory) == target_length:
            return trajectory
        
        if len(trajectory) < 2:
            return trajectory
        
        result = []
        for i in range(target_length):
            t = i / (target_length - 1)
            idx = t * (len(trajectory) - 1)
            idx_low = int(idx)
            idx_high = min(idx_low + 1, len(trajectory) - 1)
            
            frac = idx - idx_low
            
            interp = tuple(
                trajectory[idx_low][j] * (1 - frac) + trajectory[idx_high][j] * frac
                for j in range(3)
            )
            result.append(interp)
        
        return result
