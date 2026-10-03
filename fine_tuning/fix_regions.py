"""Rebuild the alpha of line-art regions that the model got wrong.

Inside each region's box, white reachable from the seed point is background;
everything else (outlines and whatever they enclose) is kept solid. Barriers
are invisible line segments that close gaps where the artwork's outline stops
short. Outside the boxes the model's alpha is left alone.

Only suits dark outlines on a white background. Regions are per image and
live in a JSON file (see regions/); all coordinates are source pixels.

usage: fix_regions.py ORIGINAL CUTOUT REGIONS_JSON OUTPUT
"""

import json
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

DARK = 128  # luminance below this is outline and blocks the fill
CLEAR = 235  # background at or above this luminance becomes fully transparent


def fix_regions(source: np.ndarray, out: np.ndarray, regions: list) -> None:
    for spec in regions:
        x0, y0, x1, y1 = spec["box"]
        src = source[y0:y1, x0:x1]
        lum = src.mean(axis=2)

        wall = Image.new("L", (x1 - x0, y1 - y0), 0)
        draw = ImageDraw.Draw(wall)
        for (ax, ay), (bx, by) in spec.get("barriers", []):
            draw.line((ax - x0, ay - y0, bx - x0, by - y0), fill=255, width=3)

        labels, _ = ndimage.label((lum >= DARK) & (np.array(wall) == 0))
        sx, sy = spec["seed"]
        seed_label = labels[sy - y0, sx - x0]
        if seed_label == 0:
            raise SystemExit(f"{spec.get('name', spec['box'])}: seed is not on white")
        background = labels == seed_label

        # background side of an outline's antialiased edge becomes black at partial alpha
        alpha = np.where(background, 255 - lum, 255)
        alpha[background & (lum >= CLEAR)] = 0
        rgb = np.where(background[..., None], 0, src)

        region = out[y0:y1, x0:x1]
        region[..., :3] = rgb.astype(np.uint8)
        region[..., 3] = alpha.astype(np.uint8)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    original, cutout, regions_json, output = sys.argv[1:]
    source = np.array(Image.open(original).convert("RGB"))
    out = np.array(Image.open(cutout).convert("RGBA"))
    if source.shape[:2] != out.shape[:2]:
        raise SystemExit("original and cutout differ in size")
    with open(regions_json) as f:
        fix_regions(source, out, json.load(f))
    Image.fromarray(out).save(output)
