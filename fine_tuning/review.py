"""Composite a cutout over magenta, black and white to expose fringes and holes.

With a box (source pixels) only that area is shown, at full resolution.

usage: review.py CUTOUT OUTPUT [LEFT TOP RIGHT BOTTOM]
"""

import sys

from PIL import Image

BACKGROUNDS = [(255, 0, 200), (0, 0, 0), (255, 255, 255)]

if __name__ == "__main__":
    if len(sys.argv) not in (3, 7):
        raise SystemExit(__doc__)
    cutout = Image.open(sys.argv[1]).convert("RGBA")
    if len(sys.argv) == 7:
        cutout = cutout.crop(tuple(int(v) for v in sys.argv[3:7]))

    sheet = Image.new("RGB", (cutout.width, cutout.height * len(BACKGROUNDS)))
    for i, colour in enumerate(BACKGROUNDS):
        tile = Image.new("RGBA", cutout.size, colour + (255,))
        tile.alpha_composite(cutout)
        sheet.paste(tile.convert("RGB"), (0, cutout.height * i))
    sheet.save(sys.argv[2])
