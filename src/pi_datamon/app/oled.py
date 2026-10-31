import math
from typing import cast

from luma.core.interface.serial import i2c  # type: ignore
from luma.oled.device import ssd1306  # type: ignore
from PIL import Image, ImageDraw, ImageFont

from pi_datamon.app.icons import (
    draw_droplet_icon,
    draw_sonar_icon,
    draw_thermometer_icon,
)

# I2C Address
SSD1306_I2C_ADDR = 0x3C


class SSD1306:
    """Handles 128x64 monochrome SSD1306 OLED canvas rendering and menu navigation."""

    # Datasheet: https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf

    def __init__(self, bus_id: int, address: int = SSD1306_I2C_ADDR):
        # Initialize luma.core I2C serial transport wrapper.
        serial_interface = i2c(port=bus_id, address=address)
        self.device = ssd1306(serial_interface)
        self.size: tuple[int, int] = cast(
            tuple[int, int],
            # Retrieve display canvas dimensions (128 pixels wide x 64 pixels high).
            self.device.size,  # type: ignore
        )
        self.font_title = ImageFont.load_default()
        self.font_data = ImageFont.load_default()
        self.mode = 0

        # Pre-calculated geometry layout constants.
        self.margin_x = 4
        self.margin_y = 4
        self.icon_size = 16
        self.text_x = self.margin_x + self.icon_size + 6  # X = 26
        self.separator_y = self.margin_y + 13  # Y = 17
        self.label_y = self.separator_y + 4  # Y = 21
        self.value_y = self.label_y + 14  # Y = 35

    def cycle_mode(self) -> None:
        """Cycle through display pages sequentially in a loop (0 -> 1 -> 2 -> 0)."""
        self.mode = (self.mode + 1) % 3

    def render(self, temperature: float, humidity: float, distance: float) -> None:
        """Draw active page layout to PIL image buffer and push to SSD1306 GDDRAM."""
        # Create a blank 1-bit monochrome image buffer in RAM (Mode '1': 0 = Black, 255 = White).
        image = Image.new("1", self.size, 0)
        draw = ImageDraw.Draw(image)

        # Draw icon and set variables for the current display mode (0 = Temperature, 1 = Humidity, 2 = Distance).
        if self.mode == 0:
            draw_thermometer_icon(draw, x=self.margin_x, y=self.margin_y)
            title = "TEMP MONITOR"
            label = "Temperature:"
            value = f"{temperature:.1f} °C"
        elif self.mode == 1:
            draw_droplet_icon(draw, x=self.margin_x, y=self.margin_y)
            title = "HUMIDITY"
            label = "Relative:"
            value = f"{humidity:.1f} %"
        else:
            draw_sonar_icon(draw, x=self.margin_x, y=self.margin_y)
            title = "DISTANCE"
            label = "Object Distance:"
            value = f"{distance:.1f} cm" if not math.isnan(distance) else "N/A"

        # Draw mode title.
        draw.text((self.text_x, self.margin_y), title, font=self.font_title, fill=255)

        # Draw horizontal separator line.
        draw.line(
            (
                self.text_x,
                self.separator_y,
                self.size[0] - self.margin_x,
                self.separator_y,
            ),
            fill=255,
        )

        # Draw metric label.
        draw.text((self.text_x, self.label_y), label, font=self.font_data, fill=255)

        # Draw measured value.
        draw.text((self.text_x, self.value_y), value, font=self.font_data, fill=255)

        # Write 1-bit canvas buffer to OLED display.
        self.device.display(image)  # type: ignore
