import csv
from pathlib import Path


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
    elapsed: float,
    temperature: float,
    humidity: float,
    distance: float,
) -> None:
    """Append a single row of sensor telemetry to the CSV log file."""
    with open(file_path, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([timestamp, f"{elapsed:.2f}", temperature, humidity, distance])
