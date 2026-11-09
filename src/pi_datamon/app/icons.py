from PIL import ImageDraw


def draw_thermometer_icon(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    """Draw a compact triangle temperature icon."""
    draw.polygon(
        (
            (x + size // 2, y),
            (x + size - 1, y + size - 1),
            (x, y + size - 1),
        ),
        outline=255,
        fill=255,
    )


def draw_droplet_icon(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    """Draw a compact circle humidity icon."""
    draw.ellipse((x, y, x + size - 1, y + size - 1), outline=255, fill=255)


def draw_sonar_icon(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    """Draw a compact square distance icon."""
    draw.rectangle((x, y, x + size - 1, y + size - 1), outline=255, fill=255)
