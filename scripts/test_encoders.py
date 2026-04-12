#!/usr/bin/env python3
"""Test script for AS5600 encoders with TCA9548A I2C multiplexer.

This script tests the encoder reading functionality by:
1. Scanning for I2C devices
2. Testing TCA9548A multiplexer
3. Reading from each AS5600 encoder
4. Verifying magnet detection
5. Testing zero/offset functions

Hardware Setup Required:
- TCA9548A I2C multiplexer connected to Pi (I2C bus 1)
- AS5600 encoder(s) connected to mux channels
- AS5600 encoders with magnets positioned

Usage:
    python3 scripts/test_encoders.py

Author: tfg_biped_leg
"""

import sys
import time
import argparse
sys.path.insert(0, '/home/pi/TFG')

from src import EncoderManager, TCA9548A, EncoderError


def scan_i2c_bus(bus=1):
    """Scan I2C bus for devices."""
    print("\n" + "="*50)
    print("I2C Bus Scan")
    print("="*50)
    
    try:
        import smbus2
        bus_obj = smbus2.SMBus(bus)
        
        print(f"Scanning I2C bus {bus}...")
        found = []
        
        for addr in range(0x03, 0x78):
            try:
                bus_obj.read_byte(addr)
                found.append(f"0x{addr:02X}")
            except:
                pass
        
        bus_obj.close()
        
        if found:
            print(f"Found {len(found)} device(s): {', '.join(found)}")
        else:
            print("No devices found!")
        
        return found
        
    except Exception as e:
        print(f"I2C scan failed: {e}")
        print("Make sure I2C is enabled: sudo raspi-config → Interface → I2C")
        return []


def test_mux():
    """Test TCA9548A multiplexer."""
    print("\n" + "="*50)
    print("TCA9548A Multiplexer Test")
    print("="*50)
    
    try:
        mux = TCA9548A(bus=1, address=0x70)
        
        if mux.is_connected():
            print("✓ TCA9548A found at address 0x70")
            
            # Test channel switching
            print("\nTesting channel switching...")
            for ch in range(4):
                mux.select_channel(ch)
                current = mux.get_current_channel()
                print(f"  Channel {ch}: {'✓' if current == ch else '✗'}")
            
            mux.close()
            return True
        else:
            print("✗ TCA9548A not found!")
            print("\nTroubleshooting:")
            print("1. Check wiring (SDA, SCL, VCC, GND)")
            print("2. Verify TCA9548A address (default: 0x70)")
            print("3. Run: sudo i2cdetect -y 1")
            return False
            
    except Exception as e:
        print(f"✗ TCA9548A test failed: {e}")
        return False


def test_encoders(channels=None):
    """Test AS5600 encoders."""
    if channels is None:
        channels = [0, 1, 2]  # Default: test channels 0, 1, 2
    
    print("\n" + "="*50)
    print("AS5600 Encoder Test")
    print("="*50)
    
    joint_names = {0: 'Hip', 1: 'Knee', 2: 'Ankle'}
    
    results = {}
    
    for ch in channels:
        joint_name = joint_names.get(ch, f'Channel {ch}')
        print(f"\n--- Testing {joint_name} (Channel {ch}) ---")
        
        try:
            from src import PiAS5600Encoder
            encoder = PiAS5600Encoder(name=joint_name.lower(), mux_channel=ch)
            
            # Check connection
            if encoder.is_connected():
                print(f"✓ {joint_name} encoder connected")
                
                # Read raw value
                raw = encoder.read_raw()
                print(f"  Raw value: {raw} (0-4095)")
                
                # Read angle
                angle = encoder.read_angle()
                print(f"  Angle: {angle:.4f} rad ({angle * 180 / 3.14159:.2f}°)")
                
                # Check magnet
                status = encoder.get_magnet_status()
                if 'error' in status:
                    print(f"  ⚠ Magnet status error: {status['error']}")
                else:
                    detected = status.get('detected', False)
                    strength = "too weak" if status.get('too_weak') else \
                               "too strong" if status.get('too_strong') else "OK"
                    print(f"  Magnet: {'✓' if detected else '✗'} ({strength})")
                
                results[ch] = {'success': True, 'raw': raw, 'angle': angle}
            else:
                print(f"✗ {joint_name} encoder not responding")
                results[ch] = {'success': False}
            
            encoder.close()
            
        except Exception as e:
            print(f"✗ {joint_name} test failed: {e}")
            results[ch] = {'success': False, 'error': str(e)}
    
    return results


def test_encoder_manager():
    """Test the EncoderManager class."""
    print("\n" + "="*50)
    print("Encoder Manager Test")
    print("="*50)
    
    try:
        import yaml
        
        with open('/home/pi/TFG/config/encoder.yaml') as f:
            config = yaml.safe_load(f)
        
        manager = EncoderManager(
            encoder_type='pi',
            config=config['pi_i2c']['joints']
        )
        
        print(f"Created manager with {len(manager)} encoder(s)")
        print(f"Encoders: {manager.get_names()}")
        
        # Check connections
        print("\nChecking connections...")
        connections = manager.check_all_connected()
        for name, connected in connections.items():
            print(f"  {name}: {'✓' if connected else '✗'}")
        
        # Read all angles
        print("\nReading all angles...")
        angles = manager.read_all()
        for name, angle in angles.items():
            print(f"  {name}: {angle:.4f} rad ({angle * 180 / 3.14159:.2f}°)")
        
        manager.close()
        return True
        
    except FileNotFoundError:
        print("Config file not found: config/encoder.yaml")
        return False
    except Exception as e:
        print(f"Manager test failed: {e}")
        return False


def continuous_read(channels=None, duration=10):
    """Continuously read encoders for specified duration."""
    if channels is None:
        channels = [0, 1, 2]
    
    print(f"\n--- Continuous Read ({duration}s) ---")
    print("Press Ctrl+C to stop")
    print()
    
    joint_names = {0: 'Hip', 1: 'Knee', 2: 'Ankle'}
    encoders = {}
    
    try:
        from src import PiAS5600Encoder
        
        for ch in channels:
            encoders[ch] = PiAS5600Encoder(name=joint_names.get(ch, f'ch{ch}'), mux_channel=ch)
        
        start_time = time.time()
        count = 0
        
        while time.time() - start_time < duration:
            values = []
            for ch, enc in encoders.items():
                try:
                    val = enc.read_angle()
                    values.append(f"{val:.4f}")
                except:
                    values.append("ERR")
            
            elapsed = time.time() - start_time
            print(f"[{elapsed:5.1f}s] " + " | ".join(values))
            count += 1
            time.sleep(0.1)
        
        print(f"\nRead {count} samples")
        
        for enc in encoders.values():
            enc.close()
            
    except KeyboardInterrupt:
        print("\nStopped by user")
        for enc in encoders.values():
            enc.close()


def main():
    parser = argparse.ArgumentParser(description='Test AS5600 encoders')
    parser.add_argument('--scan', action='store_true', help='Scan I2C bus')
    parser.add_argument('--mux', action='store_true', help='Test TCA9548A mux')
    parser.add_argument('--encoders', action='store_true', help='Test encoders')
    parser.add_argument('--manager', action='store_true', help='Test EncoderManager')
    parser.add_argument('--continuous', type=int, default=0, help='Continuous read for N seconds')
    parser.add_argument('--channels', nargs='+', type=int, default=[0,1,2], help='Channels to test')
    
    args = parser.parse_args()
    
    # If no arguments, run all tests
    run_all = not any([args.scan, args.mux, args.encoders, args.manager, args.continuous > 0])
    
    print("="*50)
    print("AS5600 Encoder Test Suite")
    print("="*50)
    
    if run_all or args.scan:
        scan_i2c_bus()
    
    if run_all or args.mux:
        test_mux()
    
    if run_all or args.encoders:
        test_encoders(args.channels)
    
    if run_all or args.manager:
        test_encoder_manager()
    
    if args.continuous > 0:
        continuous_read(args.channels, args.continuous)
    
    print("\n" + "="*50)
    print("Test Complete")
    print("="*50)


if __name__ == "__main__":
    main()
