---
name: knockout-black-1c
description: Turn black line art on white paper into a one-colour (black ink only) transparent PNG for t-shirt heat transfers, and name it with the MangaJDM filename pattern. Use when the user asks for a "1c", "one-colour", "black only", "full transparency" or "knock out all white" version of an artwork file.
---

# One-colour (black only) knockout

Produces a PNG where every white is transparent, including white inside the drawing (car bodies, windows, lettering, sky, road), and every remaining pixel is pure black whose opacity follows how dark the original was. Grey shading and soft line edges become partly transparent black. Image size, framing and lines are unchanged.

## When not to use it

Check the image first. Stop and tell the user instead of processing if it is:

- Full colour (a photo, or coloured art): the result would be a black-only greyscale. Photos need a rembg cutout instead (see `temp/SOP.md`).
- Drawn on a fake grey/white checkerboard: use `fine_tuning/checkerkill.py`, which makes a two-colour file. A 1c from it would print the checker squares.
- Meant to keep white inside the art: that is a `2c` file, not `1c`.

## Steps

Run from the repo root with the repo's virtual environment.

1. Run the script on the original. Never write over the original.

   ```bash
   .venv/bin/python fine_tuning/knockout_black.py <original.png> <output.png>
   ```

2. Name the output `<design>-<corp>-1c-<variant>.png`, lower case, hyphens only, and save it in the same design folder as the original.
   - `<design>`: the design folder name, normally make and model (`nissan-gtr-r34-nur`, `mazda-miata`, `toyota-land-cruiser-fj`).
   - `<corp>`: `corp-true` if a manufacturer name (NISSAN, TOYOTA) or a manufacturer logo or badge is visible anywhere in the art; otherwise `corp-false`. Model names such as SUPRA or V-Spec II Nur do not count. Judge by looking at the image, never from the filename or folder.
   - `<variant>`: the short tag that tells versions apart, taken from the original's name (`front-04`, `01`, `kilimanjaro-safari`).
   - Example: `gtr-nur-front-04-corp-false.png` becomes `nissan-gtr-r34-nur-corp-false-1c-front-04.png`.
   - If that name already exists, add `-alt`.

3. Check the result before reporting it done:
   - Composite it over a solid blue or magenta background and look at it. Black ink is invisible over black. All lines should show, with no white patches or grey haze.
   - Confirm that no pixel has an RGB value other than 0, 0, 0, and note the share of fully transparent pixels.

   ```bash
   .venv/bin/python -c "
   from PIL import Image; import numpy as np, sys
   im = Image.open(sys.argv[1]); a = np.asarray(im)
   print('clear', round((a[..., 3] == 0).mean() * 100, 1), '%  non-black', int((a[..., :3].max(axis=2) > 0).sum()))
   bg = Image.new('RGBA', im.size, (40, 90, 200, 255)); bg.alpha_composite(im)
   bg.convert('RGB').save(sys.argv[2])" <output.png> <scratch-preview.jpg>
   ```

4. Report: the output path, the share of transparent pixels, and anything that looked wrong. Dropbox can take a minute to show a new file in Finder.

## Tuning

- Faint speckle on the shirt: raise `DEAD_ZONE` in `fine_tuning/knockout_black.py` (default 0.08, i.e. anything under 8% darker than the paper stays transparent).
- A screen printer may want hard solid black only. This script does not threshold; say so if the user mentions screen printing.

Background: `FORK.md`, "One-colour (full transparency) shirt files"; filing rules: `temp/SOP.md`, section 8.
