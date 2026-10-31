from typing import cast

from gpiozero import DistanceSensor  # type: ignore
from gpiozero.exc import DistanceSensorException  # type: ignore

# Default GPIO Pin Mapping (Raspberry Pi BCM numbering)
DEFAULT_TRIG_PIN = 4
DEFAULT_ECHO_PIN = 27
DEFAULT_MAX_DISTANCE = 4


class HCSR04:
    """Wrapper driver for the HC-SR04 ultrasonic distance sensor."""

    # Datasheet: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf

    def __init__(
        self,
        trigger_pin: int = DEFAULT_TRIG_PIN,
        echo_pin: int = DEFAULT_ECHO_PIN,
        max_distance: int = DEFAULT_MAX_DISTANCE,
    ):
        """Initialize HC-SR04 GPIO pins."""
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.max_distance = max_distance

        # Initialize gpiozero DistanceSensor backend.
        # Triggers 10us sonic pulses and calculates travel time (Distance = Speed of Sound * Time / 2).
        self.sensor = DistanceSensor(
            echo=self.echo_pin,
            trigger=self.trigger_pin,
            max_distance=int(self.max_distance),
        )

    def read_distance_cm(self) -> float:
        """Sample the sensor and return the measured distance in centimeters."""
        try:
            # gpiozero returns distance in meters (0.0 to max_distance).
            raw_val: object = self.sensor.distance  # type: ignore
            if raw_val is not None:
                distance_meters = float(cast(float, raw_val))
                return round(distance_meters * 100.0, 2)
            return float("nan")
        except OSError, DistanceSensorException:
            # Return NaN gracefully if sound echo fails to return or times out.
            return float("nan")

    def close(self) -> None:
        """Release underlying GPIO pins."""
        self.sensor.close()
