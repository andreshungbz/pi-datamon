import math
from typing import cast

from luma.core.interface.serial import i2c  # type: ignore
from luma.oled.device import ssd1306  # type: ignore
from PIL import Image, ImageDraw, ImageFont

# Default I2C Bus and Monochrome OLED Address Configuration
# Note: PCB silkscreens often list 0x78 (the 8-bit shifted I2C write address).
# Linux kernel I2C drivers use standard 7-bit addressing: 0x78 >> 1 = 0x3C.
I2C_BUS_ID = 1
SSD1306_I2C_ADDR = 0x3C


class SSD1306:
    """Handles 128x64 monochrome SSD1306 OLED canvas rendering and menu navigation."""

    # Datasheet: https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf

    def __init__(self, bus_id: int = I2C_BUS_ID, address: int = SSD1306_I2C_ADDR):
        # Initialize luma.core I2C serial transport wrapper.
        serial_interface = i2c(port=bus_id, address=address)
        # Initialize SSD1306 display controller.
        self.device = ssd1306(serial_interface)
        # Retrieve display canvas dimensions (128 pixels wide x 64 pixels high).
        self.size: tuple[int, int] = cast(
            tuple[int, int],
            self.device.size,  # type: ignore
        )
        # Active menu mode index (0: Temperature, 1: Humidity, 2: Distance).
        self.mode = 0
        # Load default bitmap fonts for header titles and numerical metrics.
        self.font_title = ImageFont.load_default()
        self.font_data = ImageFont.load_default()

    def cycle_mode(self) -> None:
        """Cycle through display pages sequentially in a loop (0 -> 1 -> 2 -> 0)."""
        self.mode = (self.mode + 1) % 3

    def render(self, temperature: float, humidity: float, distance: float) -> None:
        """Draw active page layout to PIL image buffer and push to SSD1306 GDDRAM."""
        # Create a blank 1-bit monochrome image buffer in RAM (Mode '1': 0=Black, 255=White).
        # Dimensions: 128x64 pixels (1,024 bytes total memory footprint)
        image = Image.new("1", self.size, 0)
        draw = ImageDraw.Draw(image)

        if self.mode == 0:
            # Page 0: Temperature View
            draw.text((0, 0), "TEMP MONITOR", font=self.font_title, fill=255)
            draw.line((0, 12, 128, 12), fill=255)  # Separator line at Y=12
            draw.text(
                (0, 24),
                f"Temperature: {temperature:.1f} C",
                font=self.font_data,
                fill=255,
            )
        elif self.mode == 1:
            # Page 1: Relative Humidity View
            draw.text((0, 0), "HUMIDITY", font=self.font_title, fill=255)
            draw.line((0, 12, 128, 12), fill=255)  # Separator line at Y=12
            draw.text(
                (0, 24), f"Relative: {humidity:.1f} %", font=self.font_data, fill=255
            )
        elif self.mode == 2:
            # Page 2: Ultrasonic Distance View
            draw.text((0, 0), "DISTANCE", font=self.font_title, fill=255)
            draw.line((0, 12, 128, 12), fill=255)  # Separator line at Y=12
            dist_str = (
                f"{distance:.1f} cm" if not math.isnan(distance) else "Out of Range"
            )
            draw.text((0, 24), f"Object: {dist_str}", font=self.font_data, fill=255)

        # Write 1-bit canvas buffer over I2C to Graphic Display Data RAM (GDDRAM)
        self.device.display(image)  # type: ignore
