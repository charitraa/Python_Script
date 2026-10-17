"""Turn an analysed photo into an ordered list of drawing operations.

The plan is built layer by layer, the way a pastel artist works:

    Layer 2  sketch      thin construction lines along the main contours
    Layer 3  base        wide strokes blocking in the large colour masses
    Layer 4  strokes     medium strokes following the form
    Layer 5  layering    smaller strokes plus cool shadows and warm highlights
             blending    smudge passes over soft areas (edges are spared)
    Layer 6  details     fine and micro strokes on important features,
                         dark outline accents and specular highlight dabs

Placement of the colour layers follows the "painterly rendering" idea of
comparing the canvas painted so far with a progressively sharper target and
only adding strokes where the difference is large. Each stroke is a curved
path traced through the stroke-direction field until the colour under it
changes too much. The canvas is rendered as each layer is planned so the
next layer can measure what is still missing; the same strokes replayed on a
fresh sheet reproduce the final artwork exactly.
"""

from __future__ import annotations

import math

import cv2
import numpy as np

from image_processor import SourceAnalysis
from models import PASTEL, SKETCH, SMUDGE, CancelToken, DrawingPlan, Stage, Stroke
from pastel_renderer import PastelRenderer
from settings import STAGES, ArtSettings

SKETCH_INK = np.array([0.40, 0.29, 0.23], np.float32)   # warm umber
COOL_SHADOW = np.array([0.24, 0.22, 0.46], np.float32)  # blue-violet
WARM_LIGHT = np.array([1.0, 0.975, 0.91], np.float32)


# --------------------------------------------------------------------------- ordering
def serpentine_order(xy: np.ndarray, band: float) -> np.ndarray:
    """Row-by-row, alternating direction: how hatching moves across an area."""
    if len(xy) == 0:
        return np.zeros(0, int)
    rows = np.floor(xy[:, 1] / band).astype(int)
    x = np.where(rows % 2 == 0, xy[:, 0], -xy[:, 0])
    return np.lexsort((x, rows))


def tile_snake_order(xy: np.ndarray, tile: float, band: float, width: int) -> np.ndarray:
    """Work area by area (tiles in a snake), hatching serpentine inside each tile."""
    if len(xy) == 0:
        return np.zeros(0, int)
    ncols = max(1, int(math.ceil(width / tile)))
    tr = np.floor(xy[:, 1] / tile).astype(int)
    tc = np.floor(xy[:, 0] / tile).astype(int)
    tc = np.where(tr % 2 == 0, tc, ncols - 1 - tc)
    rows = np.floor((xy[:, 1] % tile) / band).astype(int)
    x = np.where(rows % 2 == 0, xy[:, 0], -xy[:, 0])
    return np.lexsort((x, rows, tc, tr))


def _start_xy(strokes: list[Stroke]) -> np.ndarray:
    if not strokes:
        return np.zeros((0, 2), np.float32)
    return np.array([s.points[len(s.points) // 2] for s in strokes], np.float32)


# --------------------------------------------------------------------------- generator
class StrokeGenerator:
    def __init__(self, analysis: SourceAnalysis, settings: ArtSettings,
                 cancel: CancelToken | None = None, progress=None) -> None:
        self.a = analysis
        self.s = settings
        self.cancel = cancel or CancelToken()
        self.report = progress or (lambda *_: None)
        self.rng = np.random.default_rng(settings.seed)
        self.w, self.h = analysis.size
        self.scale = analysis.scale
        self.size_mul = 0.6 + 0.9 * settings.stroke_size
        self._seed = 0
        self.renderer = PastelRenderer(self.w, self.h, settings.texture,
                                       settings.paper_grain, settings.seed)
        self.canvas = self.renderer.new_canvas()

    # ---------------------------------------------------------------- utilities
    def _next_seed(self) -> int:
        self._seed += 1
        return self._seed

    def _jitter_color(self, c: np.ndarray, amount: float = 1.0) -> tuple:
        v = 1.0 + self.rng.normal(0, 0.035 * amount)
        c = c * v + self.rng.normal(0, 0.01 * amount, 3)
        return tuple(float(x) for x in np.clip(c, 0, 1))

    def _snap(self, colors: np.ndarray, amount: float) -> np.ndarray:
        """Pull colours towards the palette, like reaching for a pastel stick."""
        if amount <= 0 or len(colors) == 0:
            return colors
        pal = self.a.lab_palette
        d = ((colors[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
        nearest = pal[d.argmin(1)]
        return colors * (1 - amount) + nearest * amount

    def _grid(self, spacing: float, accept: np.ndarray | None = None,
              jitter: float = 0.45) -> np.ndarray:
        """Jittered grid positions inside the paintable area.

        `accept` is an optional HxW float map of acceptance probabilities.
        """
        ys = np.arange(spacing / 2, self.h, spacing)
        xs = np.arange(spacing / 2, self.w, spacing)
        gx, gy = np.meshgrid(xs, ys)
        pts = np.stack([gx.ravel(), gy.ravel()], 1)
        pts += self.rng.uniform(-jitter, jitter, pts.shape) * spacing
        pts[:, 0] = np.clip(pts[:, 0], 0, self.w - 1)
        pts[:, 1] = np.clip(pts[:, 1], 0, self.h - 1)
        ix, iy = pts[:, 0].astype(int), pts[:, 1].astype(int)
        keep = self.a.valid[iy, ix] > 0.5
        if accept is not None:
            keep &= self.rng.random(len(pts)) < accept[iy, ix]
        return pts[keep].astype(np.float32)

    def _error_accept(self, level: np.ndarray, spacing: float, tau: float,
                      base_prob: float, weight: np.ndarray | None = None) -> np.ndarray:
        """Acceptance map: high where the canvas still differs from the target."""
        diff = np.sqrt(((self.canvas - level) ** 2).sum(-1))
        k = max(3, int(spacing) | 1)
        err = cv2.blur(diff, (k, k))
        if weight is not None:
            err = err * weight
        return np.where(err > tau, 1.0, base_prob).astype(np.float32)

    def _trace(self, x: float, y: float, color: np.ndarray, level: np.ndarray,
               width: float, max_len: float, tol: float, follow_color: bool = True) -> np.ndarray:
        """Trace a curved stroke through the direction field in both directions."""
        cosf, sinf, valid = self.a.dir_cos, self.a.dir_sin, self.a.valid
        w, h = self.w, self.h
        step = max(1.5, width * 0.45)
        min_len = width * 0.9
        tol2 = tol * tol
        ix, iy = int(x), int(y)
        d0x, d0y = float(cosf[iy, ix]), float(sinf[iy, ix])
        if self.rng.random() < 0.5:
            d0x, d0y = -d0x, -d0y
        fwd_share = self.rng.uniform(0.35, 0.65)
        halves = []
        for sign, share in ((1.0, fwd_share), (-1.0, 1.0 - fwd_share)):
            limit = max_len * share
            px, py = x, y
            dx, dy = d0x * sign, d0y * sign
            path = []
            travelled = 0.0
            while travelled < limit:
                nx, ny = float(cosf[int(py), int(px)]), float(sinf[int(py), int(px)])
                if nx * dx + ny * dy < 0:
                    nx, ny = -nx, -ny
                dx, dy = 0.6 * dx + 0.4 * nx, 0.6 * dy + 0.4 * ny
                n = math.hypot(dx, dy) or 1.0
                dx, dy = dx / n, dy / n
                qx, qy = px + dx * step, py + dy * step
                if not (0 <= qx < w - 1 and 0 <= qy < h - 1):
                    break
                jx, jy = int(qx), int(qy)
                if valid[jy, jx] < 0.5:
                    break
                if follow_color and travelled * 2 > min_len:
                    c = level[jy, jx]
                    if float(((c - color) ** 2).sum()) > tol2:
                        break
                path.append((qx, qy))
                px, py = qx, qy
                travelled += step
            halves.append(path)
        pts = halves[1][::-1] + [(x, y)] + halves[0]
        if len(pts) == 1:
            # Too constrained to move: make a short dab along the field direction.
            r = width * 0.4
            pts = [(x - d0x * r, y - d0y * r), (x, y), (x + d0x * r, y + d0y * r)]
        return np.asarray(pts, np.float32)

    def _color_strokes(self, pts: np.ndarray, level: np.ndarray, width: float,
                       len_range: tuple, tol: float, opacity: float, layer: int,
                       snap: float, texture: float = 1.0, colors: np.ndarray | None = None,
                       width_jitter: float = 0.2) -> list[Stroke]:
        if len(pts) == 0:
            return []
        ix, iy = pts[:, 0].astype(int), pts[:, 1].astype(int)
        sampled = level[iy, ix] if colors is None else colors
        snapped = self._snap(sampled.copy(), snap)
        strokes = []
        for i, (x, y) in enumerate(pts):
            if (i & 511) == 0:
                self.cancel.check()
            wd = width * self.rng.uniform(1 - width_jitter, 1 + width_jitter)
            ln = wd * self.rng.uniform(*len_range)
            path = self._trace(float(x), float(y), sampled[i], level, wd, ln, tol)
            strokes.append(Stroke(
                points=path, color=self._jitter_color(snapped[i]), width=wd,
                opacity=float(np.clip(opacity + self.rng.normal(0, 0.05), 0.1, 1.0)),
                layer=layer, kind=PASTEL,
                texture=float(texture * self.rng.uniform(0.8, 1.15)), seed=self._next_seed()))
        return strokes

    def _contour_chunks(self, edges: np.ndarray, chunk_len: float, max_chunks: int,
                        min_contour: float) -> list[np.ndarray]:
        """Split edge contours into smooth, de-duplicated line segments.

        Contours of 1-px edges are traced "there and back"; an occupancy map
        drops the second pass so each line is drawn once.
        """
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours = [c[:, 0, :].astype(np.float32) for c in contours if len(c) >= min_contour]
        contours.sort(key=len, reverse=True)
        occ = np.zeros((self.h, self.w), np.uint8)
        stride = max(2, int(round(2.5 * self.scale)))
        chunks = []
        n_per = max(6, int(chunk_len))
        for c in contours:
            if len(chunks) >= max_chunks:
                break
            k = 5
            if len(c) > k:
                kern = np.ones(k, np.float32) / k
                c = np.stack([np.convolve(np.pad(c[:, j], k // 2, mode="edge"), kern, "valid")
                              for j in range(2)], 1)
            for s in range(0, len(c), n_per):
                seg = c[s:s + n_per + 1]
                if len(seg) < max(4, n_per // 4):
                    continue
                ix = np.clip(seg[:, 0].astype(int), 0, self.w - 1)
                iy = np.clip(seg[:, 1].astype(int), 0, self.h - 1)
                if occ[iy, ix].mean() > 0.45:
                    continue
                cv2.polylines(occ, [seg.astype(np.int32)], False, 1, max(3, int(4 * self.scale)))
                chunks.append(seg[::stride].copy() if len(seg) > 2 * stride else seg.copy())
                if len(chunks) >= max_chunks:
                    break
        return chunks

    # ---------------------------------------------------------------- layers
    def sketch_layer(self) -> list[Stroke]:
        a, s = self.a, self.s
        chunks = self._contour_chunks(
            a.edges_coarse, chunk_len=170 * self.scale,
            max_chunks=int(180 + 520 * s.edge_detail), min_contour=20 * self.scale)
        dark = cv2.erode(a.levels["medium"], np.ones((5, 5), np.uint8))
        width = max(1.6, 2.4 * self.scale * (0.85 + 0.3 * s.stroke_size))
        strokes = []
        for seg in chunks:
            mid = seg[len(seg) // 2].astype(int)
            local = dark[min(mid[1], self.h - 1), min(mid[0], self.w - 1)] * 0.7
            col = SKETCH_INK * 0.55 + local * 0.45
            # A loose hand: small perpendicular wobble along the line.
            wobble = self.rng.normal(0, 0.6 * self.scale, seg.shape).astype(np.float32)
            wobble = cv2.GaussianBlur(wobble, (1, 5), 0) if len(seg) >= 5 else wobble
            strokes.append(Stroke(
                points=seg + wobble, color=self._jitter_color(col, 0.5),
                width=width * self.rng.uniform(0.8, 1.2),
                opacity=float(self.rng.uniform(0.6, 0.78)), layer=2, kind=SKETCH,
                texture=1.0, seed=self._next_seed()))
        return strokes

    def base_layer(self) -> list[Stroke]:
        level = self.a.levels["base"]
        width = 30 * self.scale * self.size_mul
        pts = self._grid(width * 0.72)
        strokes = self._color_strokes(pts, level, width, (2.2, 4.2), tol=0.2,
                                      opacity=0.84, layer=3, snap=0.7, texture=1.1)
        if not strokes:
            return strokes
        # Order by colour region: the largest colour masses get blocked in first.
        cols = np.array([s.color for s in strokes], np.float32)
        pal = self.a.lab_palette
        idx = ((cols[:, None, :] - pal[None]) ** 2).sum(-1).argmin(1)
        counts = np.bincount(idx, minlength=len(pal))
        group_rank = np.argsort(np.argsort(-counts))[idx]
        xy = _start_xy(strokes)
        band = width * 1.4
        rows = np.floor(xy[:, 1] / band).astype(int)
        x = np.where(rows % 2 == 0, xy[:, 0], -xy[:, 0])
        order = np.lexsort((x, rows, group_rank))
        return [strokes[i] for i in order]

    def medium_layer(self) -> list[Stroke]:
        level = self.a.levels["medium"]
        width = 14 * self.scale * self.size_mul
        spacing = width * 0.8
        tau = 0.04 + 0.05 * (1 - self.s.detail_level)
        accept = self._error_accept(level, spacing, tau, base_prob=0.4)
        pts = self._grid(spacing, accept)
        strokes = self._color_strokes(pts, level, width, (3.0, 6.0), tol=0.13,
                                      opacity=0.85, layer=4, snap=0.45)
        order = tile_snake_order(_start_xy(strokes), max(self.w, self.h) / 4, width * 1.6, self.w)
        return [strokes[i] for i in order]

    def layering_layer(self) -> list[Stroke]:
        a, s = self.a, self.s
        level = a.levels["layer"]
        width = 8.5 * self.scale * self.size_mul
        spacing = width * 0.9
        tau = 0.05 + 0.05 * (1 - s.detail_level)
        accept = self._error_accept(level, spacing, tau, base_prob=0.12)
        pts = self._grid(spacing, accept)
        strokes = self._color_strokes(pts, level, width, (3.0, 6.0), tol=0.11,
                                      opacity=0.85, layer=5, snap=0.25)

        # Cool shadows and warm highlights: the colour accents pastel artists add.
        gray = a.gray
        inside = gray[a.valid > 0.5]
        lo, hi = np.percentile(inside, [28, 84]) if inside.size else (0.3, 0.8)
        acc_w = width * 1.25
        shadow_p = np.clip((lo - gray) / 0.08, 0, 1) * (0.25 + 0.4 * s.color_richness)
        light_p = np.clip((gray - hi) / 0.06, 0, 1) * (0.3 + 0.35 * s.color_richness)
        sp = self._grid(acc_w * 1.1, shadow_p)
        if len(sp):
            base = level[sp[:, 1].astype(int), sp[:, 0].astype(int)]
            cols = base * 0.82 * 0.8 + COOL_SHADOW * 0.2
            strokes += self._color_strokes(sp, level, acc_w, (2.5, 5.0), tol=0.16,
                                           opacity=0.38, layer=5, snap=0.0, colors=cols)
        hp = self._grid(acc_w * 1.1, light_p)
        if len(hp):
            base = level[hp[:, 1].astype(int), hp[:, 0].astype(int)]
            cols = base * 0.62 + WARM_LIGHT * 0.38
            strokes += self._color_strokes(hp, level, acc_w, (2.5, 5.0), tol=0.16,
                                           opacity=0.55, layer=5, snap=0.0, colors=cols)
        order = tile_snake_order(_start_xy(strokes), max(self.w, self.h) / 5, width * 1.6, self.w)
        return [strokes[i] for i in order]

    def blending_layer(self) -> list[Stroke]:
        a, s = self.a, self.s
        if s.blending <= 0.02:
            return []
        width = 16 * self.scale * self.size_mul
        soft = np.clip(1.0 - a.edge_strength * 2.5, 0, 1) * np.clip(1.0 - 1.2 * a.importance, 0, 1)
        prob = soft * (0.25 + 0.75 * s.blending)
        pts = self._grid(width * 0.9, prob)
        strokes = []
        for x, y in pts:
            wd = width * self.rng.uniform(0.8, 1.25)
            path = self._trace(float(x), float(y), None, a.levels["medium"], wd,
                               wd * self.rng.uniform(1.8, 3.2), tol=1.0, follow_color=False)
            strokes.append(Stroke(points=path, color=(0.0, 0.0, 0.0), width=wd,
                                  opacity=float(0.3 + 0.45 * s.blending), layer=5,
                                  kind=SMUDGE, seed=self._next_seed()))
        order = serpentine_order(_start_xy(strokes), width * 2.2)
        return [strokes[i] for i in order]

    def detail_layer(self) -> list[Stroke]:
        a, s = self.a, self.s
        out: list[Stroke] = []

        # Fine strokes wherever the canvas still misses the sharp target.
        level = a.levels["fine"]
        width = 4.8 * self.scale * (0.75 + 0.5 * s.stroke_size)
        spacing = width * 1.05
        tau = 0.055 + 0.06 * (1 - s.detail_level)
        accept = self._error_accept(level, spacing, tau, base_prob=0.0,
                                    weight=0.55 + 0.9 * a.importance)
        pts = self._grid(spacing, accept)
        cap = int(4000 + 9000 * s.detail_level)
        if len(pts) > cap:
            ix, iy = pts[:, 0].astype(int), pts[:, 1].astype(int)
            pri = a.importance[iy, ix] + self.rng.random(len(pts)) * 0.5
            pts = pts[np.argsort(-pri)[:cap]]
        fine = self._color_strokes(pts, level, width, (2.5, 5.0), tol=0.1,
                                   opacity=0.9, layer=6, snap=0.0, texture=0.85)
        order = tile_snake_order(_start_xy(fine), max(self.w, self.h) / 5, width * 2.0, self.w)
        out += [fine[i] for i in order]

        # Micro strokes only on the most important features (eyes, mouth, edges).
        if s.detail_level > 0.25:
            self.renderer.render_all(self.canvas, out, self.cancel)
            rendered = len(out)
            level = a.levels["micro"]
            mw = 2.6 * self.scale
            weight = np.where(a.importance > 0.5, 1.0, 0.0).astype(np.float32)
            accept = self._error_accept(level, mw * 1.2, tau * 0.9, 0.0, weight=weight)
            mp = self._grid(mw * 1.2, accept)
            micro = self._color_strokes(mp, level, mw, (2.0, 4.5), tol=0.09,
                                        opacity=0.92, layer=6, snap=0.0, texture=0.7,
                                        width_jitter=0.15)
            order = serpentine_order(_start_xy(micro), mw * 6)
            out += [micro[i] for i in order]
        else:
            rendered = 0

        # Dark outline accents along strong edges.
        if s.edge_detail > 0.05:
            chunks = self._contour_chunks(
                a.edges_fine, chunk_len=45 * self.scale,
                max_chunks=int(60 + 380 * s.edge_detail), min_contour=14 * self.scale)
            dark = cv2.erode(a.levels["fine"], np.ones((5, 5), np.uint8)) * 0.78
            lw = 1.9 * self.scale * (0.85 + 0.3 * s.stroke_size)
            for seg in chunks:
                ix = np.clip(seg[:, 0].astype(int), 0, self.w - 1)
                iy = np.clip(seg[:, 1].astype(int), 0, self.h - 1)
                if a.edge_strength[iy, ix].mean() < 0.25:
                    continue
                col = dark[iy[len(iy) // 2], ix[len(ix) // 2]]
                out.append(Stroke(points=seg, color=self._jitter_color(col, 0.4), width=lw,
                                  opacity=float(0.4 + 0.3 * s.edge_detail), layer=6,
                                  kind=PASTEL, texture=1.0, seed=self._next_seed()))

        # Specular highlight dabs: small, bright, last.
        g = cv2.GaussianBlur(a.gray, (0, 0), 1.5 * self.scale + 0.5)
        local_max = g >= cv2.dilate(g, np.ones((9, 9), np.uint8))
        thresh = np.percentile(g[a.valid > 0.5], 97) if (a.valid > 0.5).any() else 1.0
        ys, xs = np.nonzero(local_max & (g > thresh) & (a.valid > 0.5))
        if len(xs):
            sel = self.rng.permutation(len(xs))[:70]
            hp = np.stack([xs[sel], ys[sel]], 1).astype(np.float32)
            base = a.levels["fine"][ys[sel], xs[sel]]
            cols = base * 0.5 + WARM_LIGHT * 0.5
            out += self._color_strokes(hp, a.levels["fine"], width * 0.9, (1.0, 2.2), tol=0.2,
                                       opacity=0.85, layer=6, snap=0.0, colors=cols,
                                       texture=0.6)
        self.renderer.render_all(self.canvas, out[rendered:], self.cancel)
        return out

    # ---------------------------------------------------------------- driver
    def build(self) -> DrawingPlan:
        steps = (
            ("sketch", self.sketch_layer, 0.22),
            ("base", self.base_layer, 0.32),
            ("strokes", self.medium_layer, 0.48),
            ("layering", self.layering_layer, 0.66),
            ("blending", self.blending_layer, 0.76),
            ("details", self.detail_layer, 0.98),
        )
        labels = {k: lbl for k, lbl, _ in STAGES}
        produced: dict[str, list[Stroke]] = {}
        for key, fn, pct in steps:
            self.report(pct - 0.06, f"Planning: {labels[key]}")
            strokes = fn()
            if key != "details":  # detail_layer renders itself incrementally
                self.renderer.render_all(self.canvas, strokes, self.cancel)
            produced[key] = strokes
            self.cancel.check()

        all_strokes: list[Stroke] = []
        stages = []
        for key, label, weight in STAGES:
            start = len(all_strokes)
            all_strokes += produced.get(key, [])
            stages.append(Stage(key, label, weight, start, len(all_strokes)))
        self.report(1.0, f"Done: {len(all_strokes):,} strokes")
        return DrawingPlan(paper=self.renderer.paper, strokes=all_strokes, stages=stages,
                           final=self.canvas, renderer=self.renderer)


def build_plan(analysis: SourceAnalysis, settings: ArtSettings,
               cancel: CancelToken | None = None, progress=None) -> DrawingPlan:
    return StrokeGenerator(analysis, settings, cancel, progress).build()
