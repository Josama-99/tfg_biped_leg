#!/usr/bin/env python3
"""Calibration tool for AS5600 encoder + ODrive motor control.

Records raw encoder values at 3 manual positions (limit min, middle, limit max),
then auto-calibrates ODrive motor positions at the physical limits, and
oscillates the joint safely within the calibrated range.

Usage:
    sudo /home/pi/tfg/tfg_biped_leg/tfg_venv/bin/python3 scripts/calibrate_encoder.py
"""

import sys
import math
import time
sys.path.insert(0, '/home/pi/tfg/tfg_biped_leg')

from src import PiAS5600Encoder


MUX_CHANNEL = 5
JOINT_NAME = "joint_1"
CONFIG_PATH = "/home/pi/tfg/tfg_biped_leg/config/encoder_calibration.yaml"

SAFETY_MARGIN = 100
STALL_VEL_THRESHOLD = 0.01
STALL_TIMEOUT = 2.0
ENCODER_RANGE = 4096

AXIS_STATE_FULL_CALIB = 3
AXIS_STATE_IDLE = 1
AXIS_STATE_CLOSED_LOOP = 8
CTRL_MODE_POSITION = 3
RAMP_STEP = 0.03
RAMP_INTERVAL = 0.2


def raw_distance(current, target):
    d = (target - current) % ENCODER_RANGE
    if d > ENCODER_RANGE // 2:
        d -= ENCODER_RANGE
    return d


def is_near_limit(current, limit, margin=SAFETY_MARGIN):
    if limit is None:
        return False
    return abs(raw_distance(current, limit)) <= margin


def load_calibration():
    import yaml
    try:
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError):
        return None


def save_calibration(limit_min, limit_mid, limit_max,
                     motor_pos_min=None, motor_pos_max=None,
                     margin=SAFETY_MARGIN):
    import yaml
    import datetime

    rng = abs(raw_distance(limit_min, limit_max)) if None not in (limit_min, limit_max) else None

    data = {
        "calibration": {
            "joint_name": JOINT_NAME,
            "mux_channel": MUX_CHANNEL,
            "limit_min": limit_min,
            "limit_mid": limit_mid,
            "limit_max": limit_max,
            "motor_pos_min": motor_pos_min,
            "motor_pos_max": motor_pos_max,
            "margin": margin,
            "range": rng,
            "timestamp": datetime.datetime.now().isoformat(),
        }
    }

    with open(CONFIG_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False)

    print(f"\n  ✓ Saved calibration to {CONFIG_PATH}")


def read_encoder(enc):
    try:
        enc.reset_filter()
        raw = enc.read_raw()
        enc.reset_filter()
        angle = enc.read_angle()
        deg = angle * 180.0 / math.pi
        return raw, deg
    except Exception:
        return None, None


def connect_odrive():
    import odrive
    print("Connecting to ODrive...")
    try:
        dev = odrive.find_any()
        print(f"  Connected! Serial: {dev.serial_number}")
        dev.clear_errors()

        print("  Calibrating motor (axis1)...")
        dev.axis1.requested_state = AXIS_STATE_FULL_CALIB
        while dev.axis1.current_state != AXIS_STATE_IDLE:
            time.sleep(0.1)
        print("  Calibration complete.")

        dev.axis1.requested_state = AXIS_STATE_CLOSED_LOOP
        time.sleep(0.3)

        dev.axis1.controller.config.control_mode = CTRL_MODE_POSITION
        dev.axis1.controller.input_pos = dev.axis1.encoder.pos_estimate
        print("  Closed-loop + position control enabled.")
        return dev
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return None


def detect_motor_direction(enc, odrv, limit_min, limit_max):
    """Probe motor direction using position control — command +0.5 turns, check encoder."""
    before_raw, _ = read_encoder(enc)
    if before_raw is None:
        print("  ✗ Cannot read encoder for direction probe.")
        return None

    for attempt in (1, -1):
        start_pos = odrv.axis1.encoder.pos_estimate
        odrv.axis1.controller.input_pos = start_pos + attempt * 0.5
        time.sleep(1.5)

        after_raw, _ = read_encoder(enc)
        if after_raw is None:
            continue

        delta = abs(raw_distance(before_raw, after_raw))
        if delta < 5:
            print(f"  Motor didn't move (dir={attempt:+d}), trying opposite...")
            odrv.axis1.controller.input_pos = start_pos
            time.sleep(0.3)
            continue

        dist_before = abs(raw_distance(before_raw, limit_min))
        dist_after = abs(raw_distance(after_raw, limit_min))
        toward_min = dist_after < dist_before

        odrv.axis1.controller.input_pos = start_pos
        time.sleep(0.5)

        label = "min" if toward_min else "max"
        print(f"  Direction: +motor → limit_{label}")
        return toward_min

    print("  ✗ Cannot determine direction — motor not responding.")
    return None


def approach_any_limit(enc, odrv, limit_min, limit_max, direction_sign):
    """Ramp in direction_sign, stop when EITHER limit is approached or stall."""
    ramp_pos = odrv.axis1.encoder.pos_estimate
    stall_start = None
    reached = False
    hit_label = None

    while True:
        raw, _ = read_encoder(enc)
        if raw is not None:
            if is_near_limit(raw, limit_min):
                hit_label = 'min'
                reached = True
                break
            if is_near_limit(raw, limit_max):
                hit_label = 'max'
                reached = True
                break

        vel = abs(odrv.axis1.encoder.vel_estimate)
        if vel < STALL_VEL_THRESHOLD:
            if stall_start is None:
                stall_start = time.time()
            elif time.time() - stall_start > STALL_TIMEOUT:
                if raw is not None:
                    d_min = abs(raw_distance(raw, limit_min))
                    d_max = abs(raw_distance(raw, limit_max))
                    hit_label = 'min' if d_min < d_max else 'max'
                break
        else:
            stall_start = None

        ramp_pos += direction_sign * RAMP_STEP
        odrv.axis1.controller.input_pos = ramp_pos
        time.sleep(RAMP_INTERVAL)

    motor_pos = odrv.axis1.encoder.pos_estimate
    return motor_pos, hit_label, reached


def auto_calibrate(enc, odrv, limit_min, limit_max):
    print("\n" + "=" * 60)
    print("Auto-calibrate: discovering ODrive motor positions at limits")
    print("=" * 60)
    print("  Motor will move slowly in both directions.")
    print("  Ctrl+C to abort.\n")

    try:
        toward_min = detect_motor_direction(enc, odrv, limit_min, limit_max)
        if toward_min is None:
            return None, None

        first_sign = 1 if toward_min else -1
        print(f"\n  Moving toward first limit...")
        pos1, label1, reached1 = approach_any_limit(enc, odrv, limit_min, limit_max, first_sign)
        print(f"  limit_{label1} → motor: {pos1:.4f} turns "
              f"({'reached' if reached1 else 'STALL'})")

        second_sign = -1 * first_sign
        print(f"\n  Moving toward second limit...")
        pos2, label2, reached2 = approach_any_limit(enc, odrv, limit_min, limit_max, second_sign)
        print(f"  limit_{label2} → motor: {pos2:.4f} turns "
              f"({'reached' if reached2 else 'STALL'})")

        odrv.axis1.controller.input_pos = odrv.axis1.encoder.pos_estimate

        motor_pos_min = pos1 if label1 == 'min' else pos2 if label2 == 'min' else None
        motor_pos_max = pos2 if label2 == 'max' else pos1 if label1 == 'max' else None

        if None in (motor_pos_min, motor_pos_max):
            print("  ⚠ Could not determine both motor limits.")
            return None, None

        print(f"\n  ✅ Motor limits: min={motor_pos_min:.4f}, max={motor_pos_max:.4f}")
        return motor_pos_min, motor_pos_max

    except KeyboardInterrupt:
        print("\n  ⚠ Aborted by user.")
        odrv.axis1.controller.input_pos = odrv.axis1.encoder.pos_estimate
        return None, None


def oscillate(odrv, pos_min, pos_max, cycles=0, speed=1.0):
    odrv.axis1.controller.config.control_mode = CTRL_MODE_POSITION
    odrv.axis1.controller.config.vel_limit = speed

    count = 0
    travel_time = abs(pos_max - pos_min) / speed
    print(f"\n  Oscillating: {pos_min:.2f} ↔ {pos_max:.2f} turns (speed={speed} turns/s)")
    print("  Ctrl+C to stop.\n")

    try:
        while cycles == 0 or count < cycles:
            count += 1

            odrv.axis1.controller.input_pos = pos_min
            time.sleep(travel_time * 0.6)

            odrv.axis1.controller.input_pos = pos_max
            time.sleep(travel_time * 0.6)

    except KeyboardInterrupt:
        print("\n  Oscillation stopped.")


def show_status(enc, odrv, limit_min, limit_mid, limit_max,
                motor_pos_min, motor_pos_max):
    raw, deg = read_encoder(enc)
    if raw is not None:
        print(f"  Current: RAW={raw:5d}  ({deg:7.2f}°)")
    else:
        print("  Current: (read error)")

    if odrv is not None:
        try:
            mp = odrv.axis1.encoder.pos_estimate
            print(f"  Motor:   {mp:+.4f} turns")
        except Exception:
            print("  Motor:   (error)")

    print()
    for label, val in [("Limit 1 (min)", limit_min), ("Middle", limit_mid),
                       ("Limit 2 (max)", limit_max)]:
        if val is not None and raw is not None:
            d = raw_distance(raw, val)
            print(f"  {label:14s}: {val:5d}  (Δ={d:+4d})")
        elif val is not None:
            print(f"  {label:14s}: {val:5d}")

    if limit_min is not None and limit_max is not None:
        rng = abs(raw_distance(limit_min, limit_max))
        print(f"  Range:         {rng:5d}")

    if motor_pos_min is not None or motor_pos_max is not None:
        print()
    if motor_pos_min is not None:
        print(f"  Motor limit min: {motor_pos_min:+.4f} turns")
    if motor_pos_max is not None:
        print(f"  Motor limit max: {motor_pos_max:+.4f} turns")


def main():
    enc = PiAS5600Encoder(name=JOINT_NAME, mux_channel=MUX_CHANNEL)

    if not enc.is_connected():
        print(f"ERROR: No encoder detected on mux channel {MUX_CHANNEL}")
        enc.close()
        sys.exit(1)

    limit_min = None
    limit_mid = None
    limit_max = None
    motor_pos_min = None
    motor_pos_max = None
    odrv = None

    existing = load_calibration()
    if existing:
        cal = existing.get("calibration", {})
        if cal.get("mux_channel") == MUX_CHANNEL:
            limit_min = cal.get("limit_min")
            limit_mid = cal.get("limit_mid")
            limit_max = cal.get("limit_max")
            motor_pos_min = cal.get("motor_pos_min")
            motor_pos_max = cal.get("motor_pos_max")
            print(f"Loaded existing calibration for {JOINT_NAME} (ch{MUX_CHANNEL})")

    print(f"\nEncoder Calibration — {JOINT_NAME} (mux channel {MUX_CHANNEL})")
    print("First record limits by hand, then connect ODrive and auto-calibrate.")
    print()

    while True:
        print("=" * 55)
        show_status(enc, odrv, limit_min, limit_mid, limit_max,
                    motor_pos_min, motor_pos_max)
        print()
        print("  1  — Record Limit 1 (min)")
        print("  2  — Record Middle")
        print("  3  — Record Limit 2 (max)")
        print("  s  — Show recorded values")
        print("  c  — Clear all recorded values")
        print("  w  — Save to YAML")
        if odrv is not None:
            print("  d  — Disconnect ODrive")
            print("  p  — Move motor to position (turns)")
            print("  +  — Step +0.1 turns")
            print("  -  — Step -0.1 turns")
            if limit_min is not None and limit_max is not None:
                print("  a  — Auto-calibrate motor limits")
            if motor_pos_min is not None and motor_pos_max is not None:
                print("  o  — Oscillate between limits")
        else:
            print("  m  — Connect to ODrive")
        print("  q  — Quit")
        print()

        choice = input("Select option: ").strip().lower()

        if choice == "1":
            enc.reset_filter()
            raw, _ = read_encoder(enc)
            if raw is not None:
                limit_min = raw
                motor_pos_min = None
                print(f"\n  → Limit 1 (min) = {limit_min}")
            else:
                print("\n  ⚠ Failed to read encoder")
        elif choice == "2":
            enc.reset_filter()
            raw, _ = read_encoder(enc)
            if raw is not None:
                limit_mid = raw
                print(f"\n  → Middle = {limit_mid}")
            else:
                print("\n  ⚠ Failed to read encoder")
        elif choice == "3":
            enc.reset_filter()
            raw, _ = read_encoder(enc)
            if raw is not None:
                limit_max = raw
                motor_pos_max = None
                print(f"\n  → Limit 2 (max) = {limit_max}")
            else:
                print("\n  ⚠ Failed to read encoder")
        elif choice == "s":
            print()
            print("  Recorded values:")
            print(f"    Limit 1 (min): {limit_min}")
            print(f"    Middle:        {limit_mid}")
            print(f"    Limit 2 (max): {limit_max}")
            if limit_min is not None and limit_max is not None:
                print(f"    Range:         {abs(raw_distance(limit_min, limit_max))}")
            if motor_pos_min is not None:
                print(f"    Motor min:     {motor_pos_min:+.4f}")
            if motor_pos_max is not None:
                print(f"    Motor max:     {motor_pos_max:+.4f}")
        elif choice == "c":
            limit_min = None
            limit_mid = None
            limit_max = None
            motor_pos_min = None
            motor_pos_max = None
            enc.reset_filter()
            print("\n  → All values cleared")
        elif choice == "w":
            if None in (limit_min, limit_mid, limit_max):
                print("\n  ⚠ Record all 3 positions before saving.")
            else:
                save_calibration(limit_min, limit_mid, limit_max,
                                 motor_pos_min, motor_pos_max)
        elif choice == "m":
            if odrv is None:
                odrv = connect_odrive()
            else:
                print("  ODrive already connected.")
        elif choice == "d":
            if odrv is not None:
                odrv.axis1.controller.config.control_mode = CTRL_MODE_POSITION
                odrv.axis1.controller.input_pos = odrv.axis1.encoder.pos_estimate
                odrv = None
                print("\n  → ODrive disconnected.")
            else:
                print("  No ODrive connected.")
        elif choice == "p":
            if odrv is None:
                print("\n  ⚠ Connect ODrive first (m).")
            else:
                try:
                    val = float(input("  Position (turns): "))
                    odrv.axis1.controller.config.control_mode = CTRL_MODE_POSITION
                    odrv.axis1.controller.input_pos = val
                    print(f"  → Moving to {val:.4f} turns")
                except ValueError:
                    print("  ⚠ Invalid number.")
        elif choice == "+":
            if odrv is None:
                print("\n  ⚠ Connect ODrive first (m).")
            else:
                current = odrv.axis1.encoder.pos_estimate
                odrv.axis1.controller.config.control_mode = CTRL_MODE_POSITION
                odrv.axis1.controller.input_pos = current + 0.1
                print(f"  → Step +0.1 → {current+0.1:.4f}")
        elif choice == "-":
            if odrv is None:
                print("\n  ⚠ Connect ODrive first (m).")
            else:
                current = odrv.axis1.encoder.pos_estimate
                odrv.axis1.controller.config.control_mode = CTRL_MODE_POSITION
                odrv.axis1.controller.input_pos = current - 0.1
                print(f"  → Step -0.1 → {current-0.1:.4f}")
        elif choice == "a":
            if odrv is None:
                print("\n  ⚠ Connect ODrive first (m).")
            elif None in (limit_min, limit_max):
                print("\n  ⚠ Record limits 1 and 3 first.")
            else:
                mp_min, mp_max = auto_calibrate(enc, odrv, limit_min, limit_max)
                if mp_min is not None and mp_max is not None:
                    motor_pos_min = mp_min
                    motor_pos_max = mp_max
                    save_calibration(limit_min, limit_mid, limit_max,
                                     motor_pos_min, motor_pos_max)
        elif choice == "o":
            if odrv is None:
                print("\n  ⚠ Connect ODrive first (m).")
            elif motor_pos_min is None or motor_pos_max is None:
                print("\n  ⚠ Run auto-calibrate first (a).")
            else:
                speed = 1.0
                try:
                    s = input("  Speed (turns/s, default=1.0): ").strip()
                    if s:
                        speed = float(s)
                except ValueError:
                    pass
                cycles = 0
                try:
                    c = input("  Cycles (Enter=infinite): ").strip()
                    if c:
                        cycles = int(c)
                except ValueError:
                    pass
                oscillate(odrv, motor_pos_min, motor_pos_max, cycles, speed)
        elif choice == "q":
            print("Exiting.")
            break
        else:
            print("Invalid option.")

    if odrv is not None:
        odrv.axis1.controller.config.control_mode = CTRL_MODE_POSITION
        odrv.axis1.controller.input_pos = odrv.axis1.encoder.pos_estimate
    enc.close()


if __name__ == "__main__":
    main()
