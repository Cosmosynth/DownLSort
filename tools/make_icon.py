"""Rasterize the DownLSort logo into the PNG/ICO assets the app bundles.

The source artwork (``assets/downlsort-logo.svg``) is made entirely of
axis-aligned rectangles, so it can be rendered faithfully without an SVG
engine: parse the rects, then draw them with Pillow.

Run from the repo root after editing the artwork:

    python tools/make_icon.py

Writes:
    src/downlsort/assets/downlsort-logo.png   (512x512, used by Tk)
    src/downlsort/assets/downlsort-logo.ico   (multi-size, used by the EXE)
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = ROOT / "assets" / "downlsort-logo.svg"
OUT_DIR = ROOT / "src" / "downlsort" / "assets"

VIEWBOX = 320  # artwork coordinate space
SUPERSAMPLE = 8  # render big, then downscale, for clean edges
PNG_SIZE = 512
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

_TAG = re.compile(r"<g\b[^>]*>|</g>|<rect\b[^>]*/?>", re.I)
_ATTR = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


def parse_rects(svg: str) -> list[tuple[dict[str, str], str | None]]:
    """Return ``(attributes, inherited_group_fill)`` for each rect."""
    svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S | re.I)
    rects: list[tuple[dict[str, str], str | None]] = []
    group_fill: str | None = None
    for match in _TAG.finditer(svg):
        token = match.group(0)
        if token.lower().startswith("<g"):
            group_fill = dict(_ATTR.findall(token)).get("fill") or group_fill
        elif token.lower().startswith("</g"):
            group_fill = None
        else:
            rects.append((dict(_ATTR.findall(token)), group_fill))
    return rects


def render(svg: str, size: int) -> Image.Image:
    """Render the SVG's rectangles into a *size* x *size* RGBA image."""
    scale = size / VIEWBOX
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for attrs, group_fill in parse_rects(svg):
        x = float(attrs.get("x", 0)) * scale
        y = float(attrs.get("y", 0)) * scale
        w = float(attrs.get("width", 0)) * scale
        h = float(attrs.get("height", 0)) * scale
        fill = attrs.get("fill") or group_fill
        stroke = attrs.get("stroke")
        stroke_w = float(attrs.get("stroke-width", 0)) * scale

        if fill and fill.lower() != "none":
            draw.rectangle([x, y, x + w - 1, y + h - 1], fill=fill)
        if stroke and stroke.lower() != "none" and stroke_w > 0:
            # An unfilled rect in SVG is a centered stroke.
            half = stroke_w / 2
            draw.rectangle(
                [x - half, y - half, x + w + half - 1, y + h + half - 1],
                outline=stroke,
                width=max(1, round(stroke_w)),
            )
    return img


def main() -> None:
    svg = SVG_PATH.read_text(encoding="utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    big = render(svg, PNG_SIZE * SUPERSAMPLE)
    if SUPERSAMPLE > 1:
        big = big.resize((PNG_SIZE, PNG_SIZE), Image.LANCZOS)

    png_path = OUT_DIR / "downlsort-logo.png"
    big.save(png_path)

    ico_path = OUT_DIR / "downlsort-logo.ico"
    big.save(ico_path, format="ICO", sizes=ICO_SIZES)

    print(f"wrote {png_path.relative_to(ROOT)} ({png_path.stat().st_size} bytes)")
    print(f"wrote {ico_path.relative_to(ROOT)} ({ico_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
