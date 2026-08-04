#!/usr/bin/env python3
"""
Decode Supercell .si (Supercell Icon) binary vector format to SVG.

Format (all header fields big-endian, coordinates little-endian float32):
  [0-3]  magic: b0 b0 1e 07
  [4-7]  version: 0x0903
  [8-11] num_paths (BE)
  [12-15] num_contours (BE) -- total contours across all paths
  [16-19] num_scalars (BE) -- total float32 values for coordinates
  [20-23] flags (BE)
  [24..] num_scalars × 4 bytes: LE float32 coordinates
          pair[0] = (stroke_width, ?)  -- metadata, not a vertex
          pair[1..] = (x, y) vertices distributed across paths
  After floats: width (BE f32), height (BE f32), padding (4 bytes), style bytes
"""

import struct, os, sys, glob


MAGIC = b'\xb0\xb0\x1e\x07'


def read_be_u32(data, off):
    return struct.unpack_from('>I', data, off)[0]

def read_le_f32(data, off):
    return struct.unpack_from('<f', data, off)[0]

def read_be_f32(data, off):
    return struct.unpack_from('>f', data, off)[0]


def parse_style(style_bytes):
    """Extract RGBA colors from trailing style bytes."""
    colors = []
    i = 0
    while i < len(style_bytes) - 3:
        # Look for 4-byte sequences where byte[3] == 0xff (opaque)
        r, g, b, a = style_bytes[i], style_bytes[i+1], style_bytes[i+2], style_bytes[i+3]
        if a == 0xff and r == g == b:  # greyscale opaque color
            colors.append((r, g, b, a))
            i += 4
        elif a == 0xff and not (r == 0 and g == 0 and b == 0):
            colors.append((r, g, b, a))
            i += 4
        else:
            i += 1
    # Fallback: 0x000000ff = black
    if not colors:
        # Check for explicit black
        for i in range(len(style_bytes) - 3):
            if style_bytes[i:i+4] == b'\x00\x00\x00\xff':
                colors.append((0, 0, 0, 255))
                break
    return colors or [(0, 0, 0, 255)]


def si_to_svg(data):
    if data[:4] != MAGIC:
        raise ValueError(f"Not a .si file (magic={data[:4].hex()})")

    num_paths    = read_be_u32(data, 8)
    num_contours = read_be_u32(data, 12)
    num_scalars  = read_be_u32(data, 16)

    # Read all coordinate floats (LE)
    coords = []
    off = 24
    for _ in range(num_scalars):
        coords.append(read_le_f32(data, off))
        off += 4

    # After coords: width, height as BE f32
    after = off
    width  = read_be_f32(data, after)     if after + 4 <= len(data) else 24.0
    height = read_be_f32(data, after + 4) if after + 8 <= len(data) else 24.0
    style_start = after + 12  # skip width(4) + height(4) + padding(4)

    # Parse stroke color from style bytes
    style_bytes = data[style_start:] if style_start < len(data) else b''
    colors = parse_style(style_bytes)
    stroke_color = '#{:02x}{:02x}{:02x}'.format(*colors[0][:3])

    # First pair is metadata (stroke_width, ?)
    if len(coords) >= 2:
        stroke_width = coords[0]
        pts = [(coords[i], coords[i+1]) for i in range(2, len(coords)-1, 2)]
    else:
        stroke_width = 2.0
        pts = []

    if not pts:
        # Fallback: placeholder cross
        pts = [(4, 4), (width-4, height-4)]

    # Distribute points across paths and build SVG path data
    n_pts = len(pts)
    if num_paths <= 1:
        # Single polyline path
        path_groups = [pts]
    else:
        # Try to split points evenly across paths
        per = max(1, n_pts // num_paths)
        path_groups = []
        for i in range(num_paths):
            start = i * per
            end = start + per if i < num_paths - 1 else n_pts
            if start < n_pts:
                path_groups.append(pts[start:end])

    # Build SVG path elements
    path_elems = []
    for i, group in enumerate(path_groups):
        if not group:
            continue
        fill_color = stroke_color
        if i < len(colors):
            fill_color = '#{:02x}{:02x}{:02x}'.format(*colors[i][:3])
        if len(group) == 1:
            x, y = group[0]
            r = stroke_width / 2
            path_elems.append(
                f'  <circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" fill="{fill_color}"/>'
            )
        elif len(group) == 2:
            x1, y1 = group[0]
            x2, y2 = group[1]
            path_elems.append(
                f'  <line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
                f'stroke="{fill_color}" stroke-width="{stroke_width:.2f}" '
                f'stroke-linecap="round"/>'
            )
        else:
            coords_str = ' '.join(f'{x:.3f},{y:.3f}' for x, y in group)
            path_elems.append(
                f'  <polyline points="{coords_str}" fill="none" '
                f'stroke="{fill_color}" stroke-width="{stroke_width:.2f}" '
                f'stroke-linecap="round" stroke-linejoin="round"/>'
            )

    path_content = '\n'.join(path_elems) if path_elems else '  <!-- empty -->'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.1f} {height:.1f}" width="{width:.0f}" height="{height:.0f}">
{path_content}
</svg>'''
    return svg


def convert_file(in_path, out_dir):
    with open(in_path, 'rb') as f:
        data = f.read()
    try:
        svg = si_to_svg(data)
        name = os.path.splitext(os.path.basename(in_path))[0] + '.svg'
        out_path = os.path.join(out_dir, name)
        with open(out_path, 'w') as f:
            f.write(svg)
        return True, name
    except Exception as e:
        return False, str(e)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input', help='.si file or directory')
    p.add_argument('-o', '--output', default='.', help='output directory')
    args = p.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if os.path.isdir(args.input):
        files = glob.glob(f'{args.input}/**/*.si', recursive=True)
    else:
        files = [args.input]

    ok = fail = 0
    for f in sorted(files):
        success, msg = convert_file(f, args.output)
        if success:
            ok += 1
            print(f'  [OK]  {msg}')
        else:
            fail += 1
            print(f'  [ERR] {os.path.basename(f)}: {msg}')

    print(f'\n{ok} converted, {fail} failed  →  {args.output}')
