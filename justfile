# Print recipe list
default:
    @just --list --unsorted

# Run Pi Datamon App
run-sensors:
    @uv run pi-datamon-app

# Run Pi Datamon Visualization
run-visualization:
    @uv run pi-datamon-visualization

# Format code with ruff
format:
    @ruff check --fix

# Variables
PI_HOST := "andreshung@cmps4252-pi-4.local"
PI_LOG_DIR := "/home/andreshung/Projects/pi-datamon/log"
LOCAL_LOG_DIR := invocation_directory() + "/log"

# Mount the remote Pi log directory into local ./log (press Ctrl+C to unmount)
mount:
    @mkdir -p {{ LOCAL_LOG_DIR }}
    @echo "Ensuring remote log directory exists on Pi..."
    @ssh {{ PI_HOST }} "mkdir -p {{ PI_LOG_DIR }}"
    @echo "Mounting {{ PI_HOST }}:{{ PI_LOG_DIR }} to {{ LOCAL_LOG_DIR }}"
    @sshfs {{ PI_HOST }}:{{ PI_LOG_DIR }} {{ LOCAL_LOG_DIR }} \
        -f \
        -o reconnect \
        -o ServerAliveInterval=15 \
        -o ServerAliveCountMax=3 \
        -o defer_permissions

# Emergency cleanup if a mount hangs or isn't cleared by Ctrl+C
unmount:
    @echo "Cleaning up local mount point {{ LOCAL_LOG_DIR }}..."
    @diskutil unmount force {{ LOCAL_LOG_DIR }} 2>/dev/null || umount -f {{ LOCAL_LOG_DIR }} 2>/dev/null || true
    @echo "Unmounted."
