"""Encoder manager for handling multiple encoders.

This module provides the EncoderManager class that manages multiple
encoder instances (one per joint) and provides a unified interface
for reading all encoder data.
"""

import logging
from typing import Dict, List, Optional

from .encoder_interface import EncoderInterface, EncoderError
from .pi_as5600_encoder import PiAS5600Encoder
from .serial_encoder import SerialEncoder


class EncoderManager:
    """Manager for multiple encoder instances.
    
    This class manages encoder instances for all joints and provides
    methods to read all encoders or individual encoders.
    
    Example:
        # Create manager with 3 encoders
        manager = EncoderManager(
            encoder_type='pi',
            config={
                'hip': {'channel': 0},
                'knee': {'channel': 1},
                'ankle': {'channel': 2}
            }
        )
        
        # Read all angles
        angles = manager.read_all()
        # {'hip': 0.5, 'knee': 1.2, 'ankle': 0.3}
        
        # Read single encoder
        hip_angle = manager.read('hip')
        
        # Zero all encoders
        manager.zero_all()
    """
    
    def __init__(
        self,
        encoder_type: str = 'pi',
        config: Optional[Dict] = None
    ):
        """Initialize encoder manager.
        
        Args:
            encoder_type: Type of encoder ('pi' for I2C, 'serial' for microcontroller)
            config: Configuration dictionary for encoders
        """
        self.logger = logging.getLogger("encoder_manager")
        self.encoder_type = encoder_type
        self.encoders: Dict[str, EncoderInterface] = {}
        
        if config:
            self.create_encoders(config)
    
    def create_encoders(self, config: Dict) -> None:
        """Create encoder instances based on configuration.
        
        Args:
            config: Dictionary mapping joint names to configuration
                   e.g., {'hip': {'channel': 0}, 'knee': {'channel': 1}}
        """
        self.encoders.clear()
        
        for joint_name, joint_config in config.items():
            if self.encoder_type == 'pi':
                encoder = PiAS5600Encoder(
                    name=joint_name,
                    bus=joint_config.get('bus', 1),
                    mux_address=joint_config.get('mux_address', 0x70),
                    mux_channel=joint_config.get('channel', joint_config.get('mux_channel', 0))
                )
            elif self.encoder_type == 'serial':
                encoder = SerialEncoder(
                    name=joint_name,
                    port=joint_config.get('port', '/dev/ttyUSB0'),
                    baud=joint_config.get('baud', 115200)
                )
            else:
                raise ValueError(f"Unknown encoder type: {self.encoder_type}")
            
            self.encoders[joint_name] = encoder
            self.logger.info(f"Created {self.encoder_type} encoder for {joint_name}")
    
    def read(self, name: str) -> float:
        """Read angle from a specific encoder.
        
        Args:
            name: Name of the encoder (joint name)
            
        Returns:
            Angle in radians
            
        Raises:
            KeyError: If encoder not found
            EncoderError: If read fails
        """
        if name not in self.encoders:
            raise KeyError(f"Encoder '{name}' not found. Available: {list(self.encoders.keys())}")
        
        return self.encoders[name].read_angle()
    
    def read_all(self) -> Dict[str, float]:
        """Read angles from all encoders.
        
        Returns:
            Dictionary mapping encoder names to angles in radians
        """
        results = {}
        for name, encoder in self.encoders.items():
            try:
                results[name] = encoder.read_angle()
            except EncoderError as e:
                self.logger.error(f"Failed to read {name}: {e}")
                results[name] = 0.0  # Default to 0 on error
        return results
    
    def read_raw(self, name: str) -> int:
        """Read raw value from a specific encoder.
        
        Args:
            name: Name of the encoder
            
        Returns:
            Raw encoder value
        """
        if name not in self.encoders:
            raise KeyError(f"Encoder '{name}' not found")
        return self.encoders[name].read_raw()
    
    def read_all_raw(self) -> Dict[str, int]:
        """Read raw values from all encoders.
        
        Returns:
            Dictionary mapping encoder names to raw values
        """
        results = {}
        for name, encoder in self.encoders.items():
            try:
                results[name] = encoder.read_raw()
            except EncoderError as e:
                self.logger.error(f"Failed to read raw {name}: {e}")
                results[name] = 0
        return results
    
    def zero(self, name: str) -> None:
        """Zero a specific encoder.
        
        Args:
            name: Name of the encoder to zero
        """
        if name not in self.encoders:
            raise KeyError(f"Encoder '{name}' not found")
        self.encoders[name].zero()
    
    def zero_all(self) -> None:
        """Zero all encoders."""
        for name, encoder in self.encoders.items():
            try:
                encoder.zero()
            except EncoderError as e:
                self.logger.error(f"Failed to zero {name}: {e}")
    
    def calibrate(self, name: str) -> bool:
        """Calibrate a specific encoder.
        
        Args:
            name: Name of the encoder to calibrate
            
        Returns:
            True if calibration succeeded
        """
        if name not in self.encoders:
            raise KeyError(f"Encoder '{name}' not found")
        return self.encoders[name].calibrate()
    
    def calibrate_all(self) -> Dict[str, bool]:
        """Calibrate all encoders.
        
        Returns:
            Dictionary mapping encoder names to calibration success
        """
        results = {}
        for name, encoder in self.encoders.items():
            try:
                results[name] = encoder.calibrate()
            except EncoderError as e:
                self.logger.error(f"Failed to calibrate {name}: {e}")
                results[name] = False
        return results
    
    def is_connected(self, name: str) -> bool:
        """Check if a specific encoder is connected.
        
        Args:
            name: Name of the encoder
            
        Returns:
            True if connected
        """
        if name not in self.encoders:
            return False
        return self.encoders[name].is_connected()
    
    def check_all_connected(self) -> Dict[str, bool]:
        """Check connection status of all encoders.
        
        Returns:
            Dictionary mapping encoder names to connection status
        """
        results = {}
        for name, encoder in self.encoders.items():
            results[name] = encoder.is_connected()
        return results
    
    def get_names(self) -> List[str]:
        """Get list of encoder names.
        
        Returns:
            List of encoder names
        """
        return list(self.encoders.keys())
    
    def close(self) -> None:
        """Close all encoder connections."""
        for encoder in self.encoders.values():
            try:
                encoder.close()
            except Exception as e:
                self.logger.error(f"Error closing encoder: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def __len__(self) -> int:
        """Return number of encoders."""
        return len(self.encoders)
    
    def __repr__(self) -> str:
        return f"EncoderManager(type='{self.encoder_type}', count={len(self.encoders)})"
