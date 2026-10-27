# Print recipe list
default:
    @just --list --unsorted

# Run Pi Datamon
run:
    @uv run pi-datamon

# Format code with ruff
format:
    @ruff check --fix

# Variables
PI_HOST := "andreshung@cmps4252-pi-4.local"
PI_LOG_DIR := "~/Projects/pi-datamon/log"
LOCAL_LOG_DIR := invocation_directory() + "/log"

# Mount the remote Pi log directory into local ./log
mount:
    @mkdir -p {{ LOCAL_LOG_DIR }}
    @if mountpoint -q {{ LOCAL_LOG_DIR }} 2>/dev/null; then \
        echo "Log directory is already mounted."; \
    else \
        echo "Ensuring remote log directory exists on Pi..."; \
        ssh {{ PI_HOST }} "mkdir -p {{ PI_LOG_DIR }}"; \
        echo "Mounting {{ PI_HOST }}:{{ PI_LOG_DIR }} to {{ LOCAL_LOG_DIR }}..."; \
        sshfs {{ PI_HOST }}:{{ PI_LOG_DIR }} {{ LOCAL_LOG_DIR }} \
            -o reconnect \
            -o ServerAliveInterval=15 \
            -o ServerAliveCountMax=3 \
            -o defer_permissions; \
        echo "Successfully mounted!"; \
    fi

# Unmount the local log directory
unmount:
    @if mountpoint -q {{ LOCAL_LOG_DIR }} 2>/dev/null || umount -q {{ LOCAL_LOG_DIR }} 2>/dev/null; then \
        echo "Unmounting {{ LOCAL_LOG_DIR }}..."; \
        umount {{ LOCAL_LOG_DIR }} 2>/dev/null || umount -f {{ LOCAL_LOG_DIR }} 2>/dev/null || diskutil unmount force {{ LOCAL_LOG_DIR }}; \
        echo "Successfully unmounted."; \
    else \
        echo "Log directory is not currently mounted."; \
    fi
