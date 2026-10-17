"""Export the finished artwork (PNG/JPEG) and the drawing process (MP4).

Video frames are produced by the same AnimationEngine used on screen, so the
MP4 shows the real stroke-by-stroke process. FFmpeg (libx264) is preferred;
if it is not installed, OpenCV's built-in MPEG-4 writer is used instead.
"""

from __future__ import annotations

import math
import os
import shutil
import subprocess
import tempfile

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from animation_engine import AnimationEngine, CursorSmoother, draw_pastel_stick, stage_background
from models import CancelToken, DrawingPlan
from settings import VIDEO_FORMATS, VIDEO_RESOLUTIONS, ExportSettings

BACKGROUND = (22, 18, 15)


class VideoExportError(Exception):
    pass


# --------------------------------------------------------------------------- images
def export_image(plan: DrawingPlan, path: str, jpeg_quality: int = 95) -> None:
    ext = os.path.splitext(path)[1].lower()
    img = Image.fromarray(plan.final_uint8())
    try:
        if ext in (".jpg", ".jpeg"):
            img.save(path, "JPEG", quality=jpeg_quality, subsampling=0, optimize=True)
        elif ext == ".png":
            img.save(path, "PNG", optimize=True)
        else:
            raise ValueError(f"Unsupported image format '{ext}'. Use .png or .jpg.")
    except OSError as exc:
        raise VideoExportError(f"Could not save the image:\n{exc}") from exc


# --------------------------------------------------------------------------- encoders
def find_ffmpeg() -> str | None:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:  # optional: pip install imageio-ffmpeg bundles a binary
        import imageio_ffmpeg  # type: ignore
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def describe_encoder() -> str:
    exe = find_ffmpeg()
    if exe:
        return _ENCODER_NAMES[_pick_codec(exe)]
    return "OpenCV (MPEG-4) - install FFmpeg for smaller, more compatible files"


# Preferred first: NVIDIA's hardware encoder (frees the CPU for stroke
# rendering), then software H.264, then MPEG-4 which every FFmpeg build has.
_CODECS = {
    "h264_nvenc": ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "19", "-b:v", "0"],
    "libx264": ["-c:v", "libx264", "-preset", "medium", "-crf", "18"],
    "mpeg4": ["-c:v", "mpeg4", "-q:v", "3"],
}
_ENCODER_NAMES = {
    "h264_nvenc": "FFmpeg (H.264, NVIDIA GPU)",
    "libx264": "FFmpeg (H.264)",
    "mpeg4": "FFmpeg (MPEG-4)",
}
_CODEC_CACHE: dict[str, str] = {}


def _codec_works(exe: str, codec: str) -> bool:
    """Encode one tiny frame; listing an encoder does not mean the GPU/driver can use it."""
    try:
        return subprocess.run(
            [exe, "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
             "color=c=black:s=256x256:d=0.1", "-frames:v", "1", *_CODECS[codec],
             "-pix_fmt", "yuv420p", "-f", "null", "-"],
            capture_output=True, timeout=20).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _pick_codec(exe: str) -> str:
    if exe not in _CODEC_CACHE:
        if os.environ.get("PASTEL_NO_GPU"):
            candidates = ("libx264", "mpeg4")
        else:
            candidates = ("h264_nvenc", "libx264", "mpeg4")
        _CODEC_CACHE[exe] = next((c for c in candidates if _codec_works(exe, c)), "mpeg4")
    return _CODEC_CACHE[exe]


class _FFmpegWriter:
    def __init__(self, exe: str, path: str, size: tuple[int, int], fps: int) -> None:
        codec = _CODECS[_pick_codec(exe)]
        cmd = [exe, "-y", "-hide_banner", "-loglevel", "error",
               "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{size[0]}x{size[1]}", "-r", str(fps), "-i", "-",
               "-an", *codec, "-pix_fmt", "yuv420p", "-movflags", "+faststart", path]
        self._log = tempfile.TemporaryFile()
        try:
            self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                         stderr=self._log)
        except OSError as exc:
            raise VideoExportError(f"Could not start FFmpeg:\n{exc}") from exc

    def write(self, frame: np.ndarray) -> None:
        try:
            self.proc.stdin.write(frame.tobytes())
        except (BrokenPipeError, OSError) as exc:
            raise VideoExportError("FFmpeg stopped unexpectedly:\n" + self._errors()) from exc

    def _errors(self) -> str:
        self._log.seek(0)
        return self._log.read().decode(errors="replace")[-1500:]

    def close(self, abort: bool = False) -> None:
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        if abort:
            self.proc.kill()
        code = self.proc.wait()
        errors = self._errors() if code != 0 and not abort else ""
        self._log.close()
        if errors or (code != 0 and not abort):
            raise VideoExportError("FFmpeg failed:\n" + errors)


class _OpenCVWriter:
    def __init__(self, path: str, size: tuple[int, int], fps: int) -> None:
        self.writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
        if not self.writer.isOpened():
            raise VideoExportError(
                "No MP4 video encoder is available.\n\n"
                "Install FFmpeg (https://ffmpeg.org) and make sure 'ffmpeg' is on your PATH, "
                "or run: pip install imageio-ffmpeg")

    def write(self, frame: np.ndarray) -> None:
        self.writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def close(self, abort: bool = False) -> None:
        self.writer.release()


# --------------------------------------------------------------------------- layout
def _even(v: float) -> int:
    return max(2, int(round(v / 2)) * 2)


def video_layout(art_size: tuple[int, int], settings: ExportSettings):
    """Return (frame size, artwork rectangle (x, y, w, h))."""
    aw, ah = art_size
    short = VIDEO_RESOLUTIONS.get(settings.resolution, 1080)
    ratio = VIDEO_FORMATS.get(settings.video_format)
    if ratio is None:
        art_ratio = aw / ah
        W, H = (short * art_ratio, short) if art_ratio >= 1 else (short, short / art_ratio)
        margin = 0.05
    else:
        rw, rh = ratio
        W, H = (short * rw / rh, short) if rw >= rh else (short, short * rh / rw)
        margin = 0.07
    W, H = _even(W), _even(H)
    caption_space = 0.07 * H if settings.show_captions else 0.0
    box_w = W * (1 - 2 * margin)
    box_h = H * (1 - 2 * margin) - caption_space
    scale = min(box_w / aw, box_h / ah)
    rw_, rh_ = _even(aw * scale), _even(ah * scale)
    x = (W - rw_) // 2
    y = int((H - caption_space - rh_) / 2)
    return (W, H), (x, y, rw_, rh_)


def _font(size: int):
    for name in ("DejaVuSans.ttf", "Arial.ttf", "arial.ttf", "Helvetica.ttc",
                 "segoeui.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


# --------------------------------------------------------------------------- export
def export_video(plan: DrawingPlan, path: str, settings: ExportSettings,
                 progress=None, cancel: CancelToken | None = None) -> str:
    """Render the drawing process to `path`. Returns the encoder description."""
    cancel = cancel or CancelToken()
    report = progress or (lambda *_: None)
    (W, H), (rx, ry, rw, rh) = video_layout(plan.size, settings)
    fps = int(settings.fps)
    duration = float(settings.duration)
    n_anim = int(round(duration * fps))
    n_total = n_anim + int(round(settings.hold_final_seconds * fps)) + 1

    exe = find_ffmpeg()
    writer = _FFmpegWriter(exe, path, (W, H), fps) if exe else _OpenCVWriter(path, (W, H), fps)
    encoder = describe_encoder()

    engine = AnimationEngine(plan, duration)
    cursor = CursorSmoother()
    background = stage_background((W, H), (rx, ry, rw, rh), BACKGROUND)
    font = _font(max(14, int(H * 0.026)))
    stick = max(10.0, max(rw, rh) / 46.0)
    bar_y = ry + rh + int(H * 0.035)
    try:
        for i in range(n_total):
            if (i & 7) == 0:
                cancel.check()
                report(i / n_total, f"Rendering frame {i + 1:,} of {n_total:,}")
            t = min(i / fps, duration)
            info = engine.advance_to(t)
            art = engine.compose(info, (rw, rh), BACKGROUND)
            frame = background.copy()
            frame[ry:ry + rh, rx:rx + rw] = art
            img = Image.fromarray(frame)
            if settings.show_cursor:
                cur = cursor.update(engine.scale_cursor(info, (rw, rh)), 1.0 / fps)
                if cur is not None:
                    draw_pastel_stick(img, cur[0] + rx, cur[1] + ry, cur[2], cur[3], stick)
            if settings.show_captions:
                _draw_caption(img, info, font, (rx, bar_y, rw))
            writer.write(np.asarray(img))
        writer.close()
    except BaseException:  # cancelled or failed: never leave a broken file behind
        writer.close(abort=True)
        _remove_quietly(path)
        raise
    report(1.0, "Video saved")
    return encoder


def _draw_caption(img: Image.Image, info, font, bar) -> None:
    x, y, w = bar
    d = ImageDraw.Draw(img, "RGBA")
    label = info.stage_label if info.stage_key != "final" or info.finished else "Finishing"
    d.text((x, y), label.upper(), font=font, fill=(239, 228, 212, 230))
    pct = f"{int(info.progress * 100)}%"
    tw = d.textlength(pct, font=font)
    d.text((x + w - tw, y), pct, font=font, fill=(239, 228, 212, 150))
    by = y + int(font.size * 1.6) if hasattr(font, "size") else y + 24
    d.rectangle([x, by, x + w, by + 2], fill=(255, 255, 255, 40))
    d.rectangle([x, by, x + int(w * info.progress), by + 2], fill=(196, 87, 58, 255))


def _remove_quietly(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def estimate_frames(settings: ExportSettings) -> int:
    return int(math.ceil((settings.duration + settings.hold_final_seconds) * settings.fps))
