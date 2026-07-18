"""
Drop an image into ~/Downloads/ascii and run this script with no arguments.
It converts the image to ASCII art and saves an animated SVG next to it that
types itself in line by line, terminal-style, using SMIL (so it also
animates when embedded in a GitHub README).
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif", ".webp"}

WIDTH_CHARS = 100
CHAR_ASPECT = 0.55  # monospace glyphs are taller than wide; corrects row count for image aspect ratio
RAMP = "@%#*+=-:. "  # dark->dense glyph, bright->space, per index

FONT_SIZE = 14
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.15
PAD = 20

BG_COLOR = "#0d1117"
TEXT_COLOR = "#e6edf3"
CURSOR_COLOR = "#3fb950"

TARGET_TOTAL_SECONDS = 18.0
MIN_TIME_PER_CHAR = 0.004
MAX_TIME_PER_CHAR = 0.02


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


def image_to_ascii_rows(path: Path) -> list[str]:
    img = Image.open(path).convert("L")
    height_chars = max(1, round(WIDTH_CHARS * (img.height / img.width) * CHAR_ASPECT))
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.LANCZOS
    img = img.resize((WIDTH_CHARS, height_chars), resample)

    pixels = list(img.get_flattened_data()) if hasattr(img, "get_flattened_data") else list(img.getdata())
    ramp_max = len(RAMP) - 1
    rows = []
    for y in range(height_chars):
        row_pixels = pixels[y * WIDTH_CHARS:(y + 1) * WIDTH_CHARS]
        row = "".join(RAMP[int(v / 255 * ramp_max)] for v in row_pixels)
        rows.append(row)
    return rows


def build_svg(rows: list[str]) -> str:
    row_width_px = WIDTH_CHARS * CHAR_W
    svg_width = PAD * 2 + row_width_px
    svg_height = PAD * 2 + len(rows) * CHAR_H

    total_chars = WIDTH_CHARS * len(rows)
    time_per_char = TARGET_TOTAL_SECONDS / max(total_chars, 1)
    time_per_char = max(MIN_TIME_PER_CHAR, min(MAX_TIME_PER_CHAR, time_per_char))
    row_dur = WIDTH_CHARS * time_per_char

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width:.1f}" '
        f'height="{svg_height:.1f}" viewBox="0 0 {svg_width:.1f} {svg_height:.1f}">'
    )
    parts.append(f'<rect width="100%" height="100%" rx="6" fill="{BG_COLOR}"/>')

    defs = ["<defs>"]
    texts = []
    cursor_x_anims = []
    cursor_y_anims = []

    for i, row in enumerate(rows):
        row_y = PAD + i * CHAR_H
        baseline_y = row_y + FONT_SIZE
        begin = i * row_dur

        defs.append(
            f'<clipPath id="clip{i}"><rect x="{PAD}" y="{row_y:.2f}" width="0" '
            f'height="{CHAR_H:.2f}"><animate attributeName="width" from="0" '
            f'to="{row_width_px:.2f}" begin="{begin:.3f}s" dur="{row_dur:.3f}s" '
            f'fill="freeze"/></rect></clipPath>'
        )

        texts.append(
            f'<text clip-path="url(#clip{i})" x="{PAD}" y="{baseline_y:.2f}" '
            f'font-family="ui-monospace, SFMono-Regular, Consolas, \'Liberation Mono\', '
            f'Menlo, monospace" font-size="{FONT_SIZE}" fill="{TEXT_COLOR}" '
            f'xml:space="preserve">{escape(row)}</text>'
        )

        cursor_x_anims.append(
            f'<animate attributeName="x" from="{PAD}" to="{PAD + row_width_px:.2f}" '
            f'begin="{begin:.3f}s" dur="{row_dur:.3f}s" fill="freeze"/>'
        )
        cursor_y_anims.append(
            f'<animate attributeName="y" from="{row_y:.2f}" to="{row_y:.2f}" '
            f'begin="{begin:.3f}s" dur="{row_dur:.3f}s" fill="freeze"/>'
        )

    defs.append("</defs>")
    parts.extend(defs)
    parts.extend(texts)

    parts.append(
        f'<rect width="{CHAR_W:.2f}" height="{CHAR_H * 0.85:.2f}" fill="{CURSOR_COLOR}" '
        f'x="{PAD}" y="{PAD:.2f}">'
        + "".join(cursor_x_anims) + "".join(cursor_y_anims)
        + "</rect>"
    )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    downloads = Path.home() / "Downloads"
    ascii_dir = downloads / "ascii"
    ascii_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        source = Path(sys.argv[1])
    else:
        source = find_source_image(ascii_dir)

    rows = image_to_ascii_rows(source)
    svg = build_svg(rows)

    out_path = source.with_suffix(".svg")
    out_path.write_text(svg, encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
