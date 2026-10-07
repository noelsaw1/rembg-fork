"""Feather all four sides of an image so the art fades out to transparent.

The fade band is a percentage of the image's shorter side, so it is the same
width in pixels on every side. Opacity eases from fully transparent at the very
edge to unchanged at the inner edge of the band; the art inside the band is
untouched. Corners get both fades, so they round off softly.

Works on transparent PNGs (1c, 2c) and on plain RGB images, which gain an
alpha channel.

usage: feather_edges.py INPUT OUTPUT [PERCENT=5]
"""

import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

DEFAULT_PERCENT = 5.0


def ramp(n: int, band: int) -> np.ndarray:
    """1-D opacity multiplier: 0 at both ends, 1 beyond `band` pixels in."""
    d = np.minimum(np.arange(n), np.arange(n)[::-1]).astype(np.float32)
    t = np.clip((d + 0.5) / band, 0, 1)
    return t * t * (3 - 2 * t)  # smoothstep: no hard line where the fade starts


def feather_edges(rgba: np.ndarray, percent: float = DEFAULT_PERCENT) -> np.ndarray:
    h, w = rgba.shape[:2]
    band = max(1, round(min(h, w) * percent / 100))
    mask = ramp(h, band)[:, None] * ramp(w, band)[None, :]
    out = rgba.copy()
    out[..., 3] = (rgba[..., 3] * mask).round().astype(np.uint8)
    return out


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    src, dst = sys.argv[1:3]
    percent = float(sys.argv[3]) if len(sys.argv) == 4 else DEFAULT_PERCENT
    if not 0 < percent <= 50:
        raise SystemExit("PERCENT must be above 0 and at most 50")
    rgba = np.array(Image.open(src).convert("RGBA"))
    Image.fromarray(feather_edges(rgba, percent), "RGBA").save(dst)
