from PIL import ImageDraw


def draw_thermometer_icon(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Draw a 16x16 pixel thermometer icon at position (x, y)."""
    # Outer stem and fluid bulb.
    draw.rectangle((x + 6, y + 1, x + 9, y + 10), outline=255, fill=0)
    draw.ellipse((x + 4, y + 9, x + 11, y + 15), outline=255, fill=255)
    # Internal liquid core.
    draw.line((x + 7, y + 4, x + 7, y + 10), fill=255)
    # Tick marks on the side.
    draw.line((x + 10, y + 3, x + 12, y + 3), fill=255)
    draw.line((x + 10, y + 6, x + 12, y + 6), fill=255)


def draw_droplet_icon(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Draw a 16x16 pixel raindrop/humidity icon at position (x, y)."""
    # Lower rounded water body.
    draw.ellipse((x + 3, y + 5, x + 12, y + 15), outline=255, fill=255)
    # Pointed top vertex lines.
    draw.line((x + 7, y + 1, x + 3, y + 7), fill=255)
    draw.line((x + 8, y + 1, x + 12, y + 7), fill=255)


def draw_sonar_icon(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Draw a 16x16 pixel ultrasonic/distance icon at position (x, y)."""
    # Central transducer dot.
    draw.ellipse((x + 1, y + 6, x + 5, y + 10), outline=255, fill=255)
    # Expanding acoustic wave arcs.
    draw.arc((x + 1, y + 2, x + 10, y + 14), start=300, end=60, fill=255)
    draw.arc((x + 1, y - 1, x + 15, y + 17), start=300, end=60, fill=255)
