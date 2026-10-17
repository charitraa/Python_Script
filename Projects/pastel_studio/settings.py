"""User-facing settings, defaults and shared constants for Pastel Studio.

All artistic controls are normalised to the range 0..1 (except where noted)
so that the GUI sliders, the generator and the renderer agree on meaning.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

APP_NAME = "Pastel Studio"
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

# Working resolution (long side, in pixels) used for processing and rendering.
RESOLUTIONS = {
    "Draft (800 px)": 800,
    "Standard (1200 px)": 1200,
    "High (1600 px)": 1600,
}
DEFAULT_RESOLUTION = "Standard (1200 px)"

# Canvas aspect ratios offered for cropping / fitting. None = keep original.
ASPECTS = {
    "Original": None,
    "1:1 Square": 1.0,
    "4:5 Portrait": 4 / 5,
    "3:4 Portrait": 3 / 4,
    "2:3 Portrait": 2 / 3,
    "4:3 Landscape": 4 / 3,
    "3:2 Landscape": 3 / 2,
    "16:9 Landscape": 16 / 9,
}
FRAMING_MODES = ("Crop to fill", "Fit with paper margin")

ANIMATION_DURATIONS = (15, 30, 60, 120)

# Video export presets.
VIDEO_FORMATS = {
    "Match artwork": None,
    "Landscape 16:9": (16, 9),
    "Square 1:1": (1, 1),
    "Portrait 9:16": (9, 16),
}
VIDEO_RESOLUTIONS = {"720p": 720, "1080p": 1080, "1440p": 1440}
VIDEO_FPS = (24, 30, 60)

# Drawing stages, in order: (key, label shown on screen, relative time weight).
STAGES = (
    ("paper", "Preparing Paper", 0.05),
    ("sketch", "Sketching", 0.15),
    ("base", "Blocking In Colour", 0.15),
    ("strokes", "Pastel Strokes", 0.20),
    ("layering", "Layering Colour", 0.14),
    ("blending", "Blending", 0.08),
    ("details", "Finishing Details", 0.17),
    ("final", "Finished", 0.06),
)

# Visual theme shared by the main window and the full-screen player.
THEME = {
    "bg": "#f4ece0",
    "panel": "#fbf6ee",
    "panel_edge": "#e3d5c1",
    "text": "#3b2a20",
    "muted": "#8a7462",
    "accent": "#c4573a",
    "accent_dark": "#9e3f27",
    "accent_soft": "#e9b9a3",
    "stage_bg": "#16120f",
    "stage_text": "#efe4d4",
}


@dataclass
class ArtSettings:
    """Controls that affect how the oil pastel artwork is generated."""

    texture: float = 0.65        # pastel texture intensity (waxy streaks, ragged edges)
    stroke_size: float = 0.5     # 0 = fine strokes, 1 = chunky strokes
    color_richness: float = 0.55 # saturation / contrast boost and palette size
    edge_detail: float = 0.55    # amount of sketch lines and outline accents
    paper_grain: float = 0.5     # paper tooth strength (how much paper shows through)
    blending: float = 0.35       # number and strength of smudge passes
    detail_level: float = 0.6    # density of fine strokes and error tolerance
    resolution: str = DEFAULT_RESOLUTION
    aspect: str = "Original"
    framing: str = FRAMING_MODES[0]
    seed: int = 7

    @property
    def long_side(self) -> int:
        return RESOLUTIONS.get(self.resolution, RESOLUTIONS[DEFAULT_RESOLUTION])

    def copy(self, **changes) -> "ArtSettings":
        data = asdict(self)
        data.update(changes)
        return ArtSettings(**data)


@dataclass
class ExportSettings:
    """Controls for the MP4 export of the drawing process."""

    duration: int = 30
    fps: int = 30
    resolution: str = "1080p"
    video_format: str = "Match artwork"
    show_captions: bool = True
    show_cursor: bool = True
    hold_final_seconds: float = 2.0


@dataclass
class PlaybackSettings:
    duration: int = 30


@dataclass
class AppState:
    art: ArtSettings = field(default_factory=ArtSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
    playback: PlaybackSettings = field(default_factory=PlaybackSettings)
