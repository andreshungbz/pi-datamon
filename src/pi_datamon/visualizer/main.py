"""
src/pi_datamon/visualizer/main.py

Real-time telemetry visualizer for pi-datamon sensor logs.
Monitors log/sensor_log.csv across local or SSHFS mounted filesystems and renders
animated subplots for Temperature, Humidity, and Distance using Matplotlib.
"""

import os
from pathlib import Path
from typing import Any

import matplotlib

# Force TkAgg backend before pyplot import to avoid Qt/PyQt wheel binding issues on Python 3.14
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import animation

from pi_datamon.common.console import console, print_introduction

# Dynamic absolute path resolution for reliable execution across working directories
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CSV_FILE_PATH = PROJECT_ROOT / "log" / "sensor_log.csv"

MAX_DISPLAY_POINTS = 60  # Rolling historical samples to render
UPDATE_INTERVAL_MS = 1000  # Redraw frequency in milliseconds

# Global animation reference to prevent Python garbage collection
_ani: animation.FuncAnimation | None = None


def main() -> None:
    global _ani

    # 1. Terminal Introduction
    print_introduction(
        color="cyan",
        title="pi-datamon/visualizer",
        description="Real-time data visualizer and time-series graphing for pi-datamon/app",
    )

    if not CSV_FILE_PATH.exists():
        console.print(
            f"[bold yellow]Waiting for log file to be created at [/bold yellow][cyan]{CSV_FILE_PATH}[/cyan]..."
        )

    # 2. Configure Matplotlib Dark Theme Figure and Subplots
    plt.style.use("dark_background")
    fig, (ax_temp, ax_hum, ax_dist) = plt.subplots(
        nrows=3, ncols=1, figsize=(10, 8), sharex=True
    )

    # Explicitly ignore typing on Matplotlib figure wrappers
    fig.suptitle(  # type: ignore[no-untyped-call]
        "pi-datamon Real-Time Telemetry Dashboard",
        fontsize=14,
        fontweight="bold",
        color="cyan",
    )

    # Compute static visual layout once before animation loop starts
    fig.tight_layout()

    def update_plots(_frame: int) -> None:
        """Callback executed every interval tick to fetch data and refresh subplots cleanly."""
        # SSHFS Protection: Ensure file exists and is not currently empty/locked
        if not CSV_FILE_PATH.exists() or os.path.getsize(CSV_FILE_PATH) == 0:
            return

        try:
            # Read CSV safely with pandas
            df = pd.read_csv(CSV_FILE_PATH)
            if df.empty or "iso_timestamp" not in df.columns:
                return

            # Keep last MAX_DISPLAY_POINTS rows
            recent_data = df.tail(MAX_DISPLAY_POINTS)
            timestamps: list[str] = recent_data["iso_timestamp"].to_list()

            # Clear previous axes to prevent overlay clutter
            ax_temp.cla()
            ax_hum.cla()
            ax_dist.cla()

            # Plot Temperature (°C)
            ax_temp.plot(
                timestamps,
                recent_data["temperature_c"],
                color="#ff7f0e",
                marker="o",
                markersize=3,
                linewidth=1.5,
            )
            ax_temp.set_ylabel("Temp (°C)", color="#ff7f0e", fontweight="bold")
            ax_temp.grid(True, linestyle="--", alpha=0.3)

            # Plot Humidity (%)
            ax_hum.plot(
                timestamps,
                recent_data["humidity_pct"],
                color="#1f77b4",
                marker="o",
                markersize=3,
                linewidth=1.5,
            )
            ax_hum.set_ylabel("Humidity (%)", color="#1f77b4", fontweight="bold")
            ax_hum.grid(True, linestyle="--", alpha=0.3)

            # Plot Distance (cm)
            ax_dist.plot(
                timestamps,
                recent_data["distance_cm"],
                color="#e377c2",
                marker="o",
                markersize=3,
                linewidth=1.5,
            )
            ax_dist.set_ylabel("Distance (cm)", color="#e377c2", fontweight="bold")
            ax_dist.set_xlabel("Timestamp", fontweight="bold")
            ax_dist.grid(True, linestyle="--", alpha=0.3)

            # Format bottom X-axis ticks cleanly without FixedFormatter warnings
            ax_dist.set_xticks(range(len(timestamps)))
            ax_dist.set_xticklabels(timestamps, rotation=45, ha="right", fontsize=8)

            # Reduce density if displaying max window points
            if len(timestamps) > 10:
                ax_dist.set_xticks(
                    range(0, len(timestamps), max(1, len(timestamps) // 8))
                )

        except (
            PermissionError,
            OSError,
            KeyError,
            ValueError,
            TypeError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
        ):
            # Soft fail on transient network delays, corrupt lines, or incomplete SSHFS file writes
            pass

    # 3. Attach Live Animation Loop to module-level reference
    _ani = animation.FuncAnimation(
        fig, update_plots, interval=UPDATE_INTERVAL_MS, cache_frame_data=False
    )

    console.print(
        "[bold green]Displaying live telemetry window... Press Ctrl+C or close window to exit.[/bold green]\n"
    )

    try:
        # Cast module to Any so normal property access bypasses overloaded signature checks
        plt_any: Any = plt
        plt_any.show()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Visualizer closed cleanly.[/bold yellow]")


if __name__ == "__main__":
    main()
