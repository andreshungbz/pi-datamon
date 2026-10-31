import time
from datetime import datetime
from zoneinfo import ZoneInfo

from gpiozero import Button  # type: ignore

from pi_datamon.app.distance import HCSR04
from pi_datamon.app.oled import SSD1306
from pi_datamon.app.temp_humid import AHT20
from pi_datamon.app.utils import (
    append_csv_row,
    get_repo_root,
    init_csv_writer,
)

# Default I2C Bus
I2C_BUS_ID = 1

# GPIO Pin Configuration
TRIG_PIN = 4
ECHO_PIN = 27
BUTTON_PIN = 26

# CSV Log Path Configuration
LOG_DIR = get_repo_root() / "log"
CSV_FILE_PATH = LOG_DIR / "sensor_log.csv"

# Program Configuration
POLLING_INTERVAL = 1.0
TIMEZONE = ZoneInfo("America/Belize")


def main() -> None:
    print("Initializing Pi-Datamon hardware...")

    # Initialize CSV log file.
    init_csv_writer(CSV_FILE_PATH)

    # Instantiate hardware interfaces for display and sensors.
    oled_display = SSD1306(bus_id=I2C_BUS_ID)
    temp_humid_sensor = AHT20(bus_id=I2C_BUS_ID)
    ultrasonic_sensor = HCSR04(trigger_pin=TRIG_PIN, echo_pin=ECHO_PIN)

    # Configure mode-cycling button.
    button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.05)
    button.when_pressed = oled_display.cycle_mode

    start_time = time.time()
    print(f"Logging metrics to {CSV_FILE_PATH}. Press Ctrl+C to exit.")
    try:
        # Main Program Loop
        while True:
            # Calculate Elapsed_Seconds.
            cycle_start = time.time()
            now = datetime.now(TIMEZONE)
            elapsed_seconds = cycle_start - start_time

            # Read Temperature_C and Humidity_Percent.
            try:
                temp_c, hum_pct = temp_humid_sensor.read_metrics()
            except OSError as e:
                print(f"Warning: Failed to read temperature/humidity: {e}")
                temp_c, hum_pct = float("nan"), float("nan")

            # Read Distance_cm.
            dist_cm = ultrasonic_sensor.read_distance_cm()

            # Append a new record to the CSV log file.
            iso_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            append_csv_row(
                CSV_FILE_PATH, iso_timestamp, elapsed_seconds, temp_c, hum_pct, dist_cm
            )

            # Render active sensor mode to the OLED display.
            oled_display.render(temperature=temp_c, humidity=hum_pct, distance=dist_cm)

            # Sleep for the remainder of the polling interval, accounting for execution time.
            elapsed_execution = time.time() - cycle_start
            sleep_duration = max(0.0, POLLING_INTERVAL - elapsed_execution)
            time.sleep(sleep_duration)
    except KeyboardInterrupt:
        print("\nStopping sensor collection cleanly...")
    finally:
        # Clean up and close hardware interfaces.
        oled_display.device.cleanup()
        temp_humid_sensor.close()
        ultrasonic_sensor.close()


if __name__ == "__main__":
    main()
