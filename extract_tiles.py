"""
extract_tiles.py — Extract individual tiles from TacticTileSheet.png
- Removes magenta (#FF00FF) background (replaces with transparency)
- Trims transparent padding from each tile
- Saves to textures/tiles/ as tile_ROW_COL.png

Grid layout (auto-detected):
  8 columns separated by all-pink vertical lines at x=75,151,227,303,379,455,531
  20 rows separated by all-pink horizontal lines at y=39,79,...,783
  Tile sizes: 75×39px (most rows) or 75×45px (taller cracked tile rows: 6,16-19)
"""

from PIL import Image
import os

SHEET_PATH = "textures/TacticTileSheet.png"
OUT_DIR = "textures/tiles"
PINK = (255, 0, 255)
# Tolerance: pixels within this Euclidean distance of PINK are treated as background
PINK_TOLERANCE = 30

os.makedirs(OUT_DIR, exist_ok=True)

img = Image.open(SHEET_PATH).convert("RGBA")
w, h = img.size
pixels = img.load()

# ── Pink-removal ─────────────────────────────────────────────────────────────
def is_pink(r, g, b):
    return (
        abs(r - PINK[0]) <= PINK_TOLERANCE and
        abs(g - PINK[1]) <= PINK_TOLERANCE and
        abs(b - PINK[2]) <= PINK_TOLERANCE
    )

defringe = img.copy()
dp = defringe.load()
for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        if is_pink(r, g, b):
            dp[x, y] = (0, 0, 0, 0)

# ── Grid boundaries ───────────────────────────────────────────────────────────
col_seps = [75, 151, 227, 303, 379, 455, 531]
row_seps = [39, 79, 119, 159, 199, 239, 285, 325, 365, 405, 445, 485, 525, 565, 605, 645, 691, 737, 783]

def build_bands(seps, total):
    bands = []
    prev = 0
    for s in seps:
        bands.append((prev, s - 1))
        prev = s + 1
    bands.append((prev, total - 1))
    return bands

col_bands = build_bands(col_seps, w)   # (x_start, x_end) × 8
row_bands = build_bands(row_seps, h)   # (y_start, y_end) × 20

print(f"Grid: {len(col_bands)} columns × {len(row_bands)} rows = {len(col_bands)*len(row_bands)} tiles")

# ── Extract & save ────────────────────────────────────────────────────────────
count = 0
for row_idx, (y0, y1) in enumerate(row_bands):
    for col_idx, (x0, x1) in enumerate(col_bands):
        tile = defringe.crop((x0, y0, x1 + 1, y1 + 1))

        # Trim fully-transparent rows/cols from edges
        bbox = tile.getbbox()
        if bbox is None:
            # Entirely transparent — skip
            print(f"  Skipping empty tile row={row_idx} col={col_idx}")
            continue
        tile = tile.crop(bbox)

        filename = f"tile_{row_idx:02d}_{col_idx:02d}.png"
        tile.save(os.path.join(OUT_DIR, filename))
        count += 1

print(f"Saved {count} tiles to {OUT_DIR}/")
