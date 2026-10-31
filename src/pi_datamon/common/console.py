from rich import box
from rich.console import Console
from rich.markup import escape
from rich.table import Table

# Shared console instance.
console = Console()


DEFAULT_TITLE = "pi-datamon"
DEFAULT_DESCRIPTION = "Data acquisition and monitoring system for temperature, humidity, and distance using a Raspberry Pi"
DEFAULT_REPO_URL = "https://github.com/andreshungbz/pi-datamon"


def print_introduction(
    color: str = "yellow",
    title: str = DEFAULT_TITLE,
    description: str = DEFAULT_DESCRIPTION,
    repo_url: str = DEFAULT_REPO_URL,
) -> None:
    """Print project metadata and repository links."""
    # Create and configure a Rich table.
    table = Table(
        show_header=False, box=box.SQUARE, show_lines=True, padding=(0, 1, 0, 1)
    )
    table.add_column("Label", style=color, justify="center")
    table.add_column("Value", style="white")

    # Add rows
    table.add_row(escape(f"{title}"), description)
    table.add_row(escape("GitHub"), repo_url)

    console.print(table)
    console.print()
