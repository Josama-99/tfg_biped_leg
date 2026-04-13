#!/usr/bin/env python3
"""
ODrive Interactive Test Menu

Hardware:
- ODrive v3.6 (Official)
- Motor: D5065 270KV
- Axis: 1 (or configurable)

Usage:
    python3 scripts/odrive_test.py

Note: Run with sudo if you have USB permission issues.
"""

from tfg_biped_leg.odrive_interface import IOdrive
from tfg_biped_leg.odrive_enums import ControlMode


def main():
    print("Connecting to ODrive...")
    odrv = IOdrive()
    print("Connected!\n")

    while True:
        print("=== ODrive Test Menu ===")
        print("1. Print errors")
        print("2. Print current config")
        print("3. Set default config")
        print("4. Set custom config (velocity_limit=7)")
        print("5. Save config")
        print("6. Enable closed loop control")
        print("7. Set control mode (TORQUE)")
        print("8. Set control mode (POSITION)")
        print("9. Set reference (torque/position)")
        print("10. Start live position plot")
        print("0. Exit")
        print()

        choice = input("Select option: ").strip()

        if choice == "1":
            odrv.print_odrive_errors_nb()
        elif choice == "2":
            odrv.print_config()
        elif choice == "3":
            odrv.set_default_config()
            print("Default config set.")
        elif choice == "4":
            custom_config = odrv.get_config()
            custom_config["velocity_limit"] = 7
            odrv.set_config(custom_config)
            print("Custom config set (velocity_limit=7).")
        elif choice == "5":
            odrv.save_config()
            print("Config saved.")
        elif choice == "6":
            odrv.enable_closed_loop()
            print("Closed loop control enabled.")
        elif choice == "7":
            odrv.control_mode = ControlMode.TORQUE_CONTROL
            print("Control mode set to TORQUE.")
        elif choice == "8":
            odrv.control_mode = ControlMode.POSITION_CONTROL
            print("Control mode set to POSITION.")
        elif choice == "9":
            print("=== Set Reference (torque/position) ===")
            print("Enter a value, or press Enter to go back, or 'q' to quit")
            while True:
                mode = input("Enter value: ").strip()
                if mode.lower() in ('q', 'quit', 'exit', ''):
                    print("Exiting reference mode.")
                    break
                try:
                    value = float(mode)
                    odrv.reference = value
                    print(f"Reference set to {value}.")
                except ValueError:
                    print("Invalid value. Try again.")
        elif choice == "10":
            print("Starting live plot (close window to stop)...")
            odrv.start_encoder_live_plot(odrv.get_current_pos)
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid option.")
        print()


if __name__ == "__main__":
    main()