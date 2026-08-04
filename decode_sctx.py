#!/usr/bin/env python3
"""
SCTX decoder for Clash of Clans / Supercell game sprites.
Reads the FlatBuffers-based SCTX format, decompresses ZSTD,
decodes ASTC texture, and saves as PNG.
"""

import os, sys, struct, argparse
import zstandard
from PIL import Image
import texture2ddecoder

# ScPixel::Type ASTC block sizes (from sc-workshop/SupercellTexture ScPixel.hpp)
# pixel_type_value -> (block_x, block_y)
ASTC_BLOCK_SIZES = {
    # SRGB variants  (186–200)
    186: (4,4), 187: (5,4), 188: (5,5), 189: (6,5), 190: (6,6),
    192: (8,5), 193: (8,6), 194: (8,8),
    195: (10,5), 196: (10,6), 197: (10,8), 198: (10,10),
    199: (12,10), 200: (12,12),
    # Uniform ASTC  (204–208)
    204: (4,4), 205: (5,4), 206: (5,5), 207: (6,5), 208: (6,6),
    # Standard ASTC (210–218)
    210: (8,5), 211: (8,6), 212: (8,8),
    213: (10,5), 214: (10,6), 215: (10,8), 216: (10,10),
    217: (12,10), 218: (12,12),
}

FLAG_USE_COMPRESSION = 1
FLAG_USE_PADDING     = 8


def read_u16(data, offset):
    return struct.unpack_from('<H', data, offset)[0]

def read_u32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]

def read_i32(data, offset):
    return struct.unpack_from('<i', data, offset)[0]


def parse_sctx_header(data):
    """
    Parse the FlatBuffers SCTX Header and return:
        (pixel_type, width, height, flags, texture_length, texture_data_start)
    """
    # Bytes 0-3: size of the FlatBuffers header blob
    fb_header_len = read_u32(data, 0)
    # FlatBuffers buffer starts at byte 4
    fb_start = 4
    # Root table offset (from fb_start)
    root_offset = read_u32(data, fb_start)
    root_pos = fb_start + root_offset          # absolute file offset of root table

    # vtable offset (signed, backward from root_pos)
    vtable_offset = read_i32(data, root_pos)
    vtable_pos = root_pos - vtable_offset      # absolute file offset of vtable

    # Read vtable to find field offsets
    vtable_size = read_u16(data, vtable_pos)
    # table_data_size = read_u16(data, vtable_pos + 2)  # unused
    n_fields = (vtable_size - 4) // 2
    field_offsets = [
        read_u16(data, vtable_pos + 4 + i * 2) for i in range(n_fields)
    ]

    def table_field_u16(field_idx, default=0):
        if field_idx >= n_fields or field_offsets[field_idx] == 0:
            return default
        return read_u16(data, root_pos + field_offsets[field_idx])

    def table_field_u32(field_idx, default=0):
        if field_idx >= n_fields or field_offsets[field_idx] == 0:
            return default
        return read_u32(data, root_pos + field_offsets[field_idx])

    def table_field_i32(field_idx, default=0):
        if field_idx >= n_fields or field_offsets[field_idx] == 0:
            return default
        return read_i32(data, root_pos + field_offsets[field_idx])

    # Schema field indices:
    # 0=unk1(u16), 1=pixel_type(u32), 2=width(u16), 3=height(u16),
    # 4=levels_count(u8), 5=unk3(u8), 6=flags(u32), 7=texture_length(i32)
    pixel_type     = table_field_u32(1)
    width          = table_field_u16(2)
    height         = table_field_u16(3)
    flags          = table_field_u32(6)
    texture_length = table_field_i32(7)

    # FlatBuffers header ends at fb_start + fb_header_len
    header_end = fb_start + fb_header_len   # = 4 + 48 = 52

    # Mip maps section: 4-byte total length + individual mip map entries
    mip_maps_total_len = read_u32(data, header_end)
    texture_data_start = header_end + 4 + mip_maps_total_len

    if flags & FLAG_USE_PADDING:
        # Align to 16 bytes
        texture_data_start = (texture_data_start + 15) & ~15

    return pixel_type, width, height, flags, texture_length, texture_data_start


def decode_sctx(file_path, out_dir):
    with open(file_path, 'rb') as f:
        data = f.read()

    basename = os.path.splitext(os.path.basename(file_path))[0]
    out_path  = os.path.join(out_dir, basename + '.png')

    try:
        pixel_type, width, height, flags, texture_length, tex_start = parse_sctx_header(data)
    except Exception as e:
        print(f'  [SKIP] {basename}: header parse failed – {e}')
        return False

    if width == 0 or height == 0:
        print(f'  [SKIP] {basename}: zero dimensions ({width}x{height})')
        return False

    block_size = ASTC_BLOCK_SIZES.get(pixel_type)
    if block_size is None:
        print(f'  [SKIP] {basename}: unknown pixel_type {pixel_type}')
        return False

    bx, by = block_size
    raw_tex = data[tex_start:]

    # Decompress if flag says so
    if flags & FLAG_USE_COMPRESSION:
        try:
            ctx = zstandard.ZstdDecompressor()
            raw_tex = ctx.decompress(raw_tex)
        except Exception as e:
            print(f'  [SKIP] {basename}: ZSTD decompress failed – {e}')
            return False

    # Decode ASTC → raw RGBA bytes
    try:
        rgba_bytes = texture2ddecoder.decode_astc(raw_tex, width, height, bx, by)
    except Exception as e:
        print(f'  [SKIP] {basename}: ASTC decode failed – {e}')
        return False

    # Save PNG (BGRA → RGBA swap needed)
    try:
        img = Image.frombytes('RGBA', (width, height), rgba_bytes, 'raw', 'BGRA')
        img.save(out_path)
        print(f'  [OK]   {basename}.png  ({width}x{height}  ASTC {bx}x{by})')
        return True
    except Exception as e:
        print(f'  [SKIP] {basename}: PNG save failed – {e}')
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decode Supercell .sctx files to PNG')
    parser.add_argument('input',  help='Single .sctx file or directory of .sctx files')
    parser.add_argument('-o', '--output', default='.', help='Output directory (default: cwd)')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if os.path.isdir(args.input):
        files = [
            os.path.join(args.input, f)
            for f in os.listdir(args.input)
            if f.endswith('.sctx') and not f.endswith('.sctx.meta')
        ]
        print(f'Found {len(files)} .sctx files')
        ok = fail = 0
        for fp in sorted(files):
            if decode_sctx(fp, args.output):
                ok += 1
            else:
                fail += 1
        print(f'\nDone: {ok} decoded, {fail} skipped')
    else:
        decode_sctx(args.input, args.output)
