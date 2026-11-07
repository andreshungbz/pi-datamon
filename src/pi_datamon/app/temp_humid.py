import logging
import time

import adafruit_ahtx0  # type: ignore
import board  # type: ignore
import busio  # type: ignore

# I2C Address
AHT21_I2C_ADDR = 0x38

# Logger
logger = logging.getLogger(__name__)


class AHT21:
    """AHT21 driver using Adafruit Blinka."""

    # Datasheet: https://asairsensors.com/wp-content/uploads/2021/09/Data-Sheet-AHT20-Humidity-and-Temperature-Sensor-ASAIR-V1.0.03.pdf

    def __init__(self, bus_id: int, address: int = AHT21_I2C_ADDR):
        # Assert Adafruit Blinkda I2C bus 1.
        if bus_id != 1:
            raise ValueError("Adafruit Blinka uses Raspberry Pi I2C bus 1")

        self.bus_id = bus_id
        self.address = address
        self.bus = busio.I2C(board.SCL, board.SDA)
        time.sleep(0.5)

        # Initialize the AHT21 sensor with retry logic to handle transient I2C errors.
        self.sensor = None
        self._unavailable = False
        for attempt in range(3):
            try:
                self.sensor = adafruit_ahtx0.AHTx0(self.bus, address=self.address)
                break
            except (OSError, RuntimeError, ValueError) as error:
                if attempt == 2:
                    self._report_error(error)
                else:
                    time.sleep(0.5)
            except Exception:
                self.bus.deinit()
                raise

    def _report_error(self, error: Exception) -> None:
        """Warn once per outage rather than printing on every polling cycle."""
        if not self._unavailable:
            logger.warning(
                "AHT sensor at 0x%02X unavailable (%s); retrying next sample.",
                self.address,
                error,
            )
        self._unavailable = True

    def read_metrics(self) -> tuple[float, float]:
        """Return (temperature_celsius, relative_humidity_pct), or NaNs on failure."""
        try:
            if self.sensor is None:
                self.sensor = adafruit_ahtx0.AHTx0(self.bus, address=self.address)
            metrics = (
                round(self.sensor.temperature, 1),
                round(self.sensor.relative_humidity, 1),
            )
        except (OSError, RuntimeError, ValueError) as error:
            # Reinitialize after a failed transaction on the next polling cycle.
            self.sensor = None
            self._report_error(error)
            return float("nan"), float("nan")
        self._unavailable = False
        return metrics

    def close(self) -> None:
        """Close the I2C bus connection gracefully."""
        self.bus.deinit()
