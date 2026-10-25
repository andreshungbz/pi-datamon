# Print recipe list
default:
    @just --list --unsorted

# Run Pi Datamon
run:
    @uv run pi-datamon

# Format code with ruff
format:
    @ruff check --fix
