#!/usr/bin/env python3
"""
Make the About panel's video poster: Rome's enthroned Roma, cut from the site's own Miller
facsimile tiles (K. Miller 1887, public domain).

The poster stands in for the YouTube player until someone presses play, so opening the About
panel requests nothing from YouTube. Being a local file, it can't give that away either.

Writes  public/about-video-poster.jpg
Usage:  python scripts/make_about_video_poster.py      (needs Pillow)
"""
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
TILES = REPO / "public" / "Tabula_Peutingeriana_-_Miller_files" / "16"  # level 16 = full resolution
OUT = REPO / "public" / "about-video-poster.jpg"
TILE_SIZE, OVERLAP = 254, 1  # from Tabula_Peutingeriana_-_Miller.dzi

ROMA = (16328, 1574)   # miller_px/miller_py of ROMA (data_id 1203) in review_places_db.json
CROP_W = 1600          # source pixels; 16:9
SHIFT = (320, 36)      # moves the frame so Roma sits at ~30% width, clear of the centred play button
# The player is at most 720 CSS px wide. The facsimile's dotting and hatching compress badly, so
# 1280x720 came to 284 KB; this size is half that and still sharp under the poster's dark overlay.
OUT_SIZE = (960, 540)


def stitch(x0, y0, x1, y1):
    canvas = Image.new("RGB", (x1 - x0, y1 - y0))
    for col in range(x0 // TILE_SIZE, (x1 - 1) // TILE_SIZE + 1):
        for row in range(y0 // TILE_SIZE, (y1 - 1) // TILE_SIZE + 1):
            # A tile starts OVERLAP px before its grid cell, except in the first column/row.
            left = col * TILE_SIZE - (OVERLAP if col else 0)
            top = row * TILE_SIZE - (OVERLAP if row else 0)
            with Image.open(TILES / f"{col}_{row}.jpeg") as tile:
                canvas.paste(tile, (left - x0, top - y0))
    return canvas


def main():
    w, h = CROP_W, CROP_W * 9 // 16
    x0 = ROMA[0] + SHIFT[0] - w // 2
    y0 = ROMA[1] + SHIFT[1] - h // 2
    poster = stitch(x0, y0, x0 + w, y0 + h).resize(OUT_SIZE, Image.LANCZOS)
    poster.save(OUT, quality=74, optimize=True, progressive=True)
    print(f"{OUT}: {poster.size[0]}x{poster.size[1]}, {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
