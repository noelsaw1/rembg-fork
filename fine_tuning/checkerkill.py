"""Remove a baked-in grey/white checkerboard ("fake transparency") from line art.

Usage: checkerkill.py SRC OUT [SEAL=10]
The checker runs under the whole drawing, so pixels alone cannot tell fill from
background. Dark outlines are thickened by SEAL px to close small gaps, light area
connected to the image edge becomes transparent, and everything the outlines
enclose is repainted solid white (2c). Art edges are un-mixed as black ink.
"""
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

src, out = sys.argv[1], sys.argv[2]
seal = int(sys.argv[3]) if len(sys.argv) > 3 else 10

rgb = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
v = rgb.min(axis=2)
light = v >= 200

def outside(k):
    sealed = ndimage.binary_dilation(v < 160, iterations=k)
    lab, _ = ndimage.label(~sealed)
    ids = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, ids[ids > 0])
    for _ in range(k + 2):
        bg = ndimage.binary_dilation(bg) & light
    return bg


# A wide seal finds the logo's silhouette; a narrow one, trusted only near that
# silhouette, keeps fine edge detail (speed-line tips) clean.
bg = outside(seal)
bg |= outside(2) & ndimage.binary_dilation(bg, iterations=3 * seal)

paper = 236.0  # darker checker grey; anything this light counts as paper
grey = np.clip(v / paper, 0, 1)
out_rgb = np.repeat((grey * 255)[..., None], 3, axis=2)
alpha = np.ones_like(v)
alpha[bg] = 0
ring = ndimage.binary_dilation(bg, iterations=3) & ~bg
alpha[ring] = 1 - grey[ring]
out_rgb[ring] = 0

rgba = np.dstack([out_rgb, alpha * 255]).round().astype(np.uint8)
Image.fromarray(rgba, "RGBA").save(out)
print(f"clear={(alpha == 0).mean():.2%}")
