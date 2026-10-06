from __future__ import annotations

import struct
from pathlib import Path

BRAND_DIR = (
    Path(__file__).parent.parent
    / "custom_components"
    / "momcozy_baby_monitor"
    / "brand"
)


def _png_metadata(path: Path) -> tuple[int, int, int]:
    """Return the PNG width, height, and color type from its IHDR chunk."""
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert data[12:16] == b"IHDR"
    width, height, _depth, color_type = struct.unpack(">IIBB", data[16:26])
    return width, height, color_type


def test_home_assistant_brand_assets_have_supported_sizes_and_transparency():
    expected_sizes = {
        "icon.png": (256, 256),
        "icon@2x.png": (512, 512),
        "dark_icon.png": (256, 256),
        "dark_icon@2x.png": (512, 512),
        "logo.png": (512, 256),
        "logo@2x.png": (1024, 512),
        "dark_logo.png": (512, 256),
        "dark_logo@2x.png": (1024, 512),
    }

    for filename, expected_size in expected_sizes.items():
        width, height, color_type = _png_metadata(BRAND_DIR / filename)
        assert (width, height) == expected_size
        assert color_type in {4, 6}, f"{filename} must retain an alpha channel"


def test_vector_icon_is_native_artwork_instead_of_an_embedded_vendor_bitmap():
    svg = (BRAND_DIR / "icon.svg").read_text(encoding="utf-8")

    assert "<path" in svg
    assert "data:image" not in svg
    assert "base64" not in svg
