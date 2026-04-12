"""Serial encoder interface for microcontroller-based encoder reading.

This module provides a SerialEncoder class that communicates with
a microcontroller (e.g., Teensy, ESP32) that reads the AS5600
encoders and sends the data via serial.

This is a placeholder for future implementation when switching
from Raspberry Pi I2C to a microcontroller-based approach.
"""

import serial
import time
from typing import Optional

from .encoder_interface import EncoderInterface, EncoderTimeoutError, EncoderNotFoundError


class SerialEncoder(EncoderInterface):
    """Serial encoder interface for microcontroller communication.
    
    This class reads encoder data from a microcontroller via serial
    communication. The microcontroller is responsible for reading the
    AS5600 encoders and sending the data to the Pi.
    
    Expected Serial Protocol:
        - Send command: "ANGLE\n" or "RAW\n"
        - Receive response: "1234\n" (raw value) or "1.2345\n" (angle in radians)
    
    Example Microcontroller Code (Arduino/Teensy):
        if (Serial.available()) {
            String cmd = Serial.readStringUntil('\n');
            if (cmd == "ANGLE") {
                Serial.println(encoder.readAngle(), 4);
            } else if (cmd == "RAW") {
                Serial.println(encoder.readRaw());
            }
        }
    
    Example:
        # Pi side
        encoder = SerialEncoder(name='hip', port='/dev/ttyUSB0', baud=115200)
        angle = encoder.read_angle()  # Reads from microcontroller
    """
    
    def __init__(
        self,
        name: str = "encoder",
        port: str = "/dev/ttyUSB0",
        baud: int = 115200,
        timeout: float = 1.0
    ):
        """Initialize serial encoder interface.
        
        Args:
            name: Descriptive name for this encoder
            port: Serial port device path
            baud: Baud rate (115200 is typical)
            timeout: Serial read timeout in seconds
        """
        super().__init__(name)
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None
        self._connected = False
    
    def _ensure_connection(self) -> None:
        """Ensure serial connection is open."""
        if self._serial is None or not self._serial.is_open:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=self.timeout
            )
            self._connected = True
            self.logger.info(f"{self.name}: Connected to {self.port}")
    
    def is_connected(self) -> bool:
        """Check if the serial connection is open.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            self._ensure_connection()
            return self._serial.is_open
        except Exception as e:
            self.logger.warning(f"{self.name}: Serial connection failed: {e}")
            return False
    
    def read_raw(self) -> int:
        """Read raw encoder value from microcontroller.
        
        Returns:
            Raw encoder value
            
        Raises:
            EncoderTimeoutError: If communication times out
            EncoderNotFoundError: If connection fails
        """
        try:
            self._ensure_connection()
            
            # Send raw command
            self._serial.write(b"RAW\n")
            self._serial.flush()
            
            # Read response
            response = self._serial.readline()
            
            if not response:
                raise EncoderTimeoutError(f"{self.name}: No response from microcontroller")
            
            # Parse integer value
            raw_value = int(response.decode().strip())
            return raw_value
            
        except serial.SerialException as e:
            self._connected = False
            raise EncoderNotFoundError(f"{self.name}: Serial error: {e}")
        except ValueError as e:
            raise EncoderTimeoutError(f"{self.name}: Invalid response: {response}")
    
    def read_angle(self) -> float:
        """Read angle in radians from microcontroller.
        
        Returns:
            Angle in radians
            
        Raises:
            EncoderTimeoutError: If communication times out
            EncoderNotFoundError: If connection fails
        """
        try:
            self._ensure_connection()
            
            # Send angle command
            self._serial.write(b"ANGLE\n")
            self._serial.flush()
            
            # Read response
            response = self._serial.readline()
            
            if not response:
                raise EncoderTimeoutError(f"{self.name}: No response from microcontroller")
            
            # Parse float value
            angle = float(response.decode().strip()) - self._offset
            return angle
            
        except serial.SerialException as e:
            self._connected = False
            raise EncoderNotFoundError(f"{self.name}: Serial error: {e}")
        except ValueError as e:
            raise EncoderTimeoutError(f"{self.name}: Invalid response: {response}")
    
    def calibrate(self) -> bool:
        """Run calibration on microcontroller.
        
        Note: The actual calibration is performed by the microcontroller.
        This sends the calibrate command and waits for completion.
        
        Returns:
            True if calibration succeeded
        """
        try:
            self._ensure_connection()
            
            # Send calibrate command
            self._serial.write(b"CALIBRATE\n")
            self._serial.flush()
            
            # Wait for response
            response = self._serial.readline()
            
            if response and b"OK" in response:
                self.logger.info(f"{self.name}: Calibration complete")
                return True
            else:
                self.logger.warning(f"{self.name}: Calibration may have failed")
                return False
                
        except Exception as e:
            self.logger.error(f"{self.name}: Calibration error: {e}")
            return False
    
    def send_position_command(self, position: float) -> bool:
        """Send position command to microcontroller.
        
        This is for sending commands TO the motor controller,
        not reading encoder values.
        
        Args:
            position: Target position in radians
            
        Returns:
            True if command sent successfully
        """
        try:
            self._ensure_connection()
            cmd = f"POS:{position:.4f}\n"
            self._serial.write(cmd.encode())
            self._serial.flush()
            return True
        except Exception as e:
            self.logger.error(f"{self.name}: Failed to send command: {e}")
            return False
    
    def close(self) -> None:
        """Close serial connection."""
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
            self.logger.info(f"{self.name}: Serial connection closed")
        self._connected = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
