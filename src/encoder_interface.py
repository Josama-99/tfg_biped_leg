"""Abstract base class for encoder interfaces.

This module defines the EncoderInterface abstract class that provides
a unified interface for reading encoder data regardless of the
underlying hardware implementation (Pi I2C, Serial, CAN, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging


class EncoderError(Exception):
    """Base exception for encoder errors."""
    pass


class EncoderTimeoutError(EncoderError):
    """Raised when encoder communication times out."""
    pass


class EncoderNotFoundError(EncoderError):
    """Raised when encoder is not found on the bus."""
    pass


class EncoderInterface(ABC):
    """Abstract base class for encoder implementations.
    
    This class defines the interface that all encoder implementations
    must follow. This allows swapping between different hardware
    (Pi I2C, microcontroller Serial, CAN, etc.) without changing
    high-level code.
    
    Example:
        # Create encoder based on configuration
        if config['type'] == 'pi':
            encoder = PiAS5600Encoder(bus=1, channel=0)
        else:
            encoder = SerialEncoder(port='/dev/ttyUSB0')
        
        # Use it the same way regardless of implementation
        angle = encoder.read_angle()
        encoder.zero()
    """
    
    def __init__(self, name: str = "encoder"):
        """Initialize the encoder interface.
        
        Args:
            name: Descriptive name for this encoder (e.g., 'hip', 'knee')
        """
        self.name = name
        self.logger = logging.getLogger(f"encoder.{name}")
        self._offset = 0.0
    
    @abstractmethod
    def read_raw(self) -> int:
        """Read the raw encoder value.
        
        Returns:
            Raw encoder value (typically 0 to max_count)
            
        Raises:
            EncoderTimeoutError: If communication times out
            EncoderNotFoundError: If encoder is not responding
        """
        pass
    
    @abstractmethod
    def read_angle(self) -> float:
        """Read the current angle in radians.
        
        Returns:
            Current angle in radians (typically 0 to 2*pi)
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the encoder is connected and responding.
        
        Returns:
            True if encoder responds, False otherwise
        """
        pass
    
    def zero(self) -> None:
        """Set the current position as the zero reference.
        
        After calling this, read_angle() will return 0 for the
        current position.
        """
        self._offset = self.read_angle()
        self.logger.info(f"{self.name} zeroed at {self._offset:.4f} rad")
    
    def set_offset(self, offset: float) -> None:
        """Set a manual offset value.
        
        Args:
            offset: Offset value in radians
        """
        self._offset = offset
        self.logger.debug(f"{self.name} offset set to {offset:.4f} rad")
    
    def get_offset(self) -> float:
        """Get the current offset value.
        
        Returns:
            Current offset in radians
        """
        return self._offset
    
    @abstractmethod
    def calibrate(self) -> bool:
        """Run calibration sequence.
        
        This method should be implemented by subclasses if
        calibration is supported.
        
        Returns:
            True if calibration succeeded, False otherwise
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
