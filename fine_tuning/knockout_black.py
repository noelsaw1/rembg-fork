"""Single-colour knockout for one-colour shirt transfers.

Every white becomes transparent, including white inside the art (car bodies,
logo letters). What remains is pure black, with each pixel's opacity taken
from how dark the original is, so grey shading and antialiased edges print
as lighter black. Works straight from the original; no rembg cutout needed.

Only suits black line art on white or off-white paper.

usage: knockout_black.py ORIGINAL OUTPUT
"""

import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # some originals are 8448x4608

PAPER_PERCENTILE = 95  # paper brightness; borders can be black frames, so not sampled there
DEAD_ZONE = 0.08  # darkness below this is paper texture and stays fully transparent


def knockout_black(source: np.ndarray) -> np.ndarray:
    lum = source.astype(np.float32).mean(axis=2)
    paper = np.percentile(lum, PAPER_PERCENTILE)
    ink = np.clip((paper - lum) / paper, 0, 1)
    ink = np.clip((ink - DEAD_ZONE) / (1 - DEAD_ZONE), 0, 1)

    out = np.zeros(source.shape[:2] + (4,), np.uint8)
    out[..., 3] = (ink * 255).round().astype(np.uint8)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    original, output = sys.argv[1:]
    source = np.array(Image.open(original).convert("RGB"))
    Image.fromarray(knockout_black(source), "RGBA").save(output)
