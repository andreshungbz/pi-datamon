from typing import cast

from gpiozero import DistanceSensor  # type: ignore
from gpiozero.exc import DistanceSensorNoEcho, GPIOZeroError  # type: ignore

# Ultrasonic Sensor Configuration
MAX_DISTANCE = 4


class HCSR04:
    """Wrapper driver for the HC-SR04 ultrasonic distance sensor."""

    # Datasheet: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf

    def __init__(
        self,
        trigger_pin: int,
        echo_pin: int,
        max_distance: int = MAX_DISTANCE,
    ):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.max_distance = max_distance

        # Initialize the underlying gpiozero DistanceSensor.
        self.sensor = DistanceSensor(
            echo=self.echo_pin,
            trigger=self.trigger_pin,
            max_distance=self.max_distance,
        )

    def read_distance_cm(self) -> float:
        """Sample distance and return centimeters, or NaN if out-of-range."""
        try:
            raw_val: object = self.sensor.distance  # type: ignore
            if raw_val is not None:
                distance_meters = cast(float, raw_val)
                return round(distance_meters * 100.0, 2)
            return float("nan")
        except OSError, DistanceSensorNoEcho, GPIOZeroError:
            return float("nan")

    def close(self) -> None:
        """Release underlying GPIO pins."""
        self.sensor.close()
