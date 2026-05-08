#!/usr/bin/env python3
"""Lee el encoder AS5600 conectado al canal 5 del multiplexor TCA9548A."""

import sys
import time
import math
sys.path.insert(0, '/home/pi/tfg/tfg_biped_leg')

from src import PiAS5600Encoder


def main():
    enc = PiAS5600Encoder(name="encoder", mux_channel=5)

    if not enc.is_connected():
        print("ERROR: No se detecta el encoder en el canal 5")
        print("  Verifica:")
        print("  1. Cableado (SDA, SCL, VCC, GND)")
        print("  2. I2C habilitado: sudo raspi-config")
        print("  3. Direccion del mux: sudo i2cdetect -y 1 (debe aparecer 0x70)")
        enc.close()
        sys.exit(1)

    print("Leyendo encoder en canal 5... (Ctrl+C para salir)")
    print(f"{'Angulo (rad)':>12} {'Angulo (grados)':>16} {'Raw':>6} {'Magnet':>6}")
    print("-" * 46)

    try:
        while True:
            raw = enc.read_raw()
            angle_rad = enc.read_angle()
            angle_deg = angle_rad * 180.0 / math.pi
            status = enc.get_magnet_status()
            magnet = "OK" if status.get("detected") else "NO"
            print(f"{angle_rad:12.4f} {angle_deg:16.2f} {raw:6d} {magnet:>6}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nDetenido")
    finally:
        enc.close()


if __name__ == "__main__":
    main()
