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

New fine-tuning scripts and their data files belong in `fine_tuning/`.

## Not tracked

`temp/` is git-ignored and holds internal working notes and test outputs.
