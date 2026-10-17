"""One call from a loaded photo to a finished DrawingPlan (used by GUI and tests)."""

from __future__ import annotations

from PIL import Image

from image_processor import analyze, frame_image
from models import CancelToken, DrawingPlan
from settings import ArtSettings
from stroke_generator import build_plan


def create_artwork(image: Image.Image, settings: ArtSettings,
                   cancel: CancelToken | None = None, progress=None) -> DrawingPlan:
    """Frame, analyse and plan the drawing. `progress(fraction, message)`."""
    cancel = cancel or CancelToken()
    report = progress or (lambda *_: None)
    framed, valid = frame_image(image, settings)
    analysis = analyze(framed, valid, settings, cancel, report)
    # Analysis covers 0..15 %, stroke planning the rest.
    plan = build_plan(analysis, settings, cancel,
                      lambda f, msg: report(0.15 + 0.85 * f, msg))
    plan.source = framed
    return plan
