"""Procedural paper and oil pastel stroke rendering.

The renderer simulates the physical behaviour that makes oil pastel look
like oil pastel, within the limits of a 2D image:

* Paper has *tooth*: a height map of tiny peaks and valleys. Pigment catches
  on the peaks first, so light pressure leaves speckled paper showing through,
  heavy pressure fills the valleys.
* A pastel stick leaves *streaks* along the direction of travel, because its
  worn tip is uneven. These come from pre-computed anisotropic noise tiles.
* Wax builds up at the stroke edges (slightly darker rims) and the edges are
  ragged rather than clean.
* Smudging drags existing pigment along a direction, softening transitions.

Every stroke is rendered into a small patch around its path only, so replaying
thousands of strokes is cheap and fully deterministic.
"""

from __future__ import annotations

import math

import cv2
import numpy as np

from models import SKETCH, SMUDGE, Stroke

STREAK_TILE = 256
STREAK_ANGLES = 16
_SUB = 4  # cv2 sub-pixel shift of 2 bits


def _normalise(a: np.ndarray, lo_pct: float = 1, hi_pct: float = 99) -> np.ndarray:
    lo, hi = np.percentile(a, [lo_pct, hi_pct])
    return np.clip((a - lo) / (hi - lo + 1e-9), 0, 1).astype(np.float32)


def _streak_bank(seed: int) -> np.ndarray:
    """Tileable anisotropic noise: long streaks along each of 16 directions."""
    rng = np.random.default_rng(seed + 101)
    n = STREAK_TILE
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.fftfreq(n)[None, :]
    bank = np.empty((STREAK_ANGLES, n, n), np.float32)
    white = np.fft.fft2(rng.standard_normal((n, n)))
    for i in range(STREAK_ANGLES):
        a = math.pi * i / STREAK_ANGLES
        along = fx * math.cos(a) + fy * math.sin(a)
        across = -fx * math.sin(a) + fy * math.cos(a)
        # Very little variation along the stroke, lots across it.
        filt = np.exp(-(along / 0.012) ** 2 - (across / 0.16) ** 2)
        field = np.real(np.fft.ifft2(white * filt))
        bank[i] = _normalise(field)
    return bank


def make_paper(w: int, h: int, grain: float, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create a warm, textured drawing sheet.

    Returns (paper RGB float32, tooth 0..1 float32, shade multiplier float32).
    """
    rng = np.random.default_rng(seed)
    s = max(w, h) / 1000.0
    white = rng.standard_normal((h, w)).astype(np.float32)
    fine = cv2.GaussianBlur(white, (0, 0), 0.8 * s + 0.4)
    medium = cv2.GaussianBlur(white, (0, 0), 1.7 * s + 0.5)
    # Pastel papers have a slightly cellular "honeycomb" surface: emphasise
    # the medium-scale bumps with a soft threshold.
    cells = np.tanh(medium / (medium.std() + 1e-9) * 1.6)
    tooth = _normalise(0.45 * fine / (fine.std() + 1e-9) + 0.55 * cells)

    mottle = cv2.resize(rng.standard_normal((9, 12)).astype(np.float32), (w, h),
                        interpolation=cv2.INTER_CUBIC)
    mottle += 0.5 * cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 25 * s)

    # Light from the top-left grazing the tooth gives the embossed look.
    relief = cv2.GaussianBlur(tooth, (0, 0), 0.6 * s + 0.3)
    emboss = cv2.Sobel(relief, cv2.CV_32F, 1, 0, ksize=3) + cv2.Sobel(relief, cv2.CV_32F, 0, 1, ksize=3)
    emboss /= (np.percentile(np.abs(emboss), 98) + 1e-9)
    shade = 1.0 - 0.07 * grain * np.clip(emboss, -1.5, 1.5)

    # Sparse paper fibres.
    fibres = np.zeros((h, w), np.uint8)
    for _ in range(int(w * h / 9000)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        a = rng.uniform(0, math.pi)
        ln = rng.uniform(4, 14) * s
        x2, y2 = x + math.cos(a) * ln, y + math.sin(a) * ln
        cv2.line(fibres, (int(x * _SUB), int(y * _SUB)), (int(x2 * _SUB), int(y2 * _SUB)),
                 255, 1, cv2.LINE_AA, 2)
    fibre_f = cv2.GaussianBlur(fibres.astype(np.float32) / 255.0, (0, 0), 0.6)

    base = np.array([0.958, 0.936, 0.890], np.float32)
    lum = (1.0
           - 0.045 * grain * (1.0 - tooth)
           + 0.012 * mottle
           - 0.035 * fibre_f * (0.5 + grain))
    paper = base[None, None, :] * (lum * shade)[..., None]
    # A faint warm tint in the valleys.
    paper[..., 2] -= 0.012 * grain * (1.0 - tooth)
    return np.clip(paper, 0, 1).astype(np.float32), tooth, shade.astype(np.float32)


class PastelRenderer:
    """Holds the shared textures and draws individual strokes onto a canvas."""

    def __init__(self, w: int, h: int, texture: float, grain: float, seed: int) -> None:
        self.w, self.h = w, h
        self.texture = float(texture)
        self.grain = float(grain)
        self.paper, self.tooth, self.shade = make_paper(w, h, grain, seed)
        self.streaks = _streak_bank(seed)

    def new_canvas(self) -> np.ndarray:
        return self.paper.copy()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def truncate(points: np.ndarray, frac: float) -> tuple[np.ndarray, np.ndarray]:
        """Return the path prefix up to `frac` of its length and the
        normalised arc-length parameter (relative to the *full* stroke)."""
        if len(points) < 2:
            return points, np.zeros(len(points), np.float32)
        seg = np.linalg.norm(np.diff(points, axis=0), axis=1)
        cum = np.concatenate([[0.0], np.cumsum(seg)])
        total = cum[-1] if cum[-1] > 0 else 1.0
        t = (cum / total).astype(np.float32)
        if frac >= 1.0:
            return points, t
        cut = frac * total
        i = int(np.searchsorted(cum, cut, side="right"))
        if i >= len(points):
            return points, t
        i = max(i, 1)
        r = 0.0 if seg[i - 1] == 0 else (cut - cum[i - 1]) / seg[i - 1]
        last = points[i - 1] + (points[i] - points[i - 1]) * r
        pts = np.vstack([points[:i], last[None, :]]).astype(np.float32)
        ts = np.concatenate([t[:i], [np.float32(frac)]])
        return pts, ts

    def _bbox(self, pts: np.ndarray, pad: float):
        x0 = max(0, int(math.floor(pts[:, 0].min() - pad)))
        y0 = max(0, int(math.floor(pts[:, 1].min() - pad)))
        x1 = min(self.w, int(math.ceil(pts[:, 0].max() + pad)) + 1)
        y1 = min(self.h, int(math.ceil(pts[:, 1].max() + pad)) + 1)
        if x1 <= x0 or y1 <= y0:
            return None
        return x0, y0, x1, y1

    @staticmethod
    def _taper(t: np.ndarray, floor: float = 0.45) -> np.ndarray:
        """Pressure profile: quick attack, gentle lift-off at the end."""
        rise = np.clip(t / 0.12, 0, 1)
        fall = np.clip((1 - t) / 0.28, 0, 1)
        return floor + (1.0 - floor) * np.sqrt(np.minimum(rise, fall))

    def _path_mask(self, pts, ts, width, x0, y0, pw, ph, taper_floor=0.45) -> np.ndarray:
        mask = np.zeros((ph, pw), np.uint8)
        local = np.round((pts - np.array([x0, y0], np.float32)) * _SUB).astype(np.int32)
        widths = width * self._taper(ts, taper_floor)
        if len(local) == 1:
            r = max(1, int(round(widths[0] / 2)))
            cv2.circle(mask, tuple(local[0]), r * _SUB, 255, -1, cv2.LINE_AA, 2)
        for i in range(len(local) - 1):
            th = max(1, int(round((widths[i] + widths[i + 1]) / 2)))
            cv2.line(mask, tuple(local[i]), tuple(local[i + 1]), 255, th, cv2.LINE_AA, 2)
        return mask.astype(np.float32) * (1.0 / 255.0)

    def _streak_patch(self, angle: float, seed: int, x0, y0, pw, ph) -> np.ndarray:
        b = int(round((angle % math.pi) / math.pi * STREAK_ANGLES)) % STREAK_ANGLES
        tile = self.streaks[b]
        ox = (seed * 7919) % STREAK_TILE
        oy = (seed * 104729) % STREAK_TILE
        ys = (np.arange(y0 + oy, y0 + oy + ph)) % STREAK_TILE
        xs = (np.arange(x0 + ox, x0 + ox + pw)) % STREAK_TILE
        return tile[np.ix_(ys, xs)]

    # ------------------------------------------------------------------ public
    def render(self, canvas: np.ndarray, stroke: Stroke, frac: float = 1.0):
        """Draw `stroke` (or its first `frac` of length) onto `canvas` in place.

        Returns the touched bounding box (x0, y0, x1, y1) or None.
        """
        if stroke.kind == SMUDGE:
            return self._render_smudge(canvas, stroke, frac)
        pts, ts = self.truncate(stroke.points, frac)
        if len(pts) == 0:
            return None
        width = max(1.0, stroke.width)
        bbox = self._bbox(pts, width * 0.75 + 3)
        if bbox is None:
            return None
        x0, y0, x1, y1 = bbox
        pw, ph = x1 - x0, y1 - y0

        floor = 0.8 if stroke.kind == SKETCH else 0.45
        mask = self._path_mask(pts, ts, width, x0, y0, pw, ph, floor)
        if width > 4:
            mask = cv2.GaussianBlur(mask, (0, 0), 0.5 + width * 0.03)

        d = stroke.points[-1] - stroke.points[0]
        angle = math.atan2(float(d[1]), float(d[0])) if np.any(d) else 0.0
        streak = self._streak_patch(angle, stroke.seed, x0, y0, pw, ph)
        tooth = self.tooth[y0:y1, x0:x1]
        tex = self.texture * stroke.texture

        if stroke.kind == SKETCH:
            # A dry, grainy line: tooth dominates, no wax rim.
            g = 0.5 + 0.6 * (tooth - 0.5) * (0.3 + self.grain) + 0.2 * (streak - 0.5)
            alpha = mask * np.clip(stroke.opacity + (g - 0.5) * 1.3, 0, 1)
            col = np.asarray(stroke.color, np.float32)[None, None, :]
            region = canvas[y0:y1, x0:x1]
            a = alpha[..., None]
            region *= (1 - a)
            region += col * a
            return bbox

        # Ragged edges: the stroke boundary breaks up on the paper tooth.
        rough = 0.6 * tooth + 0.4 * streak
        mask = np.clip(mask * (1.25 + 0.5 * tex) - (0.25 + 0.5 * tex) * rough, 0, 1)

        # Pigment deposit: the stick only touches paper peaks higher than a
        # pressure-dependent threshold. The tooth term is shared by every
        # stroke, so the same valleys stay light through all layers, which is
        # what gives oil pastel its speckled, grainy look.
        height = (1.0 - 0.45 * tex) * tooth + 0.45 * tex * streak
        thr = (1.0 - stroke.opacity) * (0.6 + 1.4 * self.grain) + 0.1 * self.grain
        soft = 0.1 + 0.18 * (1.0 - self.grain)
        t = np.clip((height - thr + soft) / (2 * soft), 0, 1)
        alpha = mask * (t * t * (3 - 2 * t))

        # Waxy pigment: value varies with the streaks, builds up at the rim and
        # catches the light like a thin relief.
        rim = np.clip(4.0 * mask * (1.0 - mask), 0, 1)
        shade = self.shade[y0:y1, x0:x1]
        relief = -(cv2.Sobel(mask, cv2.CV_32F, 1, 0, ksize=3) + cv2.Sobel(mask, cv2.CV_32F, 0, 1, ksize=3))
        lum = ((1.0 + 0.24 * tex * (streak - 0.5) - 0.10 * tex * rim + 0.07 * tex * np.clip(relief, -1, 1))
               * (1.0 + (shade - 1.0) * 0.7))
        col = np.asarray(stroke.color, np.float32)[None, None, :] * lum[..., None]

        region = canvas[y0:y1, x0:x1]
        a = alpha[..., None]
        region *= (1 - a)
        region += np.clip(col, 0, 1) * a
        return bbox

    def _render_smudge(self, canvas: np.ndarray, stroke: Stroke, frac: float):
        pts, ts = self.truncate(stroke.points, frac)
        if len(pts) < 2:
            return None
        width = max(2.0, stroke.width)
        drag = int(max(3, width * 0.9)) | 1
        bbox = self._bbox(pts, width * 0.7 + drag)
        if bbox is None:
            return None
        x0, y0, x1, y1 = bbox
        pw, ph = x1 - x0, y1 - y0
        d = stroke.points[-1] - stroke.points[0]
        angle = math.atan2(float(d[1]), float(d[0])) if np.any(d) else 0.0

        kernel = np.zeros((drag, drag), np.float32)
        c = drag // 2
        dx, dy = math.cos(angle) * c, math.sin(angle) * c
        cv2.line(kernel, (int(round(c - dx)), int(round(c - dy))),
                 (int(round(c + dx)), int(round(c + dy))), 1.0, 1, cv2.LINE_AA)
        kernel /= kernel.sum() + 1e-9

        region = canvas[y0:y1, x0:x1]
        dragged = cv2.filter2D(region, -1, kernel, borderType=cv2.BORDER_REFLECT)
        mask = self._path_mask(pts, ts, width, x0, y0, pw, ph)
        mask = cv2.GaussianBlur(mask, (0, 0), 0.25 * width + 0.5)
        a = (mask * stroke.opacity)[..., None]
        region *= (1 - a)
        region += dragged * a
        return bbox

    def render_all(self, canvas: np.ndarray, strokes, cancel=None, progress=None,
                   start: int = 0) -> np.ndarray:
        for i, s in enumerate(strokes):
            self.render(canvas, s)
            if cancel is not None and (i & 255) == 0:
                cancel.check()
            if progress is not None and (i % 500) == 0:
                progress(i + start)
        return canvas
