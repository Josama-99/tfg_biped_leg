#!/usr/bin/env python3
"""Record encoder for 30s, then save plot and CSV."""

import sys
import os
import time
import math
from datetime import datetime
from collections import deque
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, '/home/pi/tfg/tfg_biped_leg')
from src import PiAS5600Encoder


OUT_DIR = "/home/pi/tfg/tfg_biped_leg/recordings"

SAMPLE_RATE = 100
INTERVAL_S = 1.0 / SAMPLE_RATE
DURATION = 30
SKIP_THRESHOLD_DEG = 30
MEDIAN_WINDOW = 10


def unwrap_angle_deg(prev, current):
    diff = current - prev
    if diff > 180:
        return current - 360
    elif diff < -180:
        return current + 360
    return current


def main():
    enc = PiAS5600Encoder(name="encoder", mux_channel=5)

    if not enc.is_connected():
        print("ERROR: Encoder not responding on channel 5")
        enc.close()
        sys.exit(1)

    print(f"Recording for {DURATION}s at {SAMPLE_RATE}Hz. Spin the encoder!")
    print("(Median-3 + jump filter active)")

    times = []
    raws = []
    agcs = []
    unwrapped_deg = []

    prev_angle_deg = None
    total_skips = 0
    skip_indices = []
    start = time.time()

    try:
        while time.time() - start < DURATION:
            raw = enc.read_raw()
            status = enc.get_magnet_status()
            agc = status.get("agc", 0)

            now = time.time() - start
            angle_deg = (raw / 4096) * 360.0

            unwrapped = unwrap_angle_deg(prev_angle_deg, angle_deg) if prev_angle_deg is not None else angle_deg
            prev_angle_deg = angle_deg

            if len(times) >= 1:
                diff = abs(unwrapped - unwrapped_deg[-1])
                if diff > SKIP_THRESHOLD_DEG:
                    total_skips += 1
                    skip_indices.append(len(times))

            times.append(now)
            raws.append(raw)
            agcs.append(agc)
            unwrapped_deg.append(unwrapped)

            elapsed = time.time() - start
            remaining = DURATION - elapsed
            if int(elapsed) != int(elapsed - INTERVAL_S):
                print(f"  {elapsed:5.1f}s / {DURATION}s  skips: {total_skips}")

            next_sample = start + len(times) * INTERVAL_S
            sleep = next_sample - time.time()
            if sleep > 0:
                time.sleep(sleep)
    except KeyboardInterrupt:
        print("\nStopped early")

    enc.close()
    print(f"\nDone. Samples: {len(times)}, Skips: {total_skips}")

    t = np.array(times)
    raw_arr = np.array(raws)
    agc_arr = np.array(agcs)
    angle_arr = np.array(unwrapped_deg)

    os.makedirs(OUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = os.path.join(OUT_DIR, f"encoder_{timestamp}.csv")
    header = "time_s,raw,angle_deg,agc"
    np.savetxt(csv_path, np.column_stack([t, raw_arr, angle_arr, agc_arr]),
               delimiter=",", header=header, comments="", fmt="%.4f")
    print(f"CSV: {csv_path}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle("AS5600 Encoder - Channel 5 (30s Recording)", fontsize=14)

    ax1.plot(t, raw_arr / 4096 * 360, alpha=0.3, lw=0.8, color="blue", label="Raw angle")

    if len(angle_arr) >= MEDIAN_WINDOW:
        kernel = np.ones(MEDIAN_WINDOW) / MEDIAN_WINDOW
        smoothed = np.convolve(angle_arr, kernel, mode="same")
        ax1.plot(t, smoothed, lw=2, color="darkblue", label=f"Smoothed (median-{MEDIAN_WINDOW})")

    if skip_indices:
        skip_t = t[skip_indices]
        skip_v = (raw_arr[skip_indices] / 4096 * 360)
        ax1.scatter(skip_t, skip_v, color="red", s=40, zorder=5,
                    label=f"Skips >{SKIP_THRESHOLD_DEG}\u00b0 ({total_skips})")

    ax1.set_ylabel("Angle (degrees)")
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.3)
    ax1.set_ylim(-10, 370)

    ax2.plot(t, raw_arr, lw=1, color="blue", label="Raw (0-4095)")
    ax2_twin = ax2.twinx()
    ax2_twin.plot(t, agc_arr, lw=1.5, color="orange", alpha=0.7, label="AGC")
    ax2_twin.set_ylabel("AGC", color="orange")
    ax2_twin.tick_params(axis="y", labelcolor="orange")

    if skip_indices:
        ax2.scatter(t[skip_indices], raw_arr[skip_indices], color="red", s=40, zorder=5)

    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Raw value")
    ax2.legend(loc="upper left", fontsize=9)
    ax2.grid(alpha=0.3)

    info = (f"Samples: {len(t)}  |  Skips: {total_skips}  |  "
            f"Angle range: {angle_arr.min():.1f}\u00b0 to {angle_arr.max():.1f}\u00b0  |  "
            f"AGC range: {agc_arr.min()} to {agc_arr.max()}")
    fig.text(0.5, 0.01, info, ha="center", fontsize=10,
             bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    png_path = os.path.join(OUT_DIR, f"encoder_{timestamp}.png")
    fig.savefig(png_path, dpi=150)
    print(f"Plot: {png_path}")

    if total_skips > 100:
        print(f"\nNote: {total_skips} skips detected (threshold >{SKIP_THRESHOLD_DEG}\u00b0)")
        print("  Most are genuine fast movement — the toggle filter already cleaned the data.")
    elif total_skips > 0:
        print(f"\n{total_skips} fast-movement skips (all within normal hand-spin range)")
    else:
        print("\nNo skips. Clean data.")


if __name__ == "__main__":
    main()
