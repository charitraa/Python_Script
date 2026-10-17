"""Timeline playback of a DrawingPlan.

`AnimationEngine` is a deterministic replay machine: given a time `t` it
commits every stroke that should be finished by then onto a fresh canvas
(previous strokes are never re-rendered), draws the stroke currently in
progress partially, and composes a display frame. The same engine drives the
full-screen player and the MP4 exporter, so both show the identical process.

`PlaybackThread` runs an engine on a background thread against the wall
clock and publishes the latest frame for the Tk main loop to pick up.
"""

from __future__ import annotations

import math
import queue
import threading
import time
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image, ImageDraw

from models import SMUDGE, DrawingPlan

BLENDER_COLOR = (0.93, 0.91, 0.86)  # a colourless blending stick


@dataclass
class FrameInfo:
    t: float
    progress: float          # 0..1 over the whole animation
    stage_index: int
    stage_key: str
    stage_label: str
    stage_progress: float
    stroke_index: int        # next stroke to commit (strokes before are on canvas)
    stroke_frac: float       # how much of `stroke_index` is drawn
    cursor: tuple | None     # (x, y, angle, rgb) in canvas pixels
    paper_fade: float        # 0..1, paper fading in at the very start
    sheen: float             # -1 = off, else 0..1 position of the finishing light sweep
    finished: bool


class AnimationEngine:
    def __init__(self, plan: DrawingPlan, duration: float) -> None:
        self.plan = plan
        self.renderer = plan.renderer
        self.canvas = None
        self.committed = 0
        self._last_t = -1.0
        self.set_duration(duration)
        self.reset()

    # ---------------------------------------------------------------- timeline
    def set_duration(self, duration: float) -> None:
        self.duration = max(1.0, float(duration))
        weights = []
        for st in self.plan.stages:
            empty = st.end == st.start and st.key not in ("paper", "final")
            weights.append(0.0 if empty else st.weight)
        total = sum(weights) or 1.0
        self.windows = []
        acc = 0.0
        for w in weights:
            t0 = acc / total * self.duration
            acc += w
            self.windows.append((t0, acc / total * self.duration))

    def reset(self) -> None:
        self.canvas = self.renderer.new_canvas()
        self.committed = 0
        self._last_t = -1.0

    def stroke_position(self, t: float) -> tuple[int, float, float]:
        """Map time to (stage index, stage progress, fractional stroke position)."""
        t = min(max(t, 0.0), self.duration)
        stages = self.plan.stages
        for i, (st, (t0, t1)) in enumerate(zip(stages, self.windows)):
            if t < t1 or i == len(stages) - 1:
                f = 0.0 if t1 <= t0 else min(1.0, max(0.0, (t - t0) / (t1 - t0)))
                return i, f, st.start + f * (st.end - st.start)
        return len(stages) - 1, 1.0, float(len(self.plan.strokes))

    # ---------------------------------------------------------------- playback
    def advance_to(self, t: float) -> FrameInfo:
        if t < self._last_t:
            self.reset()  # seeking backwards: replay from the blank sheet
        self._last_t = t
        si, sf, pos = self.stroke_position(t)
        strokes = self.plan.strokes
        target = min(int(pos), len(strokes))
        if target == len(strokes) and self.committed < target:
            # Jumping to the end: the finished artwork is already known.
            self.canvas = self.plan.final.copy()
            self.committed = target
        while self.committed < target:
            self.renderer.render(self.canvas, strokes[self.committed])
            self.committed += 1
        frac = pos - target
        stage = self.plan.stages[si]

        cursor = None
        if target < len(strokes) and stage.key not in ("paper", "final"):
            s = strokes[target]
            x, y, ang = s.point_at(frac)
            cursor = (x, y, ang, BLENDER_COLOR if s.kind == SMUDGE else s.color)

        paper_fade = 1.0
        if stage.key == "paper":
            paper_fade = min(1.0, sf / 0.55)
        sheen = sf if stage.key == "final" and sf < 1.0 else -1.0
        return FrameInfo(
            t=t, progress=min(1.0, t / self.duration), stage_index=si,
            stage_key=stage.key, stage_label=stage.label, stage_progress=sf,
            stroke_index=target, stroke_frac=frac, cursor=cursor,
            paper_fade=paper_fade, sheen=sheen,
            finished=t >= self.duration)

    def finish(self) -> FrameInfo:
        return self.advance_to(self.duration)

    # ---------------------------------------------------------------- frames
    def compose(self, info: FrameInfo, size: tuple[int, int] | None = None,
                background=(22, 18, 15)) -> np.ndarray:
        """Return the artwork as uint8 RGB at `size` (w, h) for this frame."""
        strokes = self.plan.strokes
        partial = None
        if info.stroke_frac > 0.02 and info.stroke_index < len(strokes):
            s = strokes[info.stroke_index]
            if s.kind != SMUDGE:
                # Draw the stroke in progress on a scratch copy of its patch.
                pad = s.width + 4
                x0 = max(0, int(s.points[:, 0].min() - pad))
                y0 = max(0, int(s.points[:, 1].min() - pad))
                x1 = min(self.canvas.shape[1], int(s.points[:, 0].max() + pad) + 1)
                y1 = min(self.canvas.shape[0], int(s.points[:, 1].max() + pad) + 1)
                if x1 > x0 and y1 > y0:
                    partial = (x0, y0, self.canvas[y0:y1, x0:x1].copy())
                    self.renderer.render(self.canvas, s, info.stroke_frac)

        frame = (np.clip(self.canvas, 0, 1) * 255.0 + 0.5).astype(np.uint8)
        if partial is not None:
            x0, y0, patch = partial
            self.canvas[y0:y0 + patch.shape[0], x0:x0 + patch.shape[1]] = patch

        if size is not None and (size[0], size[1]) != (frame.shape[1], frame.shape[0]):
            interp = cv2.INTER_AREA if size[0] < frame.shape[1] else cv2.INTER_CUBIC
            frame = cv2.resize(frame, size, interpolation=interp)

        if info.paper_fade < 1.0:
            f = info.paper_fade * info.paper_fade * (3 - 2 * info.paper_fade)
            bg = np.array(background, np.float32)
            frame = (frame.astype(np.float32) * f + bg * (1 - f)).astype(np.uint8)
        if info.sheen >= 0.0:
            frame = _apply_sheen(frame, info.sheen)
        return frame

    def scale_cursor(self, info: FrameInfo, size: tuple[int, int]):
        if info.cursor is None:
            return None
        h, w = self.canvas.shape[:2]
        x, y, a, c = info.cursor
        return x * size[0] / w, y * size[1] / h, a, c


def _apply_sheen(frame: np.ndarray, pos: float) -> np.ndarray:
    """A soft diagonal light sweep: the "fixative" finishing touch."""
    h, w = frame.shape[:2]
    u = (np.arange(w, dtype=np.float32)[None, :] / w * 0.6
         + np.arange(h, dtype=np.float32)[:, None] / h * 0.4)
    centre = -0.2 + 1.4 * pos
    strength = 0.10 * math.sin(math.pi * pos)
    band = np.exp(-((u - centre) / 0.09) ** 2) * strength
    f = frame.astype(np.float32)
    f += (255.0 - f) * band[..., None]
    return f.astype(np.uint8)


def stage_background(size, rect, color=(22, 18, 15)) -> np.ndarray:
    """Dark vignetted backdrop with a soft drop shadow under the paper `rect`."""
    W, H = size
    x, y, w, h = rect
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    glow = np.clip(1.0 - r * 1.3, 0, 1)
    bg = np.array(color, np.float32)[None, None, :] * (0.75 + 0.6 * glow[..., None])
    shadow = np.zeros((H, W), np.float32)
    off = max(4, int(min(W, H) * 0.01))
    shadow[y + off:y + h + off, x + off // 2:x + w + off // 2] = 1.0
    shadow = cv2.GaussianBlur(shadow, (0, 0), max(4, min(W, H) * 0.018))
    bg *= (1.0 - 0.75 * shadow[..., None])
    # Dither so the dark gradient does not band after H.264 compression.
    bg += np.random.default_rng(0).uniform(-1.5, 1.5, bg.shape).astype(np.float32)
    return np.clip(bg, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------- cursor
class CursorSmoother:
    """Eases the on-screen pastel stick towards the stroke position."""

    def __init__(self) -> None:
        self.pos = None
        self.tilt = -0.95

    def update(self, target, dt: float):
        if target is None:
            return None
        x, y, angle, color = target
        if self.pos is None:
            self.pos = [x, y]
        k = 1.0 - math.exp(-dt * 28.0)
        self.pos[0] += (x - self.pos[0]) * k
        self.pos[1] += (y - self.pos[1]) * k
        # The hand tilts slightly with the stroke direction.
        want = -0.95 + 0.18 * math.sin(angle)
        self.tilt += (want - self.tilt) * (1.0 - math.exp(-dt * 6.0))
        return self.pos[0], self.pos[1], self.tilt, color

    def reset(self) -> None:
        self.pos = None


def draw_pastel_stick(img: Image.Image, x: float, y: float, tilt: float, color,
                      size: float) -> None:
    """Draw an oil pastel stick whose tip touches (x, y). Used by player and exporter."""
    draw = ImageDraw.Draw(img, "RGBA")
    ux, uy = math.cos(tilt), math.sin(tilt)       # along the stick, away from the tip
    px, py = -uy, ux                              # across the stick
    half = size * 0.5
    length = size * 6.5

    def quad(a0, a1, w0, w1, dx=0.0, dy=0.0):
        return [(x + ux * a0 + px * w0 + dx, y + uy * a0 + py * w0 + dy),
                (x + ux * a1 + px * w1 + dx, y + uy * a1 + py * w1 + dy),
                (x + ux * a1 - px * w1 + dx, y + uy * a1 - py * w1 + dy),
                (x + ux * a0 - px * w0 + dx, y + uy * a0 - py * w0 + dy)]

    rgb = tuple(int(max(0, min(1, c)) * 255) for c in color)
    light = tuple(min(255, int(c * 1.15 + 18)) for c in rgb)
    dark = tuple(int(c * 0.7) for c in rgb)
    sh = size * 0.55
    draw.polygon(quad(size * 0.3, length, half, half, sh, sh * 1.3), fill=(0, 0, 0, 70))
    draw.polygon(quad(0, size * 1.1, half * 0.35, half), fill=dark + (255,))        # worn tip
    draw.polygon(quad(size * 1.1, length, half, half), fill=rgb + (255,))           # body
    draw.polygon(quad(size * 1.1, length, half * 0.25, half * 0.25, -px * half * 0.45,
                      -py * half * 0.45), fill=light + (150,))                      # sheen
    draw.polygon(quad(size * 2.6, length, half * 1.04, half * 1.04),
                 fill=(236, 226, 205, 255))                                         # paper wrapper
    draw.polygon(quad(size * 3.4, size * 3.9, half * 1.04, half * 1.04), fill=rgb + (255,))
    draw.line([(x + ux * size * 2.6 + px * half * 1.04, y + uy * size * 2.6 + py * half * 1.04),
               (x + ux * length + px * half * 1.04, y + uy * length + py * half * 1.04)],
              fill=(0, 0, 0, 60), width=max(1, int(size / 10)))


# ---------------------------------------------------------------------------- thread
class PlaybackThread(threading.Thread):
    """Runs an AnimationEngine against the wall clock on a worker thread.

    Commands are queued from the Tk thread; the most recent rendered frame is
    exposed through `latest()` as (frame_id, PIL.Image, FrameInfo).
    """

    def __init__(self, plan: DrawingPlan, duration: float, display_size: tuple[int, int],
                 fps: int = 30, background=(22, 18, 15)) -> None:
        super().__init__(daemon=True)
        self.engine = AnimationEngine(plan, duration)
        self.display_size = display_size
        self.fps = fps
        self.background = background
        self.commands: queue.Queue = queue.Queue()
        self._latest = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self.paused = False
        self.cursor = CursorSmoother()
        self.error: Exception | None = None

    # Commands (thread-safe, called from the UI thread)
    def pause(self): self.commands.put(("pause",))
    def resume(self): self.commands.put(("resume",))
    def toggle(self): self.commands.put(("toggle",))
    def restart(self): self.commands.put(("restart",))
    def skip(self): self.commands.put(("skip",))
    def set_duration(self, d): self.commands.put(("duration", d))
    def resize(self, size): self.commands.put(("resize", size))
    def stop(self): self._stop.set()

    def latest(self):
        with self._lock:
            return self._latest

    def run(self) -> None:
        try:
            self._loop()
        except Exception as exc:  # surfaced to the UI by the poller
            self.error = exc

    def _loop(self) -> None:
        clock = time.perf_counter
        t = 0.0
        last = clock()
        frame_id = 0
        dirty = True
        period = 1.0 / self.fps
        while not self._stop.is_set():
            while True:
                try:
                    cmd = self.commands.get_nowait()
                except queue.Empty:
                    break
                dirty = True
                name = cmd[0]
                if name == "pause":
                    self.paused = True
                elif name == "resume":
                    self.paused = False
                elif name == "toggle":
                    self.paused = not self.paused
                elif name == "restart":
                    t = 0.0
                    self.engine.reset()
                    self.cursor.reset()
                    self.paused = False
                elif name == "skip":
                    t = self.engine.duration
                elif name == "duration":
                    frac = t / self.engine.duration
                    self.engine.set_duration(cmd[1])
                    t = frac * self.engine.duration
                elif name == "resize":
                    self.display_size = cmd[1]

            now = clock()
            dt = now - last
            last = now
            if not self.paused and t < self.engine.duration:
                t = min(self.engine.duration, t + dt)
                dirty = True
            if dirty:
                info = self.engine.advance_to(t)
                size = self.display_size
                frame = self.engine.compose(info, size, self.background)
                img = Image.fromarray(frame)
                cur = self.cursor.update(self.engine.scale_cursor(info, size), dt)
                if cur is not None:
                    draw_pastel_stick(img, cur[0], cur[1], cur[2], cur[3],
                                      size=max(10.0, max(size) / 46.0))
                frame_id += 1
                with self._lock:
                    self._latest = (frame_id, img, info, self.paused)
                dirty = not (self.paused or info.finished)
            spent = clock() - now
            time.sleep(max(0.002, period - spent))
