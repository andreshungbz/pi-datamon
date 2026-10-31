import math
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from rich.live import Live

from pi_datamon.common.console import console, print_introduction
from pi_datamon.common.utils import (
    append_csv_row,
    get_repo_root,
    init_csv_writer,
    make_status_table,
)

# CSV Log Path Configuration
LOG_DIR = get_repo_root() / "log"
CSV_FILE_PATH = LOG_DIR / "sensor_log.csv"

# Program Configuration
POLLING_INTERVAL = 1.0
TIMEZONE = ZoneInfo("America/Belize")

# Simulation Baselines
TEMP_BASE = 24.0  # °C
TEMP_STEP = 0.2
HUM_BASE = 50.0  # %
HUM_STEP = 0.5
DIST_BASE = 15.0  # cm
DIST_STEP = 0.8


def main() -> None:
    print_introduction(
        color="magenta",
        title="pi-datamon/simulator",
        description="Simulator for populating sensor_log.csv with mock sensor data",
    )

    # Initialize CSV log file.
    init_csv_writer(CSV_FILE_PATH)

    start_time = time.time()
    console.print(
        f"Logging to {CSV_FILE_PATH}. Press [bold red]Ctrl+C[/bold red] to exit."
    )

    temp = TEMP_BASE
    hum = HUM_BASE
    dist = DIST_BASE
    try:
        # Create initial status layout.
        now = datetime.now(TIMEZONE)
        iso_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        initial_table = make_status_table(
            iso_timestamp, 0, temp, hum, dist, mode="Simulator"
        )

        with Live(initial_table, console=console, refresh_per_second=4) as live:
            while True:
                # Calculate Elapsed_Seconds.
                cycle_start = time.time()
                now = datetime.now(TIMEZONE)
                elapsed_seconds = math.floor(cycle_start - start_time)

                # Generate simulated values.
                temp = round(
                    max(15.0, min(35.0, temp + random.uniform(-TEMP_STEP, TEMP_STEP))),
                    1,
                )
                hum = round(
                    max(30.0, min(80.0, hum + random.uniform(-HUM_STEP, HUM_STEP))),
                    1,
                )
                dist = round(
                    max(2.0, min(400.0, dist + random.uniform(-DIST_STEP, DIST_STEP))),
                    1,
                )

                # Append a new record to the CSV log file.
                iso_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                append_csv_row(
                    CSV_FILE_PATH,
                    iso_timestamp,
                    elapsed_seconds,
                    temp,
                    hum,
                    dist,
                )

                # Refresh the terminal display.
                live.update(
                    make_status_table(
                        iso_timestamp,
                        elapsed_seconds,
                        temp,
                        hum,
                        dist,
                        mode="Simulator",
                    )
                )

                # Sleep for the remainder of the polling interval, accounting for execution time.
                elapsed_execution = time.time() - cycle_start
                sleep_duration = max(0.0, POLLING_INTERVAL - elapsed_execution)
                time.sleep(sleep_duration)
    except KeyboardInterrupt:
        console.print("[bold yellow]Stopping simulator...[/bold yellow]")


if __name__ == "__main__":
    main()
