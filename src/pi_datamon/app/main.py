"""
src/pi_datamon/app/main.py

Main orchestrator script for sensor acquisition, CSV logging, and OLED display output.
Polls AHT20 (I2C), HC-SR04 (GPIO), and SSD1306 (OLED) in a 1.0-second loop.
"""

import time
from datetime import UTC, datetime

from gpiozero import Button  # type: ignore

from pi_datamon.app.distance import HCSR04
from pi_datamon.app.oled import SSD1306
from pi_datamon.app.temp_humid import AHT20
from pi_datamon.app.utils import CSV_FILE_PATH, append_csv_row, init_csv_writer

# Hardware Configuration
I2C_BUS_ID = 1
TRIG_PIN = 4
ECHO_PIN = 27
BUTTON_PIN = 26

POLLING_INTERVAL = 1.0


def main() -> None:
    print("Initializing Pi-Datamon hardware...")

    # Prepare CSV Output Log File
    init_csv_writer(CSV_FILE_PATH)

    # Instantiate Hardware Drivers (Using exact hardware model names)
    aht20 = AHT20(bus_id=I2C_BUS_ID)
    hcsr04 = HCSR04(trigger_pin=TRIG_PIN, echo_pin=ECHO_PIN)
    display = SSD1306(bus_id=I2C_BUS_ID)

    # Configure Interrupt Button (Mode Switching)
    button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.05)
    button.when_pressed = display.cycle_mode

    start_time = time.time()
    print(f"Logging metrics to {CSV_FILE_PATH}. Press Ctrl+C to exit.")

    try:
        while True:
            cycle_start = time.time()
            now = datetime.now(UTC).astimezone()
            iso_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            elapsed_seconds = cycle_start - start_time

            # 1. Sample AHT20 Temperature and Humidity
            try:
                temp_c, hum_pct = aht20.read_metrics()
            except OSError as e:
                print(f"Warning: Failed to read AHT20 sensor: {e}")
                temp_c, hum_pct = float("nan"), float("nan")

            # 2. Sample HC-SR04 Distance Sensor
            dist_cm = hcsr04.read_distance_cm()

            # 3. Log Telemetry to CSV
            append_csv_row(
                CSV_FILE_PATH, iso_timestamp, elapsed_seconds, temp_c, hum_pct, dist_cm
            )

            # 4. Render Active Page to OLED Display
            display.render(temperature=temp_c, humidity=hum_pct, distance=dist_cm)

            # 5. Sleep to Maintain Sampling Rate
            elapsed_execution = time.time() - cycle_start
            sleep_duration = max(0.0, POLLING_INTERVAL - elapsed_execution)
            time.sleep(sleep_duration)

    except KeyboardInterrupt:
        print("\nStopping sensor collection cleanly...")
    finally:
        aht20.close()
        hcsr04.close()
        display.device.cleanup()


if __name__ == "__main__":
    main()
