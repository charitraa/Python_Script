"""
Drop an image into ~/Downloads/ascii and run this script with no arguments.
It samples the image on a square-cell grid and saves a JS file next to it
containing SILHOUETTE_ASPECT and a flat SILHOUETTE_FLAT array of normalized
(x, y) coordinates for every grid cell darker than a brightness threshold,
for driving a canvas/JS reveal animation on a website.
"""

import sys
from pathlib import Path

from PIL import Image

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif", ".webp"}

WIDTH_CELLS = 100
BRIGHTNESS_THRESHOLD = 128  # 0-255; grayscale values below this count as "filled"


def find_source_image(ascii_dir: Path) -> Path:
    candidates = [
        p for p in ascii_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]
    if not candidates:
        print(f"No image found in {ascii_dir}")
        print("Drop an image in there and run this script again.")
        sys.exit(1)
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if len(candidates) > 1:
        print(f"Found {len(candidates)} images, using the most recent: {candidates[0].name}")
    return candidates[0]


def image_to_silhouette(path: Path) -> tuple[float, list[float]]:
    img = Image.open(path).convert("L")
    height_cells = max(1, round(WIDTH_CELLS * (img.height / img.width)))
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.LANCZOS
    img = img.resize((WIDTH_CELLS, height_cells), resample)
    pixels = list(img.get_flattened_data()) if hasattr(img, "get_flattened_data") else list(img.getdata())

    aspect = WIDTH_CELLS / height_cells
    flat: list[float] = []
    for row in range(height_cells):
        y = round((row + 0.5) / height_cells, 3)
        for col in range(WIDTH_CELLS):
            if pixels[row * WIDTH_CELLS + col] < BRIGHTNESS_THRESHOLD:
                x = round((col + 0.5) / WIDTH_CELLS, 3)
                flat.append(x)
                flat.append(y)
    return round(aspect, 4), flat


def build_js(aspect: float, flat: list[float]) -> str:
    values = ", ".join(str(v) for v in flat)
    return (
        f"const SILHOUETTE_ASPECT = {aspect};\n"
        f"const SILHOUETTE_FLAT = [{values}];\n"
    )


def main():
    downloads = Path.home() / "Downloads"
    ascii_dir = downloads / "ascii"
    ascii_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        source = Path(sys.argv[1])
    else:
        source = find_source_image(ascii_dir)

    aspect, flat = image_to_silhouette(source)
    js = build_js(aspect, flat)

    out_path = source.with_suffix(".js")
    out_path.write_text(js, encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
