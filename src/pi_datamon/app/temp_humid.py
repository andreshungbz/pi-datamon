import time

import adafruit_ahtx0  # type: ignore
import board  # type: ignore
import busio  # type: ignore

# I2C Address
AHT20_I2C_ADDR = 0x38


class AHT20:
    """AHT20/AHT21 driver using Adafruit Blinka."""

    # Datasheet: https://asairsensors.com/wp-content/uploads/2021/09/Data-Sheet-AHT20-Humidity-and-Temperature-Sensor-ASAIR-V1.0.03.pdf

    def __init__(self, bus_id: int, address: int = AHT20_I2C_ADDR):
        if bus_id != 1:
            raise ValueError("Adafruit Blinka uses Raspberry Pi I2C bus 1")

        self.bus_id = bus_id
        self.address = address
        self.bus = busio.I2C(board.SCL, board.SDA)
        time.sleep(0.5)

        self.sensor = None
        for attempt in range(3):
            try:
                self.sensor = adafruit_ahtx0.AHTx0(self.bus, address=self.address)
                break
            except Exception:
                if attempt == 2:
                    self.bus.deinit()
                    raise
                time.sleep(0.5)

    def read_metrics(self) -> tuple[float, float]:
        """Trigger a reading and return (temperature_celsius, relative_humidity_pct)."""
        if self.sensor is None:
            raise RuntimeError("AHT sensor is not initialized")
        try:
            return round(self.sensor.temperature, 1), round(
                self.sensor.relative_humidity, 1
            )
        except (OSError, RuntimeError):
            return float("nan"), float("nan")

    def close(self) -> None:
        """Close the I2C bus connection gracefully."""
        self.bus.deinit()
