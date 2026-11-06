"""Exercise sensor failures without importing Raspberry Pi hardware libraries."""

import importlib.util
import math
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, PropertyMock, call, patch


class AHT20Tests(unittest.TestCase):
    def setUp(self):
        self.driver = Mock()
        self.busio = Mock()
        modules = {
            "adafruit_ahtx0": self.driver,
            "board": SimpleNamespace(SCL=3, SDA=2),
            "busio": self.busio,
        }
        source = (
            Path(__file__).resolve().parents[1]
            / "src/pi_datamon/app/temp_humid.py"
        )
        spec = importlib.util.spec_from_file_location("temp_humid_under_test", source)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", modules):
            spec.loader.exec_module(self.module)
        self.sleep = patch.object(self.module.time, "sleep").start()
        self.warning = patch.object(self.module.logger, "warning").start()
        self.addCleanup(patch.stopall)
        self.good_sensor = SimpleNamespace(temperature=26.24, relative_humidity=63.87)
        self.driver.AHTx0.return_value = self.good_sensor

    def assert_missing(self, metrics):
        self.assertEqual(len(metrics), 2)
        self.assertTrue(all(math.isnan(value) for value in metrics))

    def test_initialization_retries_then_reads(self):
        self.driver.AHTx0.side_effect = [
            OSError(5, "Input/output error"),
            RuntimeError("Could not calibrate"),
            self.good_sensor,
        ]
        sensor = self.module.AHT20(bus_id=1)
        self.assertEqual(sensor.read_metrics(), (26.2, 63.9))
        self.assertEqual(self.driver.AHTx0.call_count, 3)
        self.assertEqual(self.sleep.call_args_list, [call(0.5)] * 3)
        self.warning.assert_not_called()

    def test_absent_at_startup_then_recovers(self):
        self.driver.AHTx0.side_effect = ValueError("No I2C device at address: 0x38")
        sensor = self.module.AHT20(bus_id=1)
        self.assertEqual(self.driver.AHTx0.call_count, 3)
        self.assert_missing(sensor.read_metrics())
        self.assert_missing(sensor.read_metrics())
        self.warning.assert_called_once()
        self.busio.I2C.return_value.deinit.assert_not_called()

        self.driver.AHTx0.side_effect = None
        self.assertEqual(sensor.read_metrics(), (26.2, 63.9))
        sensor.close()
        self.busio.I2C.return_value.deinit.assert_called_once()

    def test_failed_temperature_or_humidity_invalidates_both_and_reconnects(self):
        for property_name in ("temperature", "relative_humidity"):
            with self.subTest(property_name=property_name):
                broken = Mock(temperature=25.0, relative_humidity=60.0)
                setattr(
                    type(broken),
                    property_name,
                    PropertyMock(side_effect=OSError(5, "Input/output error")),
                )
                self.driver.AHTx0.side_effect = [broken, self.good_sensor]
                sensor = self.module.AHT20(bus_id=1)
                self.assert_missing(sensor.read_metrics())
                self.assertEqual(sensor.read_metrics(), (26.2, 63.9))

    def test_warning_reappears_for_a_new_outage_after_recovery(self):
        sensor = self.module.AHT20(bus_id=1)
        self.driver.AHTx0.side_effect = OSError(5, "Input/output error")
        sensor.sensor = None
        self.assert_missing(sensor.read_metrics())
        self.assert_missing(sensor.read_metrics())
        self.warning.assert_called_once()
        self.driver.AHTx0.side_effect = None
        self.assertEqual(sensor.read_metrics(), (26.2, 63.9))
        sensor.sensor = None
        self.driver.AHTx0.side_effect = RuntimeError("Could not calibrate")
        self.assert_missing(sensor.read_metrics())
        self.assertEqual(self.warning.call_count, 2)

    def test_unexpected_programming_errors_are_not_hidden(self):
        self.driver.AHTx0.side_effect = TypeError("bad driver argument")
        with self.assertRaises(TypeError):
            self.module.AHT20(bus_id=1)
        self.busio.I2C.return_value.deinit.assert_called_once()

    def test_unsupported_bus_rejected_before_opening_hardware(self):
        with self.assertRaises(ValueError):
            self.module.AHT20(bus_id=2)
        self.busio.I2C.assert_not_called()


if __name__ == "__main__":
    unittest.main()
