# Fork notes

This is a fork of [danielgatis/rembg](https://github.com/danielgatis/rembg). The `rembg/` package is unchanged from upstream; everything fork-specific lives outside it so upstream merges stay clean.

## What this fork adds

### [fine_tuning/](fine_tuning/)

Post-processing scripts that repair a cutout after `rembg` has produced it. They do not call or modify `rembg`; they only need the original image and the cutout, plus `numpy`, `scipy` and `Pillow`, which a `rembg` install already provides.

| File | Purpose |
| --- | --- |
| [fix_regions.py](fine_tuning/fix_regions.py) | Rebuilds transparency inside chosen boxes from the original's dark outlines. For line art on a white background, where the model erases part of the art or leaves a soft, smeared edge. |
| [review.py](fine_tuning/review.py) | Composites a cutout (or a boxed area of it) over magenta, black and white so fringes and missing areas are obvious. |
| [regions/](fine_tuning/regions/) | One JSON file per image listing the boxes `fix_regions.py` should repair. |
| [knockout_black.py](fine_tuning/knockout_black.py) | Turns line art into black ink on a fully transparent background, white inside the art included. For one-colour shirt transfers. Works from the original alone; no `rembg` cutout. |
| [checkerkill.py](fine_tuning/checkerkill.py) | Removes a grey/white checkerboard that was drawn into the image as fake transparency. Seals gaps in the outlines, clears outside the art and repaints inside it solid white. `checkerkill.py SRC OUT [SEAL=10]`; raise SEAL if the outside leaks into an enclosed area. |
| [feather_edges.py](fine_tuning/feather_edges.py) | Fades all four sides to transparent over a band that is a percentage of the shorter side. `feather_edges.py IN OUT [PERCENT=5]`, up to 50. Only lowers opacity, so 1c files stay pure black. |

Typical use, from the repo root with the virtual environment active:

```bash
rembg i -m birefnet-general -dc original.png cutout.png
python fine_tuning/fix_regions.py original.png cutout.png fine_tuning/regions/<image>.json fixed.png
python fine_tuning/review.py fixed.png review.png
```

A regions file is a list of entries, with all coordinates in source-image pixels:

```json
[
  {
    "name": "what is being repaired",
    "box": [left, top, right, bottom],
    "seed": [x, y],
    "barriers": [[[x1, y1], [x2, y2]]]
  }
]
```

- `box`: the area to rebuild. Everything outside it keeps the model's result.
- `seed`: a point on white background inside the box. White connected to it becomes transparent; everything else in the box becomes solid.
- `barriers`: optional invisible lines that close a gap where the artwork's outline stops short, so the fill does not leak through.

### One-colour (full transparency) shirt files

A two-colour transfer (black plus white ink) costs more than one colour. For a black-only print, every white goes, including car bodies, Mt. Fuji and logo letters; only black ink stays.

1. Mark each image that should be one-colour by adding `-full` to the end of its filename in the transparent output folder (`car-miata-multi-gen-no-logo-full.png`).
2. For each marked file, run the script on the matching original (same name without `-full`), writing straight over the marked file:

```bash
python fine_tuning/knockout_black.py original.png original-full.png
```

To do a whole folder, with `SRC` holding the originals and `DST` the `-full` files:

```bash
for f in "$DST"/*-full.png; do
  n=$(basename "$f"); python fine_tuning/knockout_black.py "$SRC/${n%-full.png}.png" "$f"
done
```

3. Review over a coloured background, since black ink is invisible over black: `python fine_tuning/review.py <file> review.png` and look at the magenta panel.

What to expect:

- Every pixel is pure black (RGB 0, 0, 0); only its opacity varies. Grey shading and antialiased line edges print as lighter black. That suits heat transfers. A screen printer may want hard solid black only, which this script does not produce.
- Paper texture is ignored: anything less than 8% darker than the paper stays fully transparent (`DEAD_ZONE`). Raise it if faint speckle shows on the shirt.
- The paper brightness is taken from the image as a whole, not its border, so art framed in black panels still works.
- The art must be dark ink on white or off-white paper. Coloured art (the RX-7 / GT-R / Supra trio) becomes a black-only greyscale.

New fine-tuning scripts and their data files belong in `fine_tuning/`.

## Not tracked

`temp/` is git-ignored and holds internal working notes and test outputs.
