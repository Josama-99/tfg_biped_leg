"""Unit tests for leg kinematics."""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tfg_biped_leg.leg_kinematics import LegKinematics


class TestLegKinematics:
    """Test cases for LegKinematics class."""
    
    @pytest.fixture
    def kinematics(self):
        """Create kinematics instance for testing."""
        return LegKinematics(upper_leg_length=0.3, lower_leg_length=0.3)
    
    def test_home_position(self, kinematics):
        """Test FK at home position (all zeros)."""
        x, y, z = kinematics.forward_kinematics(0.0, 0.0, 0.0)
        
        total_length = kinematics.L1 + kinematics.L2
        assert np.isclose(x, total_length)
        assert np.isclose(y, 0.0)
        assert np.isclose(z, 0.0)
    
    def test_ik_at_home(self, kinematics):
        """Test IK at home position."""
        hip, knee, ankle = kinematics.inverse_kinematics(0.6, 0.0, 0.0)
        
        assert np.isclose(hip, 0.0)
        assert np.isclose(knee, 0.0)
        assert np.isclose(ankle, 0.0)
    
    def test_fk_ik_consistency(self, kinematics):
        """Test that FK and IK are inverse of each other."""
        test_angles = [0.3, -0.5, 0.1]
        
        x, y, z = kinematics.forward_kinematics(*test_angles)
        hip, knee, ankle = kinematics.inverse_kinematics(x, y, z)
        
        assert np.isclose(hip, test_angles[0], atol=1e-6)
        assert np.isclose(knee, test_angles[1], atol=1e-6)
        assert np.isclose(ankle, test_angles[2], atol=1e-6)
    
    def test_joint_limits(self, kinematics):
        """Test joint limits checking."""
        assert kinematics.joint_limits_check(0.0, 0.0, 0.0)
        
        assert not kinematics.joint_limits_check(1.5, 0.0, 0.0)
        assert not kinematics.joint_limits_check(0.0, -2.0, 0.0)
        assert not kinematics.joint_limits_check(0.0, 0.0, 1.0)
    
    def test_jacobian_shape(self, kinematics):
        """Test Jacobian matrix dimensions."""
        J = kinematics.jacobian(0.0, 0.0, 0.0)
        
        assert J.shape == (3, 3)
    
    def test_jacobian_at_home(self, kinematics):
        """Test Jacobian at home position."""
        J = kinematics.jacobian(0.0, 0.0, 0.0)
        
        expected = np.array([
            [0.0, -0.3, -0.3],
            [0.6, 0.3, 0.3],
            [0.0, 0.0, 0.0]
        ])
        
        assert np.allclose(J, expected, atol=1e-6)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
