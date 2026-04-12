"""TCA9548A I2C multiplexer helper.

This module provides a Python interface for the TCA9548A
I2C multiplexer, which allows connecting multiple devices
with the same I2C address to a single I2C bus.
"""

import smbus2
import logging
from typing import Optional


class TCA9548A:
    """Driver for TCA9548A I2C multiplexer.
    
    The TCA9548A has 8 independent I2C buses, each of which
    can be connected to devices that share the same I2C address.
    
    Example:
        mux = TCA9548A(bus=1, address=0x70)
        mux.select_channel(0)  # Enable channel 0
        # Now can communicate with device on channel 0
        mux.select_channel(1)  # Switch to channel 1
        # Now can communicate with device on channel 1
    """
    
    # TCA9548A I2C address (default)
    DEFAULT_ADDRESS = 0x70
    
    # Register to control channels
    CONTROL_REG = 0x00
    
    # Number of channels
    NUM_CHANNELS = 8
    
    def __init__(self, bus: int = 1, address: int = DEFAULT_ADDRESS):
        """Initialize TCA9548A multiplexer.
        
        Args:
            bus: I2C bus number (1 for Raspberry Pi)
            address: I2C address of the TCA9548A (default 0x70)
        """
        self.bus_num = bus
        self.address = address
        self.logger = logging.getLogger("tca9548a")
        self._bus: Optional[smbus2.SMBus] = None
        self._current_channel = None
        
    def _get_bus(self) -> smbus2.SMBus:
        """Get or create the I2C bus connection.
        
        Returns:
            SMBus instance
        """
        if self._bus is None:
            self._bus = smbus2.SMBus(self.bus_num)
        return self._bus
    
    def is_connected(self) -> bool:
        """Check if the TCA9548A is connected and responding.
        
        Returns:
            True if device responds, False otherwise
        """
        try:
            bus = self._get_bus()
            bus.read_byte(self.address)
            return True
        except Exception as e:
            self.logger.warning(f"TCA9548A not found: {e}")
            return False
    
    def select_channel(self, channel: int) -> None:
        """Select an I2C channel.
        
        Args:
            channel: Channel number (0-7)
            
        Raises:
            ValueError: If channel is out of range
            IOError: If communication fails
        """
        if not 0 <= channel < self.NUM_CHANNELS:
            raise ValueError(f"Channel must be 0-{self.NUM_CHANNELS-1}, got {channel}")
        
        try:
            bus = self._get_bus()
            # Write channel selection to control register
            # Each bit enables the corresponding channel (bit 0 = channel 0, etc.)
            bus.write_byte_data(self.address, self.CONTROL_REG, 1 << channel)
            self._current_channel = channel
            self.logger.debug(f"Selected channel {channel}")
        except Exception as e:
            self.logger.error(f"Failed to select channel {channel}: {e}")
            raise
    
    def get_current_channel(self) -> Optional[int]:
        """Get the currently selected channel.
        
        Returns:
            Current channel number (0-7) or None if not set
        """
        return self._current_channel
    
    def enable_all_channels(self) -> None:
        """Enable all I2C channels.
        
        This is useful for scanning all devices.
        """
        try:
            bus = self._get_bus()
            # Set all bits to enable all channels
            bus.write_byte_data(self.address, self.CONTROL_REG, 0xFF)
            self._current_channel = None
            self.logger.debug("All channels enabled")
        except Exception as e:
            self.logger.error(f"Failed to enable all channels: {e}")
            raise
    
    def disable_all_channels(self) -> None:
        """Disable all I2C channels."""
        try:
            bus = self._get_bus()
            bus.write_byte_data(self.address, self.CONTROL_REG, 0x00)
            self._current_channel = None
            self.logger.debug("All channels disabled")
        except Exception as e:
            self.logger.error(f"Failed to disable all channels: {e}")
            raise
    
    def close(self) -> None:
        """Close the I2C bus connection."""
        if self._bus is not None:
            self._bus.close()
            self._bus = None
            self.logger.debug("I2C bus closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def __repr__(self) -> str:
        return f"TCA9548A(bus={self.bus_num}, address=0x{self.address:02X})"
