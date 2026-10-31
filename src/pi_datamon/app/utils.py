import csv
from pathlib import Path

from PIL import ImageDraw


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
    if not file_path.exists():
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


def draw_thermometer_icon(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Draw a 16x16 pixel thermometer icon at position (x, y)."""
    # Outer stem and fluid bulb.
    draw.rectangle((x + 6, y + 1, x + 9, y + 10), outline=255, fill=0)
    draw.ellipse((x + 4, y + 9, x + 11, y + 15), outline=255, fill=255)
    # Internal liquid core.
    draw.line((x + 7, y + 4, x + 7, y + 10), fill=255)
    # Tick marks on the side.
    draw.line((x + 10, y + 3, x + 12, y + 3), fill=255)
    draw.line((x + 10, y + 6, x + 12, y + 6), fill=255)


def draw_droplet_icon(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Draw a 16x16 pixel raindrop/humidity icon at position (x, y)."""
    # Lower rounded water body.
    draw.ellipse((x + 3, y + 5, x + 12, y + 15), outline=255, fill=255)
    # Pointed top vertex lines.
    draw.line((x + 7, y + 1, x + 3, y + 7), fill=255)
    draw.line((x + 8, y + 1, x + 12, y + 7), fill=255)


def draw_sonar_icon(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Draw a 16x16 pixel ultrasonic/distance icon at position (x, y)."""
    # Central transducer dot.
    draw.ellipse((x + 1, y + 6, x + 5, y + 10), outline=255, fill=255)
    # Expanding acoustic wave arcs.
    draw.arc((x + 1, y + 2, x + 10, y + 14), start=300, end=60, fill=255)
    draw.arc((x + 1, y - 1, x + 15, y + 17), start=300, end=60, fill=255)
