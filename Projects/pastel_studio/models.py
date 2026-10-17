"""Plain data structures shared by the generator, renderer and animation engine."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

import numpy as np

# Stroke kinds understood by the renderer.
PASTEL = "pastel"   # a waxy pigment stroke
SKETCH = "sketch"   # a thin, grainy construction line
SMUDGE = "smudge"   # a finger/blender pass that moves existing pigment


class Cancelled(Exception):
    """Raised inside long-running work when the user cancels it."""


@dataclass
class Stroke:
    """One drawing operation, fully resolved so replaying it is deterministic."""

    points: np.ndarray          # (N, 2) float32 path in canvas pixels (x, y)
    color: tuple                # RGB floats in 0..1
    width: float                # nominal width in pixels
    opacity: float              # pigment pressure, 0..1
    layer: int                  # 1..6, see README "Layered rendering"
    kind: str = PASTEL
    texture: float = 1.0        # per-stroke multiplier on grain/streak texture
    seed: int = 0               # drives per-stroke texture offsets

    def length(self) -> float:
        if len(self.points) < 2:
            return 0.0
        return float(np.linalg.norm(np.diff(self.points, axis=0), axis=1).sum())

    def point_at(self, frac: float) -> tuple[float, float, float]:
        """Return (x, y, angle) at a fraction of the path length."""
        pts = self.points
        if len(pts) < 2:
            return float(pts[0, 0]), float(pts[0, 1]), 0.0
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        cum = np.concatenate([[0.0], np.cumsum(seg)])
        target = max(0.0, min(1.0, frac)) * cum[-1]
        i = int(np.clip(np.searchsorted(cum, target) - 1, 0, len(seg) - 1))
        t = 0.0 if seg[i] == 0 else (target - cum[i]) / seg[i]
        p = pts[i] + (pts[i + 1] - pts[i]) * t
        d = pts[i + 1] - pts[i]
        return float(p[0]), float(p[1]), float(np.arctan2(d[1], d[0]))


@dataclass
class Stage:
    key: str
    label: str
    weight: float
    start: int      # index of the first stroke in DrawingPlan.strokes
    end: int        # one past the last stroke


@dataclass
class DrawingPlan:
    """Everything the animation needs: paper, ordered strokes and the result."""

    paper: np.ndarray            # float32 HxWx3, the blank sheet
    strokes: list[Stroke]
    stages: list[Stage]
    final: np.ndarray            # float32 HxWx3, paper + every stroke rendered in order
    renderer: object             # pastel_renderer.PastelRenderer (shared textures)
    source: np.ndarray = field(default=None)  # uint8 RGB, the framed input photo

    @property
    def size(self) -> tuple[int, int]:
        h, w = self.paper.shape[:2]
        return w, h

    def final_uint8(self) -> np.ndarray:
        return to_uint8(self.final)


def to_uint8(img: np.ndarray) -> np.ndarray:
    return (np.clip(img, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


class CancelToken:
    """A thread-safe cancellation flag passed into long-running work."""

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def check(self) -> None:
        if self._event.is_set():
            raise Cancelled()
