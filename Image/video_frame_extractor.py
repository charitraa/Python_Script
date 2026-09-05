#!/usr/bin/env python3
"""
Video Frame Extractor
---------------------
Turns a video into pictures: writes out every frame (or a sampled subset)
as individual image files.

Examples
--------
    # every single frame of the video -> ./clip_frames/
    python video_frame_extractor.py clip.mp4

    # 1 image per second, as PNG, into a chosen folder
    python video_frame_extractor.py clip.mp4 --fps 1 --format png -o thumbs

    # every 10th frame, only between 00:30 and 01:15, scaled to half size
    python video_frame_extractor.py clip.mp4 --every 10 --start 00:30 --end 1:15 --scale 0.5

    # several videos at once (each gets its own output folder)
    python video_frame_extractor.py a.mp4 b.mkv c.mov --fps 2

Run with no arguments for an interactive prompt-based mode.

Requires: opencv-python  (pip install opencv-python)
"""

import argparse
import os
import sys

try:
    import cv2
except ImportError:
    sys.exit(
        "Error: OpenCV is not installed.\n"
        "Install it with:  pip install opencv-python"
    )

# tqdm gives a nice progress bar, but the script works fine without it.
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


# Extensions we are willing to treat as a video when scanning a directory.
VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv",
    ".wmv", ".m4v", ".mpg", ".mpeg", ".ts", ".3gp",
}


def parse_timecode(value):
    """
    Convert a time string into seconds (float).

    Accepts plain seconds ("12", "12.5"), "MM:SS" ("01:30") or
    "HH:MM:SS" ("00:01:30.25"). Returns None for empty input.
    """
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None

    parts = value.split(":")
    if len(parts) > 3:
        raise ValueError(f"Invalid time '{value}' (use SS, MM:SS or HH:MM:SS)")

    try:
        parts = [float(p) for p in parts]
    except ValueError:
        raise ValueError(f"Invalid time '{value}' (non-numeric part)")

    seconds = 0.0
    for part in parts:          # left-to-right: HH, MM, SS
        seconds = seconds * 60 + part
    if seconds < 0:
        raise ValueError(f"Invalid time '{value}' (negative)")
    return seconds


def parse_resize(value):
    """
    Parse a '--resize' argument like '1920x1080', '640x' or 'x480'.

    A missing side means "work it out from the aspect ratio".
    Returns (width_or_None, height_or_None).
    """
    if not value:
        return None
    text = value.lower().replace(" ", "")
    if "x" not in text:
        raise ValueError("Use WIDTHxHEIGHT, e.g. 1280x720 (one side may be blank)")

    w_text, _, h_text = text.partition("x")
    width = int(w_text) if w_text else None
    height = int(h_text) if h_text else None

    if width is None and height is None:
        raise ValueError("At least one of width/height must be given")
    if (width is not None and width <= 0) or (height is not None and height <= 0):
        raise ValueError("Width/height must be positive")
    return width, height


def target_size(frame_w, frame_h, resize, scale):
    """
    Work out the output size for a frame, or None if it should be left alone.
    'resize' wins over 'scale' when both are supplied.
    """
    if resize:
        width, height = resize
        if width is None:
            width = max(1, round(frame_w * height / frame_h))
        elif height is None:
            height = max(1, round(frame_h * width / frame_w))
        return width, height

    if scale and scale != 1.0:
        return max(1, round(frame_w * scale)), max(1, round(frame_h * scale))

    return None


def encode_params(fmt, quality):
    """Build the OpenCV imwrite parameters for the chosen output format."""
    if fmt in ("jpg", "jpeg"):
        return [cv2.IMWRITE_JPEG_QUALITY, int(quality)]
    if fmt == "webp":
        return [cv2.IMWRITE_WEBP_QUALITY, int(quality)]
    if fmt == "png":
        # PNG is lossless; map 0-100 "quality" onto 9-0 compression effort.
        return [cv2.IMWRITE_PNG_COMPRESSION, max(0, min(9, 9 - int(quality) // 12))]
    return []


def human_duration(seconds):
    """Format a number of seconds as H:MM:SS.mmm for readable logging."""
    if seconds is None:
        return "unknown"
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{int(hours)}:{int(minutes):02d}:{secs:06.3f}"


def collect_videos(paths):
    """Expand the given paths into a flat list of video files."""
    videos = []
    for path in paths:
        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                full = os.path.join(path, name)
                if os.path.isfile(full) and os.path.splitext(name)[1].lower() in VIDEO_EXTENSIONS:
                    videos.append(full)
        elif os.path.isfile(path):
            videos.append(path)
        else:
            print(f"Warning: skipping '{path}' (not a file or directory)")
    return videos


def extract_frames(video_path, output_dir=None, every=1, fps=None,
                   start=None, end=None, fmt="jpg", quality=95,
                   resize=None, scale=None, max_frames=None,
                   prefix=None, overwrite=False, dry_run=False, quiet=False):
    """
    Extract frames from a single video and save them as image files.

    every      : keep 1 out of every N frames (1 = every frame)
    fps        : keep this many frames per second instead (overrides 'every')
    start/end  : time window in seconds
    max_frames : stop after writing this many images

    Returns the number of images written (or that would be written on a dry run).
    """
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        print(f"Error: could not open '{video_path}' (unsupported or corrupt file?)")
        return 0

    # Video metadata. Some containers lie or report 0, so everything is guarded.
    source_fps = capture.get(cv2.CAP_PROP_FPS) or 0.0
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = total_frames / source_fps if source_fps > 0 and total_frames > 0 else None

    stem = os.path.splitext(os.path.basename(video_path))[0]
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(video_path)), f"{stem}_frames")
    if prefix is None:
        prefix = "frame"

    # Translate --fps into a "keep 1 in N" step against the source frame rate.
    step = max(1, int(every))
    if fps:
        if source_fps <= 0:
            print("Warning: source frame rate unknown, --fps ignored (using --every instead)")
        else:
            step = max(1, round(source_fps / float(fps)))

    start_frame = 0
    if start is not None and source_fps > 0:
        start_frame = int(start * source_fps)
    end_frame = None
    if end is not None and source_fps > 0:
        end_frame = int(end * source_fps)
        if end_frame <= start_frame:
            print(f"Error: --end must be after --start for '{video_path}'")
            capture.release()
            return 0

    if not quiet:
        print(f"\n--- {os.path.basename(video_path)} ---")
        print(f"  resolution : {width}x{height}" if width else "  resolution : unknown")
        print(f"  frame rate : {source_fps:.3f} fps" if source_fps else "  frame rate : unknown")
        print(f"  frames     : {total_frames or 'unknown'}")
        print(f"  duration   : {human_duration(duration)}")
        print(f"  keeping    : every {step} frame(s)"
              + (f" (~{source_fps / step:.2f} images/sec)" if source_fps else ""))
        print(f"  output     : {output_dir}")

    # Number of images we expect, used for zero-padding and the progress bar.
    last_frame = end_frame if end_frame is not None else total_frames
    expected = None
    if last_frame and last_frame > start_frame:
        expected = (last_frame - start_frame + step - 1) // step
        if max_frames:
            expected = min(expected, max_frames)
    pad = max(4, len(str(expected)) if expected else 6)

    if dry_run:
        capture.release()
        print(f"  [dry run] would write {expected if expected is not None else 'an unknown number of'} image(s)")
        return expected or 0

    os.makedirs(output_dir, exist_ok=True)

    # Jump straight to the start of the window; from there we read sequentially,
    # which is far more reliable (and faster) than seeking per frame.
    if start_frame > 0:
        capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    params = encode_params(fmt, quality)
    extension = "jpg" if fmt == "jpeg" else fmt
    resize_to = None                      # decided once, on the first real frame

    progress = tqdm(total=expected, unit="img", desc=stem[:20], leave=False) if (tqdm and not quiet) else None

    frame_index = start_frame
    selected = 0      # frames picked by the sampling step
    written = 0       # images actually saved
    skipped = 0       # already on disk, left alone
    failed = 0        # encoder refused them
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break                     # end of stream (or an unreadable frame)

            if end_frame is not None and frame_index >= end_frame:
                break

            if (frame_index - start_frame) % step == 0:
                if resize_to is None:
                    frame_h, frame_w = frame.shape[:2]
                    resize_to = target_size(frame_w, frame_h, resize, scale) or False

                image = frame
                if resize_to:
                    # INTER_AREA for shrinking, INTER_CUBIC for enlarging.
                    shrinking = resize_to[0] < frame.shape[1]
                    image = cv2.resize(
                        frame, resize_to,
                        interpolation=cv2.INTER_AREA if shrinking else cv2.INTER_CUBIC,
                    )

                filename = f"{prefix}_{selected + 1:0{pad}d}.{extension}"
                out_path = os.path.join(output_dir, filename)

                # The counter always advances so numbering stays sequential
                # even when an image is skipped or fails to encode.
                selected += 1

                if os.path.exists(out_path) and not overwrite:
                    skipped += 1
                elif cv2.imwrite(out_path, image, params):
                    written += 1
                else:
                    failed += 1
                    print(f"\nWarning: failed to write '{out_path}'")

                if progress:
                    progress.update(1)

                if max_frames and selected >= max_frames:
                    break

            frame_index += 1
    except KeyboardInterrupt:
        print("\nInterrupted - stopping early, images written so far are kept.")
    finally:
        if progress:
            progress.close()
        capture.release()

    if not quiet:
        print(f"  done: {written} image(s) in '{output_dir}'"
              + (f", {skipped} already existed (use --overwrite)" if skipped else "")
              + (f", {failed} failed" if failed else ""))
    return written


def interactive():
    """Prompt-driven mode, used when the script is run without arguments."""
    print("--- Video Frame Extractor ---")
    print("Saves the frames of a video as individual image files.\n")

    while True:
        video = input("Path to the video file: ").strip().strip("'\"")
        if os.path.isfile(video):
            break
        print(f"  '{video}' is not a file. Try again.")

    output_dir = input("Output folder (blank = <video name>_frames): ").strip().strip("'\"") or None

    print("\nHow many frames do you want?")
    print("  1) Every frame")
    print("  2) Every Nth frame")
    print("  3) N images per second")
    choice = input("Choice [1]: ").strip() or "1"

    every, fps = 1, None
    if choice == "2":
        every = int(input("  Keep 1 frame out of every N: ").strip() or "1")
    elif choice == "3":
        fps = float(input("  Images per second: ").strip() or "1")

    fmt = (input("\nImage format jpg/png/webp [jpg]: ").strip().lower() or "jpg")
    if fmt not in ("jpg", "jpeg", "png", "webp"):
        print(f"  Unknown format '{fmt}', using jpg.")
        fmt = "jpg"

    start = parse_timecode(input("Start time (blank = beginning): ").strip())
    end = parse_timecode(input("End time (blank = end of video): ").strip())

    count = extract_frames(video, output_dir=output_dir, every=every, fps=fps,
                           start=start, end=end, fmt=fmt)
    print(f"\nFinished. {count} image(s) written.")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Extract the frames of a video as individual image files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  %(prog)s clip.mp4                       every frame -> ./clip_frames/\n"
            "  %(prog)s clip.mp4 --fps 1 --format png  one PNG per second\n"
            "  %(prog)s clip.mp4 --every 10 --scale .5 every 10th frame, half size\n"
            "  %(prog)s videos/ --fps 2 -o out/        every video in a folder\n"
        ),
    )
    parser.add_argument("videos", nargs="*",
                        help="video file(s), or a folder of videos")
    parser.add_argument("-o", "--output", metavar="DIR",
                        help="output folder (default: <video name>_frames next to the video)")

    sampling = parser.add_mutually_exclusive_group()
    sampling.add_argument("-n", "--every", type=int, default=1, metavar="N",
                          help="keep 1 frame out of every N (default: 1, i.e. every frame)")
    sampling.add_argument("--fps", type=float, metavar="F",
                          help="keep F images per second instead of a fixed step")

    parser.add_argument("--start", metavar="TIME",
                        help="start at this point (SS, MM:SS or HH:MM:SS)")
    parser.add_argument("--end", metavar="TIME",
                        help="stop at this point (SS, MM:SS or HH:MM:SS)")
    parser.add_argument("--max-frames", type=int, metavar="N",
                        help="stop after writing N images per video")

    parser.add_argument("-f", "--format", default="jpg",
                        choices=["jpg", "jpeg", "png", "webp"],
                        help="output image format (default: jpg)")
    parser.add_argument("-q", "--quality", type=int, default=95, metavar="0-100",
                        help="JPEG/WebP quality, or PNG compression effort (default: 95)")
    parser.add_argument("--resize", metavar="WxH",
                        help="resize output, e.g. 1280x720, 640x or x480")
    parser.add_argument("--scale", type=float, metavar="S",
                        help="scale output by a factor, e.g. 0.5")
    parser.add_argument("--prefix", default=None, metavar="TEXT",
                        help="filename prefix (default: 'frame')")

    parser.add_argument("--overwrite", action="store_true",
                        help="replace images that already exist (default: leave them)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would be written without writing anything")
    parser.add_argument("--quiet", action="store_true",
                        help="only report errors")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # No video given -> fall back to the friendly interactive mode.
    if not args.videos:
        if sys.stdin.isatty():
            interactive()
            return 0
        parser.print_help()
        return 1

    try:
        start = parse_timecode(args.start)
        end = parse_timecode(args.end)
        resize = parse_resize(args.resize)
    except ValueError as exc:
        parser.error(str(exc))

    if end is not None and start is not None and end <= start:
        parser.error("--end must be later than --start")
    if not 0 <= args.quality <= 100:
        parser.error("--quality must be between 0 and 100")
    if args.scale is not None and args.scale <= 0:
        parser.error("--scale must be greater than 0")
    if args.every < 1:
        parser.error("--every must be at least 1")
    if args.fps is not None and args.fps <= 0:
        parser.error("--fps must be greater than 0")

    videos = collect_videos(args.videos)
    if not videos:
        print("No video files found.")
        return 1

    total = 0
    for video in videos:
        # With several videos and one -o folder, give each its own subfolder
        # so the frames don't overwrite each other.
        output_dir = args.output
        if output_dir and len(videos) > 1:
            output_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(video))[0])

        total += extract_frames(
            video,
            output_dir=output_dir,
            every=args.every,
            fps=args.fps,
            start=start,
            end=end,
            fmt=args.format,
            quality=args.quality,
            resize=resize,
            scale=args.scale,
            max_frames=args.max_frames,
            prefix=args.prefix,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            quiet=args.quiet,
        )

    if len(videos) > 1 and not args.quiet:
        print(f"\nAll done: {total} image(s) from {len(videos)} video(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
