"""Image loading, framing and analysis.

This module turns a photograph into the measurements the stroke generator
needs: an enhanced colour target at several levels of abstraction, a colour
palette, edge maps, a stroke-direction field and an importance map.
The original file is only ever read, never written.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from models import CancelToken
from settings import ASPECTS, SUPPORTED_EXTENSIONS, ArtSettings

# Warm off-white used where the picture does not cover the paper (fit mode).
PAPER_RGB = np.array([0.955, 0.932, 0.885], dtype=np.float32)

# Refuse absurd inputs before decoding them into memory.
MAX_SOURCE_PIXELS = 120_000_000


class ImageLoadError(Exception):
    pass


def load_image(path: str) -> Image.Image:
    """Load a JPG/PNG/WebP file as an RGB Pillow image (EXIF orientation applied)."""
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ImageLoadError(
            f"Unsupported file type '{ext or '(none)'}'. "
            f"Please choose one of: {', '.join(SUPPORTED_EXTENSIONS)}."
        )
    if not os.path.isfile(path):
        raise ImageLoadError(f"File not found:\n{path}")
    try:
        with Image.open(path) as im:
            if im.width * im.height > MAX_SOURCE_PIXELS:
                raise ImageLoadError(
                    f"The image is too large ({im.width}x{im.height}). "
                    "Please use an image under 120 megapixels."
                )
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "LA", "P"):
                # Flatten transparency onto paper colour instead of black.
                im = im.convert("RGBA")
                bg = Image.new("RGBA", im.size, tuple(int(c * 255) for c in PAPER_RGB) + (255,))
                im = Image.alpha_composite(bg, im)
            return im.convert("RGB")
    except ImageLoadError:
        raise
    except UnidentifiedImageError as exc:
        raise ImageLoadError("The file could not be read as an image. It may be corrupt.") from exc
    except MemoryError as exc:
        raise ImageLoadError("Not enough memory to open this image.") from exc
    except OSError as exc:
        raise ImageLoadError(f"Could not open the image:\n{exc}") from exc


def frame_image(image: Image.Image, settings: ArtSettings) -> tuple[np.ndarray, np.ndarray]:
    """Resize and crop/fit the photo onto the drawing canvas.

    Returns (rgb uint8 HxWx3, valid float32 HxW) where `valid` marks the area
    the artist should cover with pastel (all ones except the margin in fit mode).
    """
    long_side = settings.long_side
    src_w, src_h = image.size
    aspect = ASPECTS.get(settings.aspect)
    if aspect is None:
        aspect = src_w / src_h

    if aspect >= 1:
        cw, ch = long_side, round(long_side / aspect)
    else:
        cw, ch = round(long_side * aspect), long_side
    cw, ch = max(cw, 64), max(ch, 64)

    if settings.framing.startswith("Fit"):
        margin = round(min(cw, ch) * 0.07)
        box_w, box_h = cw - 2 * margin, ch - 2 * margin
        scale = min(box_w / src_w, box_h / src_h)
        nw, nh = max(1, round(src_w * scale)), max(1, round(src_h * scale))
        resized = image.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = np.empty((ch, cw, 3), np.uint8)
        canvas[:] = (PAPER_RGB * 255).astype(np.uint8)
        x0, y0 = (cw - nw) // 2, (ch - nh) // 2
        canvas[y0:y0 + nh, x0:x0 + nw] = np.asarray(resized)
        valid = np.zeros((ch, cw), np.float32)
        valid[y0:y0 + nh, x0:x0 + nw] = 1.0
        return canvas, valid

    fitted = ImageOps.fit(image, (cw, ch), Image.Resampling.LANCZOS, centering=(0.5, 0.45))
    return np.asarray(fitted).copy(), np.ones((ch, cw), np.float32)


@dataclass
class SourceAnalysis:
    rgb: np.ndarray            # float32 original framed photo, 0..1
    target: np.ndarray         # float32 enhanced colour target, 0..1
    levels: dict               # name -> float32 blurred/abstracted target
    lab_palette: np.ndarray    # (K, 3) palette in RGB 0..1
    gray: np.ndarray           # float32 luminance of the target, 0..1
    edges_coarse: np.ndarray   # uint8 0/255 edges of the main shapes
    edges_fine: np.ndarray     # uint8 0/255 detailed edges
    edge_strength: np.ndarray  # float32 0..1 gradient magnitude
    dir_cos: np.ndarray        # float32 stroke direction field (unit vectors)
    dir_sin: np.ndarray
    importance: np.ndarray     # float32 0..1 where detail matters most
    valid: np.ndarray          # float32 0/1 paintable area
    faces: list                # [(x, y, w, h)]
    scale: float               # long side / 1000, used to scale stroke sizes

    @property
    def size(self) -> tuple[int, int]:
        h, w = self.gray.shape
        return w, h


def _enhance(rgb: np.ndarray, richness: float) -> np.ndarray:
    """Boost contrast and saturation the way pastel pigments read on paper."""
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)  # float input: L 0..100, a/b ~ -127..127
    l_chan = np.clip(lab[..., 0] * 2.55, 0, 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=1.2 + 1.6 * richness, tileGridSize=(8, 8))
    l_eq = clahe.apply(l_chan).astype(np.float32) / 2.55
    lab[..., 0] = 0.55 * lab[..., 0] + 0.45 * l_eq
    chroma = 1.0 + 0.55 * richness
    lab[..., 1] *= chroma
    lab[..., 2] *= chroma
    # Slightly lift shadows so dark areas still carry colour, like wax over paper.
    lab[..., 0] = 4.0 + lab[..., 0] * 0.96
    out = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    return np.clip(out, 0.0, 1.0)


def _abstract(rgb: np.ndarray, scale: float) -> np.ndarray:
    """Edge-preserving smoothing: flattens texture but keeps shapes."""
    img = (rgb * 255).astype(np.uint8)
    d = max(5, int(round(9 * scale)) | 1)
    for _ in range(2):
        img = cv2.bilateralFilter(img, d, 28, 6 * scale + 3)
    return img.astype(np.float32) / 255.0


def _palette(rgb: np.ndarray, k: int, seed: int) -> np.ndarray:
    small = cv2.resize(rgb, (160, max(16, int(160 * rgb.shape[0] / rgb.shape[1]))),
                       interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    cv2.setRNGSeed(seed)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 25, 0.5)
    _, _, centers = cv2.kmeans(lab, k, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
    rgb_centers = cv2.cvtColor(centers.reshape(-1, 1, 3), cv2.COLOR_LAB2RGB).reshape(-1, 3)
    return np.clip(rgb_centers, 0, 1).astype(np.float32)


def _direction_field(gray: np.ndarray, scale: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Stroke directions that follow contours, falling back to loose hatching.

    Uses the smoothed structure tensor: strokes run along edges (perpendicular
    to the gradient). In flat areas, where the tensor carries no direction,
    a slowly varying diagonal hatching angle takes over.
    """
    h, w = gray.shape
    g = cv2.GaussianBlur(gray, (0, 0), 1.5 * scale + 0.5)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    sigma = 7.0 * scale + 2.0
    j11 = cv2.GaussianBlur(gx * gx, (0, 0), sigma)
    j22 = cv2.GaussianBlur(gy * gy, (0, 0), sigma)
    j12 = cv2.GaussianBlur(gx * gy, (0, 0), sigma)

    # Doubled-angle representation avoids the 180-degree ambiguity when averaging.
    grad2 = np.arctan2(2 * j12, j11 - j22)          # 2 * gradient angle
    tangent2 = grad2 + np.pi                         # 2 * (gradient angle + 90 deg)
    trace = j11 + j22 + 1e-9
    coherence = np.sqrt((j11 - j22) ** 2 + 4 * j12 ** 2) / trace
    strength = trace / (np.percentile(trace, 90) + 1e-9)
    weight = np.clip(coherence * np.clip((strength - 0.12) * 2.0, 0, 1) * 1.4, 0, 1)

    rng = np.random.default_rng(seed)
    base = np.deg2rad(rng.uniform(35, 60))
    noise = cv2.resize(rng.standard_normal((6, 6)).astype(np.float32), (w, h),
                       interpolation=cv2.INTER_CUBIC)
    hatch2 = 2 * (base + np.deg2rad(18) * noise)

    vx = weight * np.cos(tangent2) + (1 - weight) * np.cos(hatch2)
    vy = weight * np.sin(tangent2) + (1 - weight) * np.sin(hatch2)
    vx = cv2.GaussianBlur(vx.astype(np.float32), (0, 0), 3 * scale + 1)
    vy = cv2.GaussianBlur(vy.astype(np.float32), (0, 0), 3 * scale + 1)
    angle = 0.5 * np.arctan2(vy, vx)
    return np.cos(angle).astype(np.float32), np.sin(angle).astype(np.float32)


def _detect_faces(rgb: np.ndarray) -> list:
    """Best-effort frontal face detection; returns [] if no cascade is bundled."""
    try:
        path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
    except AttributeError:
        return []
    if not os.path.isfile(path):
        return []
    detector = cv2.CascadeClassifier(path)
    if detector.empty():
        return []
    gray = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    min_side = max(24, min(gray.shape) // 12)
    faces = detector.detectMultiScale(gray, 1.1, 5, minSize=(min_side, min_side))
    return [tuple(int(v) for v in f) for f in faces]


def analyze(rgb_u8: np.ndarray, valid: np.ndarray, settings: ArtSettings,
            cancel: CancelToken | None = None, progress=None) -> SourceAnalysis:
    """Run the multi-pass analysis the stroke generator relies on."""
    cancel = cancel or CancelToken()
    report = progress or (lambda *_: None)
    h, w = rgb_u8.shape[:2]
    scale = max(h, w) / 1000.0
    rgb = rgb_u8.astype(np.float32) / 255.0

    report(0.02, "Enhancing colours")
    target = _enhance(rgb, settings.color_richness)
    # Outside the paintable area the "target" is just paper.
    target = target * valid[..., None] + PAPER_RGB * (1 - valid[..., None])
    cancel.check()

    report(0.05, "Simplifying shapes")
    smooth = _abstract(target, scale)
    cancel.check()

    size_mul = 0.6 + 0.9 * settings.stroke_size
    levels = {
        "base": cv2.GaussianBlur(smooth, (0, 0), 14 * scale * size_mul + 1),
        "medium": cv2.GaussianBlur(smooth, (0, 0), 5 * scale * size_mul + 0.5),
        "layer": cv2.GaussianBlur(smooth, (0, 0), 2.5 * scale * size_mul + 0.5),
        "fine": cv2.GaussianBlur(target, (0, 0), 1.2 * scale + 0.3),
        "micro": target,
    }

    report(0.08, "Building colour palette")
    k = int(round(14 + 30 * settings.color_richness))
    palette = _palette(smooth, k, settings.seed)
    cancel.check()

    report(0.10, "Detecting edges")
    gray = cv2.cvtColor(target, cv2.COLOR_RGB2GRAY)
    smooth_gray = cv2.cvtColor(smooth, cv2.COLOR_RGB2GRAY)
    g8 = (smooth_gray * 255).astype(np.uint8)
    # Coarse edges on a downscaled copy capture the big shapes the artist sketches first.
    coarse_scale = 500.0 / max(h, w)
    small = cv2.resize(g8, (max(8, int(w * coarse_scale)), max(8, int(h * coarse_scale))),
                       interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), 1.6)
    hi = 70 - 35 * settings.edge_detail
    coarse = cv2.Canny(small, hi * 0.45, hi)
    edges_coarse = cv2.resize(coarse, (w, h), interpolation=cv2.INTER_NEAREST)
    fine_hi = 110 - 55 * settings.edge_detail
    edges_fine = cv2.Canny(cv2.GaussianBlur(g8, (0, 0), 1.0 * scale + 0.3), fine_hi * 0.4, fine_hi)
    mask8 = (valid > 0.5).astype(np.uint8)
    inner = cv2.erode(mask8, np.ones((5, 5), np.uint8))
    edges_coarse &= inner * 255
    edges_fine &= inner * 255

    gx = cv2.Sobel(smooth_gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(smooth_gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    edge_strength = np.clip(mag / (np.percentile(mag, 98) + 1e-6), 0, 1).astype(np.float32)
    cancel.check()

    report(0.13, "Tracing stroke directions")
    dir_cos, dir_sin = _direction_field(smooth_gray, scale, settings.seed)
    cancel.check()

    report(0.15, "Finding important features")
    faces = _detect_faces(rgb)
    density = cv2.GaussianBlur(edges_fine.astype(np.float32) / 255.0, (0, 0), 6 * scale + 1)
    importance = density / (np.percentile(density, 97) + 1e-6)
    # Mild centre bias: subjects are usually near the middle of a photo.
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    centre = np.exp(-(((xx - w / 2) / (0.45 * w)) ** 2 + ((yy - h * 0.45) / (0.45 * h)) ** 2))
    importance = 0.75 * importance + 0.25 * centre
    for (fx, fy, fw, fh) in faces:
        cx, cy = fx + fw / 2, fy + fh / 2
        blob = np.exp(-(((xx - cx) / (0.6 * fw)) ** 2 + ((yy - cy) / (0.75 * fh)) ** 2))
        importance = np.maximum(importance, blob * 1.2)
    importance = np.clip(importance, 0, 1).astype(np.float32) * valid

    return SourceAnalysis(
        rgb=rgb, target=target.astype(np.float32), levels=levels, lab_palette=palette,
        gray=gray.astype(np.float32), edges_coarse=edges_coarse, edges_fine=edges_fine,
        edge_strength=edge_strength, dir_cos=dir_cos, dir_sin=dir_sin,
        importance=importance, valid=valid, faces=faces, scale=scale,
    )
