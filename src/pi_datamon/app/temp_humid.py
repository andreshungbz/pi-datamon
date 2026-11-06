import adafruit_ahtx0  # type: ignore
import board  # type: ignore

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
        self.bus = board.I2C()
        self.sensor = adafruit_ahtx0.AHTx0(self.bus, address=self.address)

    def read_metrics(self) -> tuple[float, float]:
        """Trigger a reading and return (temperature_celsius, relative_humidity_pct)."""
        return round(self.sensor.temperature, 1), round(
            self.sensor.relative_humidity, 1
        )

    def close(self) -> None:
        """Close the I2C bus connection gracefully."""
        self.bus.deinit()
