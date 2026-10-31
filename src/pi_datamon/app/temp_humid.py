import time

import smbus2  # type: ignore

# I2C Address
AHT20_I2C_ADDR = 0x38


class AHT20:
    """Low-level driver for AHT20 Temperature & Humidity sensor via smbus2."""

    # Datasheet: https://asairsensors.com/wp-content/uploads/2021/09/Data-Sheet-AHT20-Humidity-and-Temperature-Sensor-ASAIR-V1.0.03.pdf

    def __init__(self, bus_id: int, address: int = AHT20_I2C_ADDR):
        self.bus_id = bus_id
        self.address = address
        # Initialize the I2C bus connection using smbus2.
        self.bus = smbus2.SMBus(self.bus_id)
        time.sleep(0.1)
        self._initialize_sensor()

    def _initialize_sensor(self) -> None:
        """Sends the initialization command (0xBE) if necessary."""
        # Read the 1-byte status register to check the calibration bit (Bit 3).
        status = self.bus.read_byte(self.address)
        if not (status & 0x08):  # 00001000
            # Send the 0xBE Initialization/Calibrate command with data parameters [0x08, 0x00].
            # This loads factory calibration coefficients into RAM.
            self.bus.write_i2c_block_data(self.address, 0xBE, [0x08, 0x00])
            time.sleep(0.01)

    def read_metrics(self) -> tuple[float, float]:
        """Trigger a reading and return (temperature_celsius, relative_humidity_pct)."""
        # Send the 0xAC Measurement Trigger command with data parameters [0x33, 0x00]
        # This instructs the ASIC to sample MEMS (Micro-Electro-Mechanical Systems) sens.ors.
        self.bus.write_i2c_block_data(self.address, 0xAC, [0x33, 0x00])
        time.sleep(0.08)  # Wait 80ms for measurement completion.

        # Read 7 raw data bytes.
        # Byte Index: [0]      [1]        [2]       [3]                 [4]        [5]        [6]
        # Contents:   [Status] [Hum High] [Hum Mid] [Hum Low/Temp High] [Temp Mid] [Temp Low] [CRC]
        # Bit Width:  8 bits   8 bits     8 bits    4 / 4 bits          8 bits     8 bits     8 bits
        data = self.bus.read_i2c_block_data(self.address, 0x00, 7)

        # Extract the 20-bit raw humidity result.
        # 1. Shift Byte 1 left by 16 bits:                         [ H19 H18 H17 H16 H15 H14 H13 H12 | 00000000 | 00000000 ]
        # 2. Shift Byte 2 left by 8 bits, OR with previous result: [ H19 H18 H17 H16 H15 H14 H13 H12 | H11 H10 H9 H8 H7 H6 H5 H4 | 00000000 ]
        # 3. OR previous result with Byte 3:                       [ H19 H18 H17 H16 H15 H14 H13 H12 | H11 H10 H9 H8 H7 H6 H5 H4 | H3 H2 H1 H0 T19 T18 T17 T16 ]
        # 4. Shift previous result right by 4 bits:                [ H19 H18 H17 H16 H15 H14 H13 H12 | H11 H10 H9 H8 H7 H6 H5 H4 | H3 H2 H1 H0 ]
        raw_humidity = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4

        # Extract the 20-bit raw temperature result.
        # 1. Mask Byte 3 with 0x0F and shift left by 16 bits: [ T19 T18 T17 T16 | 00000000 | 00000000 ]
        # 2. OR with Byte 4 and Byte 5:                       [ T19 T18 T17 T16 | T15 T14 T13 T12 T11 T10 T9 T8 | T7 T6 T5 T4 T3 T2 T1 T0 ]
        raw_temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]

        # Convert and return relative humidity percentage and temperature in Celsius.
        # Relative Humidity RH (%) = (S_rh / 2^20) * 100
        # Temperature T (°C)       = ((S_t / 2^20) * 200) - 50
        humidity = (raw_humidity / 1048576.0) * 100.0
        temperature = ((raw_temp / 1048576.0) * 200.0) - 50.0
        return round(temperature, 2), round(humidity, 2)

    def close(self) -> None:
        """Close the I2C bus connection gracefully."""
        self.bus.close()
