# ruff: noqa: INP001
"""Generate Home Assistant brand PNGs from the project's master design."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
BRAND_DIR = ROOT / "custom_components" / "momcozy_baby_monitor" / "brand"
NAVY = "#17243b"
CORAL = "#ff8066"
CREAM = "#fff6ef"
LIGHT_BLUE = "#dbe5f7"


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    filename = "segoeuib.ttf" if bold else "segoeui.ttf"
    candidates = (
        Path("C:/Windows/Fonts") / filename,
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        if bold
        else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def _draw_icon(size: int, *, dark: bool = False) -> Image.Image:
    scale = size / 512
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    body = LIGHT_BLUE if dark else NAVY
    lens_ring = NAVY if dark else CREAM
    lens = CREAM if dark else NAVY
    highlight = NAVY if dark else CREAM
    embrace = NAVY if dark else CREAM

    def box(coords: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        return tuple(round(value * scale) for value in coords)  # type: ignore[return-value]

    draw.arc(box((341, 61, 473, 193)), 282, 352, fill=CORAL, width=round(28 * scale))
    draw.arc(box((352, 112, 425, 185)), 282, 352, fill=CORAL, width=round(22 * scale))
    draw.rounded_rectangle(
        box((78, 92, 418, 428)), radius=round(132 * scale), fill=body
    )
    draw.ellipse(box((160, 123, 336, 299)), fill=lens_ring)
    draw.ellipse(box((188, 151, 308, 271)), fill=lens)
    draw.ellipse(box((256, 177, 282, 203)), fill=highlight)

    # A sampled parametric heart stays smooth without requiring an SVG renderer.
    raw_heart = [
        (
            16 * math.sin(angle) ** 3,
            13 * math.cos(angle)
            - 5 * math.cos(2 * angle)
            - 2 * math.cos(3 * angle)
            - math.cos(4 * angle),
        )
        for angle in (index * math.tau / 160 for index in range(160))
    ]
    heart = [
        (
            round((258 + x * 5) * scale),
            round((297 - y * 4.2) * scale),
        )
        for x, y in raw_heart
    ]
    draw.polygon(heart, fill=CORAL)
    draw.arc(box((127, 224, 389, 416)), 7, 173, fill=embrace, width=round(31 * scale))
    draw.arc(box((223, 269, 293, 326)), 30, 150, fill=NAVY, width=round(11 * scale))
    draw.rounded_rectangle(
        box((128, 428, 388, 492)), radius=round(32 * scale), fill=body
    )
    return image


def _draw_logo(size: tuple[int, int], *, dark: bool = False) -> Image.Image:
    _, height = size
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    icon_size = round(height * 0.82)
    icon = _draw_icon(icon_size, dark=dark)
    image.alpha_composite(icon, (round(height * 0.06), round(height * 0.09)))

    draw = ImageDraw.Draw(image)
    text_x = round(height * 0.93)
    title_font = _font(round(height * 0.135), bold=True)
    subtitle_font = _font(round(height * 0.068), bold=True)
    primary = LIGHT_BLUE if dark else NAVY
    draw.text((text_x, round(height * 0.30)), "Momcozy", font=title_font, fill=primary)
    draw.text(
        (text_x, round(height * 0.48)),
        "BABY MONITOR",
        font=subtitle_font,
        fill=CORAL,
    )
    draw.text(
        (text_x, round(height * 0.62)),
        "FOR HOME ASSISTANT",
        font=_font(round(height * 0.047), bold=True),
        fill=primary,
    )
    return image


def main() -> None:
    """Write all PNG assets expected by Home Assistant."""
    _draw_icon(256).save(BRAND_DIR / "icon.png", optimize=True)
    _draw_icon(512).save(BRAND_DIR / "icon@2x.png", optimize=True)
    _draw_icon(256, dark=True).save(BRAND_DIR / "dark_icon.png", optimize=True)
    _draw_icon(512, dark=True).save(BRAND_DIR / "dark_icon@2x.png", optimize=True)
    _draw_logo((512, 256)).save(BRAND_DIR / "logo.png", optimize=True)
    _draw_logo((1024, 512)).save(BRAND_DIR / "logo@2x.png", optimize=True)
    _draw_logo((512, 256), dark=True).save(BRAND_DIR / "dark_logo.png", optimize=True)
    _draw_logo((1024, 512), dark=True).save(
        BRAND_DIR / "dark_logo@2x.png",
        optimize=True,
    )


if __name__ == "__main__":
    main()
