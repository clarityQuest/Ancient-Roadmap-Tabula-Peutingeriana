"""Create DeepZoom (.dzi + *_files) tiles from an image using pyvips.

Examples:
	python public/create__dzi.py --input public/Tabula_Peutingeriana_-_Miller.jpg --output public/Tabula_Peutingeriana_-_Miller
	python public/create__dzi.py --input public/Tabula_Peutingeriana_150dpi_Stitched.jpg --output public/Tabula_Peutingeriana_150dpi_Stitched
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image

try:
	import pyvips  # type: ignore
except Exception:
	pyvips = None


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Create DZI tiles with pyvips")
	p.add_argument("--input", required=True, help="Input raster image path")
	p.add_argument("--output", required=True, help="Output basename (without .dzi)")
	p.add_argument("--tile-size", type=int, default=254, help="DeepZoom tile size")
	p.add_argument("--overlap", type=int, default=1, help="DeepZoom tile overlap")
	p.add_argument("--suffix", default=".jpg[Q=90]", help="Tile suffix/encoding options")
	return p.parse_args()


def main() -> None:
	args = parse_args()
	input_path = Path(args.input)
	output_base = Path(args.output)

	if not input_path.exists():
		raise FileNotFoundError(f"Input image not found: {input_path}")

	if pyvips is not None:
		image = pyvips.Image.new_from_file(str(input_path), access="sequential")
		image.dzsave(
			str(output_base),
			tile_size=int(args.tile_size),
			overlap=int(args.overlap),
			suffix=args.suffix,
		)
		print(f"DZI created with pyvips: {output_base}.dzi")
		return

	# Pillow fallback: generate DZI XML and tile pyramid.
	tile_size = int(args.tile_size)
	overlap = int(args.overlap)
	img = Image.open(input_path).convert("RGB")
	width, height = img.size
	max_level = int(math.ceil(math.log2(max(width, height))))

	tiles_root = output_base.parent / f"{output_base.name}_files"
	tiles_root.mkdir(parents=True, exist_ok=True)

	for level in range(max_level + 1):
		scale = 2 ** (max_level - level)
		lvl_w = max(1, int(math.ceil(width / scale)))
		lvl_h = max(1, int(math.ceil(height / scale)))
		if scale == 1:
			level_img = img
		else:
			level_img = img.resize((lvl_w, lvl_h), Image.Resampling.LANCZOS)

		cols = int(math.ceil(lvl_w / tile_size))
		rows = int(math.ceil(lvl_h / tile_size))
		level_dir = tiles_root / str(level)
		level_dir.mkdir(parents=True, exist_ok=True)

		for c in range(cols):
			for r in range(rows):
				left = c * tile_size - (overlap if c > 0 else 0)
				top = r * tile_size - (overlap if r > 0 else 0)
				right = min((c + 1) * tile_size + (overlap if c < cols - 1 else 0), lvl_w)
				bottom = min((r + 1) * tile_size + (overlap if r < rows - 1 else 0), lvl_h)
				tile = level_img.crop((left, top, right, bottom))
				tile.save(level_dir / f"{c}_{r}.jpeg", format="JPEG", quality=90)

	dzi_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>\n'
		'<Image xmlns="http://schemas.microsoft.com/deepzoom/2008" '
		f'TileSize="{tile_size}" Overlap="{overlap}" Format="jpeg">\n'
		f'  <Size Width="{width}" Height="{height}"/>\n'
		'</Image>\n'
	)
	output_base.with_suffix(".dzi").write_text(dzi_xml, encoding="utf-8")
	print(f"DZI created with Pillow fallback: {output_base}.dzi")


if __name__ == "__main__":
	main()