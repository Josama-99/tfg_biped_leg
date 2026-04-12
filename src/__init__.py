"""Encoder drivers package.

This package provides modular encoder support with abstraction
layers for different hardware implementations.

Example:
    # Pi I2C implementation (current)
    from src import EncoderManager, PiAS5600Encoder
    
    manager = EncoderManager(encoder_type='pi', config={
        'hip': {'channel': 0},
        'knee': {'channel': 1},
        'ankle': {'channel': 2}
    })
    angles = manager.read_all()
    
    # Future: Microcontroller implementation
    from src import EncoderManager, SerialEncoder
    
    manager = EncoderManager(encoder_type='serial', config={
        'hip': {'port': '/dev/ttyUSB0'},
        'knee': {'port': '/dev/ttyUSB0'},
        'ankle': {'port': '/dev/ttyUSB0'}
    })
"""

from .encoder_interface import (
    EncoderInterface,
    EncoderError,
    EncoderTimeoutError,
    EncoderNotFoundError
)
from .pi_as5600_encoder import PiAS5600Encoder
from .serial_encoder import SerialEncoder
from .tca9548a import TCA9548A
from .encoder_manager import EncoderManager

__all__ = [
    # Base classes
    'EncoderInterface',
    'EncoderError',
    'EncoderTimeoutError',
    'EncoderNotFoundError',
    # Implementations
    'PiAS5600Encoder',
    'SerialEncoder',
    'TCA9548A',
    # Manager
    'EncoderManager',
]
