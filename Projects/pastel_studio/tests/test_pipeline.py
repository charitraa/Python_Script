"""Headless tests for the processing pipeline, animation engine and exporters.

Run from the project folder:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from animation_engine import AnimationEngine  # noqa: E402
from image_processor import ImageLoadError, load_image  # noqa: E402
from models import CancelToken, Cancelled  # noqa: E402
from pipeline import create_artwork  # noqa: E402
from settings import ArtSettings, ExportSettings  # noqa: E402
from video_exporter import export_image, export_video, video_layout  # noqa: E402

FAST = dict(resolution="Draft (800 px)", detail_level=0.3)


def synthetic_photo(w: int, h: int) -> Image.Image:
    """A simple 'portrait': gradient backdrop, a face-like ellipse with features."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    bg = np.stack([0.55 + 0.3 * xx / w, 0.6 + 0.2 * yy / h, 0.75 - 0.2 * xx / w], -1)
    img = Image.fromarray((bg * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    cx, cy, r = w / 2, h * 0.45, min(w, h) * 0.28
    d.rectangle([cx - r * 1.3, cy + r * 0.9, cx + r * 1.3, h], fill=(40, 50, 90))
    d.ellipse([cx - r * 0.8, cy - r, cx + r * 0.8, cy + r], fill=(222, 170, 140))
    d.ellipse([cx - r * 0.85, cy - r * 1.15, cx + r * 0.85, cy - r * 0.35], fill=(45, 30, 25))
    for sx in (-1, 1):
        ex = cx + sx * r * 0.33
        d.ellipse([ex - r * 0.13, cy - r * 0.12, ex + r * 0.13, cy + r * 0.05], fill=(250, 250, 245))
        d.ellipse([ex - r * 0.06, cy - r * 0.09, ex + r * 0.06, cy + r * 0.03], fill=(60, 40, 30))
    d.arc([cx - r * 0.3, cy + r * 0.3, cx + r * 0.3, cy + r * 0.6], 20, 160, fill=(170, 60, 60), width=4)
    return img


class PipelineTests(unittest.TestCase):
    def _check_plan(self, plan, aspect):
        w, h = plan.size
        if aspect is not None:
            self.assertAlmostEqual(w / h, aspect, delta=0.02)
        self.assertGreater(len(plan.strokes), 500)
        keys = [s.key for s in plan.stages]
        self.assertEqual(keys[0], "paper")
        self.assertEqual(keys[-1], "final")
        self.assertEqual(plan.stages[-1].end, len(plan.strokes))
        # Every drawing stage that should have content does.
        for st in plan.stages:
            if st.key in ("sketch", "base", "strokes", "details"):
                self.assertGreater(st.end - st.start, 0, st.key)
        final = plan.final_uint8()
        self.assertEqual(final.shape, (h, w, 3))
        # The artwork must differ from blank paper and resemble the source.
        paper = (plan.paper * 255).astype(np.uint8)
        self.assertGreater(np.abs(final.astype(int) - paper).mean(), 10)
        src = plan.source.astype(np.float32)
        corr = np.corrcoef(src.mean(-1).ravel(), final.astype(np.float32).mean(-1).ravel())[0, 1]
        self.assertGreater(corr, 0.75, "artwork no longer resembles the photo")

    def test_portrait(self):
        plan = create_artwork(synthetic_photo(600, 900), ArtSettings(**FAST))
        self._check_plan(plan, 600 / 900)

    def test_landscape_crop(self):
        plan = create_artwork(synthetic_photo(1600, 900),
                              ArtSettings(aspect="16:9 Landscape", **FAST))
        self._check_plan(plan, 16 / 9)

    def test_fit_with_margin_leaves_paper(self):
        plan = create_artwork(synthetic_photo(500, 500),
                              ArtSettings(aspect="3:4 Portrait", framing="Fit with paper margin",
                                          **FAST))
        w, h = plan.size
        corner = plan.final[: h // 30, : w // 30]
        paper = plan.paper[: h // 30, : w // 30]
        self.assertLess(np.abs(corner - paper).mean(), 0.02)

    def test_extreme_aspect_and_tiny_images(self):
        for size in ((40, 30), (1800, 200), (150, 1400)):
            plan = create_artwork(synthetic_photo(*size), ArtSettings(**FAST))
            self.assertEqual(plan.final.shape[:2][::-1], plan.size)

    def test_animation_replay_matches_final(self):
        plan = create_artwork(synthetic_photo(700, 500), ArtSettings(**FAST))
        engine = AnimationEngine(plan, 20)
        first = engine.compose(engine.advance_to(0.0))
        self.assertLess(first.mean(), 60)  # paper still fading in from the dark backdrop
        stages = []
        for t in np.linspace(0, 20, 41):
            info = engine.advance_to(float(t))
            stages.append(info.stage_key)
            engine.compose(info, (350, 250))
        self.assertEqual(stages[0], "paper")
        self.assertEqual(stages[-1], "final")
        self.assertEqual(sorted(set(stages), key=stages.index),
                         [s.key for s in plan.stages if s.end > s.start or s.key in ("paper", "final")])
        self.assertTrue(np.array_equal(engine.compose(engine.finish()), plan.final_uint8()))
        # Restart (seek backwards) then jump to the end.
        engine.advance_to(1.0)
        self.assertEqual(engine.committed, 0)
        self.assertTrue(np.array_equal(engine.compose(engine.finish()), plan.final_uint8()))

    def test_cancellation(self):
        token = CancelToken()
        calls = []

        def progress(f, msg):
            calls.append(f)
            if f > 0.3:
                token.cancel()

        with self.assertRaises(Cancelled):
            create_artwork(synthetic_photo(600, 600), ArtSettings(**FAST), token, progress)


class FileTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def path(self, name):
        return os.path.join(self.dir.name, name)

    def test_load_formats_and_transparency(self):
        img = synthetic_photo(120, 90)
        for ext in (".jpg", ".png", ".webp"):
            img.save(self.path("a" + ext))
            self.assertEqual(load_image(self.path("a" + ext)).size, (120, 90))
        rgba = img.convert("RGBA")
        rgba.putalpha(0)
        rgba.save(self.path("clear.png"))
        self.assertEqual(load_image(self.path("clear.png")).mode, "RGB")
        img.convert("L").save(self.path("gray.png"))
        self.assertEqual(load_image(self.path("gray.png")).mode, "RGB")

    def test_invalid_files(self):
        with open(self.path("bad.jpg"), "wb") as fh:
            fh.write(b"not an image")
        with self.assertRaises(ImageLoadError):
            load_image(self.path("bad.jpg"))
        with self.assertRaises(ImageLoadError):
            load_image(self.path("missing.png"))
        with self.assertRaises(ImageLoadError):
            load_image(self.path("notes.txt"))

    def test_export_image_and_video(self):
        plan = create_artwork(synthetic_photo(500, 700), ArtSettings(**FAST))
        export_image(plan, self.path("art.png"))
        export_image(plan, self.path("art.jpg"))
        with Image.open(self.path("art.png")) as saved:
            self.assertEqual(saved.size, plan.size)
        vs = ExportSettings(duration=3, fps=12, resolution="720p", video_format="Portrait 9:16",
                            hold_final_seconds=0.5)
        export_video(plan, self.path("draw.mp4"), vs)
        self.assertGreater(os.path.getsize(self.path("draw.mp4")), 10_000)

    def test_video_cancel_removes_partial_file(self):
        plan = create_artwork(synthetic_photo(300, 300), ArtSettings(**FAST))
        token = CancelToken()

        def progress(f, msg):
            if f > 0.2:
                token.cancel()

        out = self.path("cancelled.mp4")
        with self.assertRaises(Cancelled):
            export_video(plan, out, ExportSettings(duration=5, fps=24, resolution="720p"),
                         progress, token)
        self.assertFalse(os.path.exists(out))

    def test_video_layouts(self):
        for fmt, ratio in (("Landscape 16:9", 16 / 9), ("Square 1:1", 1.0), ("Portrait 9:16", 9 / 16)):
            (W, H), (x, y, w, h) = video_layout((800, 1000), ExportSettings(video_format=fmt))
            self.assertAlmostEqual(W / H, ratio, delta=0.01)
            self.assertEqual((W % 2, H % 2), (0, 0))
            self.assertTrue(0 <= x and x + w <= W and 0 <= y and y + h <= H)


if __name__ == "__main__":
    unittest.main()
