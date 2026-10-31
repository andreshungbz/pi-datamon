import os
import platform

import matplotlib

# Select matplotlib backend based on the operating system.
if platform.system() == "Darwin":
    matplotlib.use("MacOSX")
else:
    matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import animation

from pi_datamon.common.console import console, print_introduction
from pi_datamon.common.utils import get_repo_root

# CSV Log Path Configuration
LOG_DIR = get_repo_root() / "log"
CSV_FILE_PATH = LOG_DIR / "sensor_log.csv"

# Visualizer Configuration
VIEW_WINDOW_WIDTH = 30
POLL_INTERVAL_MS = 500

# Color Palette Configuration
BG_COLOR = "#ffffff"
TEXT_COLOR_DARK = "#111111"
TICK_COLOR = "#333333"
GRID_COLOR = "#bbbbbb"
COLOR_TEMP = "#1f77b4"
COLOR_HUM = "#2ca02c"
COLOR_DIST = "#d62728"

# Typography & Sizing Configuration
FONT_SIZE_MAIN_TITLE = 24
FONT_SIZE_SUBPLOT_TITLE = 14
FONT_SIZE_AXIS_LABEL = 12
FONT_SIZE_TICKS = 10
LINE_WIDTH = 1.8
MARKER_SIZE = 4

# Layout & Spacing Configuration
FIG_RECT_LAYOUT = (0.0, 0.0, 0.94, 0.94)
SUPTITLE_Y_POSITION = 0.94

# Global State Variables
_ani: animation.FuncAnimation | None = None  # Matplotlib animation object
_start_row_index: int | None = None  # Index of the first row to display
_last_row_count: int = 0  # Last known row count


def main() -> None:
    global _ani, _start_row_index, _last_row_count

    print_introduction(
        color="cyan",
        title="pi-datamon/visualizer",
        description="Real-time data visualizer and time-series graphing for pi-datamon/app",
    )

    if not CSV_FILE_PATH.exists():
        console.print(
            f"[bold yellow]Waiting for log file at [/bold yellow][cyan]{CSV_FILE_PATH}[/cyan]..."
        )
    else:
        # Record initial row count.
        try:
            initial_df = pd.read_csv(CSV_FILE_PATH)
            _start_row_index = len(initial_df)
            _last_row_count = _start_row_index
        except (
            PermissionError,
            OSError,
            KeyError,
            ValueError,
            TypeError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
        ):
            _start_row_index = 0
            _last_row_count = 0

    # Instantiate Matplotlib figure and subplots for temperature, humidity, and distance.
    plt.style.use("default")
    fig, (ax_temp, ax_hum, ax_dist) = plt.subplots(
        # Stack 3 subplots vertically, sharing the X-axis for elapsed time.
        nrows=3,
        ncols=1,
        figsize=(10, 8),
        sharex=True,
    )

    # Set main title.
    fig.suptitle(  # type: ignore
        "Pi Datamon Real-Time Log Visualization",
        fontsize=FONT_SIZE_MAIN_TITLE,
        fontweight="bold",
        color=TEXT_COLOR_DARK,
        y=SUPTITLE_Y_POSITION,
    )

    # Set canvas and subplot background colors.
    fig.patch.set_facecolor(BG_COLOR)
    for ax in (ax_temp, ax_hum, ax_dist):
        ax.set_facecolor(BG_COLOR)

    # Enable X-axis tick labels for all subplots despite shared X-axis.
    for ax in (ax_temp, ax_hum, ax_dist):
        ax.tick_params(labelbottom=True, colors=TICK_COLOR, labelsize=FONT_SIZE_TICKS)

    # Set temperature subplot.
    ax_temp.set_title(
        "Temperature Over Time",
        color=COLOR_TEMP,
        fontsize=FONT_SIZE_SUBPLOT_TITLE,
        loc="center",
        fontweight="bold",
        pad=6,
    )
    ax_temp.set_ylabel(
        "Temperature (°C)",
        color=COLOR_TEMP,
        fontweight="bold",
        fontsize=FONT_SIZE_AXIS_LABEL,
    )
    ax_temp.set_xlabel(
        "Elapsed Time (s)",
        fontweight="bold",
        color=TICK_COLOR,
        fontsize=FONT_SIZE_AXIS_LABEL,
    )
    ax_temp.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)

    # Set humidity subplot.
    ax_hum.set_title(
        "Humidity Over Time",
        color=COLOR_HUM,
        fontsize=FONT_SIZE_SUBPLOT_TITLE,
        loc="center",
        fontweight="bold",
    )
    ax_hum.set_ylabel(
        "Humidity (%)",
        color=COLOR_HUM,
        fontweight="bold",
        fontsize=FONT_SIZE_AXIS_LABEL,
    )
    ax_hum.set_xlabel(
        "Elapsed Time (s)",
        fontweight="bold",
        color=TICK_COLOR,
        fontsize=FONT_SIZE_AXIS_LABEL,
    )
    ax_hum.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)

    # Set distance subplot.
    ax_dist.set_title(
        "Distance Over Time",
        color=COLOR_DIST,
        fontsize=FONT_SIZE_SUBPLOT_TITLE,
        loc="center",
        fontweight="bold",
    )
    ax_dist.set_ylabel(
        "Distance (cm)",
        color=COLOR_DIST,
        fontweight="bold",
        fontsize=FONT_SIZE_AXIS_LABEL,
    )
    ax_dist.set_xlabel(
        "Elapsed Time (s)",
        fontweight="bold",
        color=TICK_COLOR,
        fontsize=FONT_SIZE_AXIS_LABEL,
    )
    ax_dist.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)

    # Initialize persistent line objects for each subplot.
    (line_temp,) = ax_temp.plot(
        [],
        [],
        color=COLOR_TEMP,
        marker="o",
        markersize=MARKER_SIZE,
        linewidth=LINE_WIDTH,
    )
    (line_hum,) = ax_hum.plot(
        [],
        [],
        color=COLOR_HUM,
        marker="o",
        markersize=MARKER_SIZE,
        linewidth=LINE_WIDTH,
    )
    (line_dist,) = ax_dist.plot(
        [],
        [],
        color=COLOR_DIST,
        marker="o",
        markersize=MARKER_SIZE,
        linewidth=LINE_WIDTH,
    )

    # Automatically adjust layout to prevent overlap of titles, labels, and ticks.
    fig.tight_layout(rect=FIG_RECT_LAYOUT)

    # Group all axes.
    all_axes = (ax_temp, ax_hum, ax_dist)

    # Readjust X-axis tick labels dynamically whenever pan/zoom occurs.

    def on_xlims_changed(_ax: plt.Axes) -> None:  # type: ignore[name-defined]
        """Dynamic callback that adjusts integer tick labels whenever pan/zoom occurs."""
        x_min, x_max = ax_dist.get_xlim()
        visible_ticks = np.linspace(x_min, x_max, num=6)  # type: ignore
        tick_labels = [f"{round(v)}" for v in visible_ticks]  # type: ignore

        for ax in all_axes:
            ax.set_xticks(visible_ticks)
            ax.set_xticklabels(
                tick_labels, rotation=0, ha="center", fontsize=FONT_SIZE_TICKS
            )

    ax_dist.callbacks.connect("xlim_changed", on_xlims_changed)

    # Define the update function for the animation loop.

    def update_plots(_frame: int) -> None:
        """Callback executed on poll interval."""
        global _start_row_index, _last_row_count

        # Check if the CSV file exists and is not empty.
        if not CSV_FILE_PATH.exists() or os.path.getsize(CSV_FILE_PATH) == 0:
            return

        try:
            # Read CSV file and determine the last row.
            df = pd.read_csv(CSV_FILE_PATH)
            current_row_count = len(df)

            # Return if no new rows have been appended.
            if current_row_count == _last_row_count or df.empty:
                return

            # Initialize baseline row index on first valid read if unassigned.
            if _start_row_index is None:
                _start_row_index = max(0, current_row_count - 1)

            # Filter data to all entries captured strictly after start.
            full_session_data = df.iloc[_start_row_index:].copy()
            if full_session_data.empty:
                _last_row_count = current_row_count
                return

            # Normalize column names to lowercase.
            col_map = {col.lower(): col for col in full_session_data.columns}

            # Retrieve the actual column names for elapsed time, temperature, humidity, and distance.
            elapsed_col = col_map.get("elapsed_seconds")
            temp_col = col_map.get("temperature_c")
            hum_col = col_map.get("humidity_percent") or col_map.get("humidity_pct")
            dist_col = col_map.get("distance_cm")

            # Return if any of the required columns are missing.
            if not all([temp_col, hum_col, dist_col]):
                return

            # Clean and sanitize numeric conversions across all historical points.
            temp_series = (
                pd.to_numeric(full_session_data[temp_col], errors="coerce")
                .ffill()
                .bfill()
                .fillna(0.0)
            )
            hum_series = (
                pd.to_numeric(full_session_data[hum_col], errors="coerce")
                .ffill()
                .bfill()
                .fillna(0.0)
            )
            dist_series = (
                pd.to_numeric(full_session_data[dist_col], errors="coerce")
                .ffill()
                .bfill()
                .fillna(0.0)
            )
            temp_vals = temp_series.to_numpy()
            hum_vals = hum_series.to_numpy()
            dist_vals = dist_series.to_numpy()

            # Extract X-axis values from Elapsed_Seconds.
            if elapsed_col and elapsed_col in full_session_data.columns:
                elapsed_series = pd.to_numeric(
                    full_session_data[elapsed_col], errors="coerce"
                ).fillna(0.0)
                x_vals = elapsed_series.to_numpy()
                x_labels = [str(int(v)) for v in x_vals]
            else:
                # Safety fallback if the column is ever missing or corrupted.
                x_vals = np.arange(len(temp_vals), dtype=float)
                x_labels = [str(i) for i in range(len(temp_vals))]

            # Return if there are no valid X-axis values to plot.
            if len(x_vals) == 0:
                return

            # Mutate the line objects with the latest data for each subplot.
            line_temp.set_data(x_vals, temp_vals)
            line_hum.set_data(x_vals, hum_vals)
            line_dist.set_data(x_vals, dist_vals)

            # Limit X-axis scroll view.
            x_max = float(x_vals[-1])
            if len(x_vals) > VIEW_WINDOW_WIDTH:
                x_min = float(x_vals[-VIEW_WINDOW_WIDTH])
            else:
                x_min = float(x_vals[0])

            x_margin = 0.5
            for ax in all_axes:
                ax.set_xlim(x_min - x_margin, x_max + x_margin)

            # Scale Y-axis limits dynamically.
            visible_slice = slice(-VIEW_WINDOW_WIDTH, None)
            for ax, vals in zip(all_axes, (temp_vals, hum_vals, dist_vals)):
                vis_vals = vals[visible_slice]
                if len(vis_vals) > 0:
                    v_min, v_max = float(np.min(vis_vals)), float(np.max(vis_vals))
                    y_margin = (v_max - v_min) * 0.1 if v_max != v_min else 1.0
                    ax.set_ylim(v_min - y_margin, v_max + y_margin)

            # Isolate visible X-axis values and labels for tick placement.
            vis_x_vals = x_vals[visible_slice]
            vis_x_labels = x_labels[visible_slice]

            # Prevent overcrowding of X-axis tick labels by selecting a subset based on the number of visible points.
            step = max(1, len(vis_x_vals) // 6)
            tick_positions = vis_x_vals[::step]
            tick_labels = [vis_x_labels[i] for i in range(0, len(vis_x_labels), step)]

            # Apply the calculated tick positions and labels to all subplots.
            for ax in all_axes:
                ax.set_xticks(tick_positions)
                ax.set_xticklabels(
                    tick_labels, rotation=0, ha="center", fontsize=FONT_SIZE_TICKS
                )

            # Queue redraw, activating when a new row is appended.
            fig.canvas.draw_idle()  # type: ignore

            _last_row_count = current_row_count
        except (
            PermissionError,
            OSError,
            KeyError,
            ValueError,
            TypeError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
        ):
            # Gracefully handle any exceptions that may arise during file reading or data processing.
            # e.g., permission issues, missing columns, malformed CSV data.
            pass

    console.print(
        f"Visualizing [cyan]{CSV_FILE_PATH}[/cyan]. Press [bold red]Ctrl+C[/bold red] or close the window to exit."
    )

    # Attach the update function to the Matplotlib animation loop.
    _ani = animation.FuncAnimation(
        fig, update_plots, interval=POLL_INTERVAL_MS, cache_frame_data=False
    )

    try:
        # Start the Matplotlib event loop.
        plt.show()  # type: ignore[reportUnknownMemberType]
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Visualizer stopped.[/bold yellow]")


if __name__ == "__main__":
    main()
