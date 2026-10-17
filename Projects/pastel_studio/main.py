"""Pastel Studio entry point.

    python main.py                      # open the desktop app
    python main.py photo.jpg            # open the app with a photo loaded
    python main.py photo.jpg --output art.png --video drawing.mp4
                                        # render without the GUI
"""

from __future__ import annotations

import argparse
import os
import sys

# Allow `python pastel_studio/main.py` from any working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _check_dependencies() -> None:
    missing = []
    for module, package in (("numpy", "numpy"), ("cv2", "opencv-python-headless"),
                            ("PIL", "Pillow")):
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        sys.exit("Missing packages: " + ", ".join(missing)
                 + "\nInstall them with:  pip install -r requirements.txt")


def _run_headless(args) -> int:
    from image_processor import ImageLoadError, load_image
    from pipeline import create_artwork
    from settings import ArtSettings, ExportSettings
    from video_exporter import VideoExportError, export_image, export_video

    def progress(frac, msg=""):
        print(f"\r[{int(frac * 100):3d}%] {msg:<60}", end="", flush=True)

    try:
        image = load_image(args.image)
    except ImageLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    settings = ArtSettings(aspect=args.aspect, resolution=args.quality, seed=args.seed)
    plan = create_artwork(image, settings, progress=progress)
    print()
    try:
        if args.output:
            export_image(plan, args.output)
            print(f"Artwork saved to {args.output}")
        if args.video:
            vs = ExportSettings(duration=args.duration, fps=args.fps,
                                resolution=args.video_resolution, video_format=args.video_format)
            encoder = export_video(plan, args.video, vs, progress=progress)
            print(f"\nVideo saved to {args.video} ({encoder})")
    except (VideoExportError, ValueError) as exc:
        print(f"\nerror: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    _check_dependencies()
    from settings import ASPECTS, RESOLUTIONS, VIDEO_FORMATS, VIDEO_RESOLUTIONS

    parser = argparse.ArgumentParser(description="Pastel Studio: photo to oil pastel drawing")
    parser.add_argument("image", nargs="?", help="photo to open")
    parser.add_argument("--output", help="save the artwork (PNG/JPEG) without opening the GUI")
    parser.add_argument("--video", help="save the drawing video (MP4) without opening the GUI")
    parser.add_argument("--aspect", default="Original", choices=list(ASPECTS))
    parser.add_argument("--quality", default="Standard (1200 px)", choices=list(RESOLUTIONS))
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--video-resolution", default="1080p", choices=list(VIDEO_RESOLUTIONS))
    parser.add_argument("--video-format", default="Match artwork", choices=list(VIDEO_FORMATS))
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    if args.output or args.video:
        if not args.image:
            parser.error("an input image is required with --output/--video")
        return _run_headless(args)

    try:
        import tkinter as tk
    except ImportError:
        sys.exit("Tkinter is not available in this Python installation.\n"
                 "  Debian/Ubuntu: sudo apt install python3-tk\n"
                 "  Fedora:        sudo dnf install python3-tkinter\n"
                 "  Arch:          sudo pacman -S tk\n"
                 "  macOS/Windows: use the installer from python.org (includes Tk)")

    if sys.platform == "win32":
        try:  # crisp rendering on high-DPI Windows displays
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass

    from gui import PastelStudioApp

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        sys.exit(f"Could not open a window (is a display available?): {exc}")
    PastelStudioApp(root, initial_image=args.image)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
