import csv
from pathlib import Path

from rich import box
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

MODE_LABELS: dict[int, str] = {
    0: "Temperature",
    1: "Humidity",
    2: "Distance",
}


def get_repo_root() -> Path:
    """Find repository root by searching upward for pyproject.toml."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


def init_csv_writer(file_path: Path) -> None:
    """Ensure output directory and CSV headers exist."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists() or file_path.stat().st_size == 0:
        with open(file_path, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                [
                    "Timestamp",
                    "Elapsed_Seconds",
                    "Temperature_C",
                    "Humidity_Percent",
                    "Distance_cm",
                ]
            )


def append_csv_row(
    file_path: Path,
    timestamp: str,
    elapsed: int,
    temperature: float,
    humidity: float,
    distance: float,
) -> None:
    """Append a single row of sensor telemetry to the CSV log file."""
    with open(file_path, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                timestamp,
                elapsed,
                f"{temperature:.1f}",
                f"{humidity:.1f}",
                f"{distance:.1f}",
            ]
        )


def make_status_table(
    timestamp: str,
    elapsed: int,
    temp: float,
    hum: float,
    dist: float,
    mode: int | str = 0,
) -> Table:
    """Generate a compact Rich table for live terminal display during polling/simulation."""
    # Determine mode label based on input type (int or str).
    if isinstance(mode, int):
        mode_str = MODE_LABELS.get(mode, "All Sensors")
    else:
        mode_str = mode

    # Create live spinner for mode label.
    mode_header = Table.grid(padding=(0, 1))
    mode_header.add_column(justify="left")
    mode_header.add_column(justify="left")
    mode_header.add_row(
        Spinner("dots", style="bold green"),
        Text("Mode", style="white"),
    )

    # Create and configure Rich table.
    table = Table(
        box=box.SQUARE,
        show_lines=True,
        padding=(0, 1, 0, 1),
        show_header=True,
    )
    table.add_column(mode_header, style="bold green", justify="left")
    table.add_column("Timestamp", style="white", justify="center")
    table.add_column("Elapsed (s)", style="cyan", justify="right")
    table.add_column("Temp (°C)", style="yellow", justify="right")
    table.add_column("Humidity (%)", style="blue", justify="right")
    table.add_column("Distance (cm)", style="magenta", justify="right")

    # Add row.
    table.add_row(
        mode_str,
        timestamp,
        f"{elapsed}",
        f"{temp:.1f}",
        f"{hum:.1f}",
        f"{dist:.1f}",
    )
    return table
