---
name: feather-edges
description: Feather all four sides of an artwork PNG so it fades out to transparent toward the edges, with an adjustable fade width (default 5% of the shorter side). Use when the user asks to feather, fade, soften or vignette the edges or sides of an image, or wants a print to fade out instead of ending in a hard rectangle.
---

# Feather all four sides

Fades the image's opacity from fully transparent at the outer edge to unchanged at the inner edge of a band. The band is a percentage of the image's shorter side, so it is the same width in pixels on all four sides. The fade eases in, so there is no visible line where it starts. Corners get both fades and round off softly. Art inside the band is untouched.

It only lowers opacity; it never changes colours. That makes it safe on `1c` files (they stay pure black) and `2c` files. A plain RGB image gains an alpha channel, but its white paper stays opaque white inside the band, so knock out the background first (`knockout-black-1c` skill, or the rembg steps in `temp/SOP.md`) unless a white rectangle with faded edges is what the user wants.

## Width

- Default: 5% (a small, subtle fade).
- The user can ask for more: "10%", "20%", "a heavy fade". Map loose wording to a number and say which number you used: small 5, medium 10, large 20.
- Allowed range: above 0 and at most 50 (50 fades all the way to the centre of the shorter side).

## Steps

Run from the repo root with the repo's virtual environment.

1. Run the script. Never write over the input.

   ```bash
   .venv/bin/python fine_tuning/feather_edges.py <input.png> <output.png> [PERCENT]
   ```

2. Name the output after the input with `-feather-<percent>` added before `.png`, in the same folder. Example: `nissan-gtr-r34-nur-corp-false-1c-front-04.png` at 5% becomes `nissan-gtr-r34-nur-corp-false-1c-front-04-feather-5.png`. Keep the rest of the name, including the corp label and stage, unchanged.

3. Check it over a solid blue or magenta background (black ink is invisible over black) and look at it: all four sides should fade evenly, with no hard line where the fade begins and nothing changed in the middle.

   ```bash
   .venv/bin/python -c "
   from PIL import Image; import sys
   im = Image.open(sys.argv[1]).convert('RGBA'); bg = Image.new('RGBA', im.size, (40, 90, 200, 255))
   bg.alpha_composite(im); bg.convert('RGB').save(sys.argv[2])" <output.png> <scratch-preview.jpg>
   ```

4. Report the output path and the percentage used. Dropbox can take a minute to show a new file in Finder.

## Notes

- If the art already fades out near the edges (some scenes are drawn that way), a further feather mostly affects the corners. Say so if the result looks unchanged.
- Feathering leaves partly transparent pixels. A heat transfer prints these as lighter ink; a screen printer may need a halftone instead.

Background: `FORK.md`; filing rules: `temp/SOP.md`, section 8.
