"""AS5600 magnetic encoder driver for Raspberry Pi.

This module provides a Python driver for the AS5600 magnetic
rotary encoder using I2C on the Raspberry Pi with a TCA9548A
I2C multiplexer to support multiple encoders.
"""

import math
import time
import smbus2
from typing import Optional

from .encoder_interface import (
    EncoderInterface, 
    EncoderTimeoutError, 
    EncoderNotFoundError
)
from .tca9548a import TCA9548A


class PiAS5600Encoder(EncoderInterface):
    """AS5600 encoder driver for Raspberry Pi with I2C multiplexer.
    
    The AS5600 is a 12-bit magnetic rotary encoder that measures
    the magnetic field angle of a magnet placed above the chip.
    It provides 360 degrees of resolution with 4096 positions.
    
    This class uses the TCA9548A I2C multiplexer to read multiple
    AS5600 encoders that share the same I2C address (0x36).
    
    Example:
        # Create encoder on mux channel 0
        encoder = PiAS5600Encoder(name='hip', mux_channel=0)
        
        # Read angle
        angle = encoder.read_angle()  # Returns radians
        
        # Zero at current position
        encoder.zero()
        
        # Now reads will be relative to zero point
        angle = encoder.read_angle()  # Now relative to zero
    """
    
    # AS5600 I2C address (fixed, cannot be changed)
    AS5600_ADDR = 0x36
    
    # AS5600 registers
    REG_RAW_ANGLE = 0x0C        # Raw angle (high byte)
    REG_RAW_ANGLE_L = 0x0D      # Raw angle (low byte) - alternate register
    REG_ANGLE = 0x0E            # Filtered angle
    REG_STATUS = 0x0B            # Status register
    REG_AGC = 0x1A              # Automatic Gain Control
    REG_MAGNITUDE = 0x1B         # Magnetic magnitude
    REG_CONFIG = 0x07            # Configuration register
    
    # Status bits
    STATUS_MAGNET_DETECTED = 0x20
    STATUS_MAGNET_TOO_STRONG = 0x08
    STATUS_MAGNET_TOO_WEAK = 0x10
    
    # Encoder resolution (12-bit)
    MAX_RAW_VALUE = 4096  # 2^12
    
    def __init__(
        self,
        name: str = "encoder",
        bus: int = 1,
        mux_address: int = TCA9548A.DEFAULT_ADDRESS,
        mux_channel: int = 0
    ):
        """Initialize AS5600 encoder.
        
        Args:
            name: Descriptive name for this encoder
            bus: I2C bus number (1 for Raspberry Pi)
            mux_address: TCA9548A I2C address (default 0x70)
            mux_channel: TCA9548A channel (0-7) for this encoder
        """
        super().__init__(name)
        self.bus_num = bus
        self.mux_address = mux_address
        self.mux_channel = mux_channel
        
        self._mux = TCA9548A(bus=bus, address=mux_address)
        self._connected = False
        
    def _select_mux_channel(self) -> None:
        """Select the multiplexer channel for this encoder."""
        self._mux.select_channel(self.mux_channel)
    
    def _read_byte(self, register: int) -> int:
        """Read a single byte from the AS5600.
        
        Args:
            register: Register address to read
            
        Returns:
            Byte value read from register
        """
        self._select_mux_channel()
        bus = smbus2.SMBus(self.bus_num)
        try:
            return bus.read_byte_data(self.AS5600_ADDR, register)
        finally:
            bus.close()
    
    def _read_word(self, register: int) -> int:
        """Read a 16-bit word from the AS5600.
        
        Args:
            register: Register address to read
            
        Returns:
            16-bit word value
        """
        self._select_mux_channel()
        bus = smbus2.SMBus(self.bus_num)
        try:
            return bus.read_word_data(self.AS5600_ADDR, register)
        finally:
            bus.close()
    
    def is_connected(self) -> bool:
        """Check if the encoder is connected and responding.
        
        Returns:
            True if encoder responds, False otherwise
        """
        try:
            self._select_mux_channel()
            bus = smbus2.SMBus(self.bus_num)
            try:
                # Try to read status register
                status = bus.read_byte_data(self.AS5600_ADDR, self.REG_STATUS)
                self._connected = True
                self.logger.debug(f"{self.name}: Encoder connected")
                return True
            finally:
                bus.close()
        except Exception as e:
            self._connected = False
            self.logger.warning(f"{self.name}: Encoder not responding: {e}")
            return False
    
    def read_raw(self) -> int:
        """Read the raw encoder value (0-4095).
        
        Returns:
            Raw encoder value (12-bit, 0-4095)
            
        Raises:
            EncoderTimeoutError: If communication times out
            EncoderNotFoundError: If encoder is not responding
        """
        try:
            # Read high and low bytes of raw angle
            high = self._read_byte(self.REG_RAW_ANGLE)
            low = self._read_byte(self.REG_RAW_ANGLE_L)
            
            # Combine into 12-bit value (bits 11-0)
            raw = ((high & 0x0F) << 8) | low
            
            return raw
            
        except FileNotFoundError as e:
            raise EncoderNotFoundError(f"{self.name}: I2C bus not found: {e}")
        except OSError as e:
            if "121" in str(e) or "Remote I/O" in str(e):
                raise EncoderTimeoutError(f"{self.name}: Encoder timeout: {e}")
            raise
        except Exception as e:
            raise EncoderTimeoutError(f"{self.name}: Communication error: {e}")
    
    def read_angle(self) -> float:
        """Read the current angle in radians.
        
        Returns:
            Current angle in radians (0 to 2*pi), adjusted by offset
        """
        raw = self.read_raw()
        # Convert raw value to radians (0 to 2*pi)
        angle = (raw / self.MAX_RAW_VALUE) * 2 * math.pi - self._offset
        return angle
    
    def read_filtered_angle(self) -> float:
        """Read the filtered angle in radians.
        
        The AS5600 has a built-in low-pass filter that provides
        a smoother reading at the cost of some latency.
        
        Returns:
            Filtered angle in radians
        """
        try:
            high = self._read_byte(self.REG_ANGLE)
            low = self._read_byte(self.REG_ANGLE_L)
            raw = ((high & 0x0F) << 8) | low
            return (raw / self.MAX_RAW_VALUE) * 2 * math.pi - self._offset
        except Exception as e:
            self.logger.warning(f"{self.name}: Failed to read filtered angle: {e}")
            return self.read_angle()
    
    def get_magnet_status(self) -> dict:
        """Get the magnet detection status.
        
        Returns:
            Dictionary with magnet status information
        """
        try:
            status = self._read_byte(self.REG_STATUS)
            agc = self._read_byte(self.REG_AGC)
            magnitude = self._read_word(self.REG_MAGNITUDE)
            
            detected = bool(status & self.STATUS_MAGNET_DETECTED)
            too_strong = bool(status & self.STATUS_MAGNET_TOO_STRONG)
            too_weak = bool(status & self.STATUS_MAGNET_TOO_WEAK)
            
            return {
                'detected': detected,
                'too_strong': too_strong,
                'too_weak': too_weak,
                'agc': agc,
                'magnitude': magnitude
            }
        except Exception as e:
            self.logger.error(f"{self.name}: Failed to read magnet status: {e}")
            return {'error': str(e)}
    
    def calibrate(self) -> bool:
        """Run calibration to find zero position.
        
        This runs a simple calibration that sets the current
        position as zero. For full calibration, the magnet
        position should be adjusted so that the magnitude
        reading is optimal (not too strong/weak).
        
        Returns:
            True if calibration succeeded
        """
        self.logger.info(f"{self.name}: Starting calibration")
        
        # Check magnet status
        status = self.get_magnet_status()
        if 'error' in status:
            self.logger.error(f"{self.name}: Cannot calibrate - {status['error']}")
            return False
        
        if not status['detected']:
            self.logger.error(f"{self.name}: Magnet not detected!")
            return False
        
        if status['too_strong']:
            self.logger.warning(f"{self.name}: Magnet too strong - move farther from chip")
        
        if status['too_weak']:
            self.logger.warning(f"{self.name}: Magnet too weak - move closer to chip")
        
        # Set current position as zero
        self.zero()
        self.logger.info(f"{self.name}: Calibration complete")
        return True
    
    def close(self) -> None:
        """Close connections."""
        self._mux.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
