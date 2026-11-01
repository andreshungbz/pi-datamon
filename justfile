# ==================================================================================== #
# VARIABLES
# ==================================================================================== #

PI_HOST := "andreshung@cmps4252-pi-4.local"
PI_LOG_DIR := "/home/andreshung/Projects/pi-datamon/log"
LOCAL_LOG_DIR := invocation_directory() + "/log"

# ==================================================================================== #
# GENERAL
# ==================================================================================== #

# Show recipe list.
default:
    @just --list --unsorted

# Show project information.
info:
    @uv run python -c "from pi_datamon.common.console import print_introduction; print_introduction('yellow')"

# ==================================================================================== #
# PROGRAM
# ==================================================================================== #

# Run Pi Datamon (should be run on the Pi).
run:
    @uv run pi-datamon-app

# Run Pi Datamon Visualizer (should be run on the local machine).
visualize:
    @uv run pi-datamon-visualizer

# Run Pi Datamon Simulator.
simulate:
    @uv run pi-datamon-simulator

# ==================================================================================== #
# DEVELOPMENT
# ==================================================================================== #

# Check and fix code with ruff.
check:
    @ruff check --select I --fix

# Clear log directory and file.
cleanup:
    rm -rf log/

# ==================================================================================== #
# FILESYSTEM
# ==================================================================================== #

# Mount the Pi's log directory from remote.
mount:
    @mkdir -p {{ LOCAL_LOG_DIR }}
    @ssh {{ PI_HOST }} "mkdir -p {{ PI_LOG_DIR }}"
    @echo "Mounting {{ PI_HOST }}:{{ PI_LOG_DIR }} to {{ LOCAL_LOG_DIR }}"
    @sshfs {{ PI_HOST }}:{{ PI_LOG_DIR }} {{ LOCAL_LOG_DIR }} \
        -f \
        -o reconnect \
        -o ServerAliveInterval=15 \
        -o ServerAliveCountMax=3 \
        -o cache=no \
        -o cache_timeout=1 \
        -o defer_permissions

# Emergency mount cleanup (MacOS).
unmount-macos:
    diskutil unmount force {{ LOCAL_LOG_DIR }} 2>/dev/null || umount -f {{ LOCAL_LOG_DIR }} 2>/dev/null || true
