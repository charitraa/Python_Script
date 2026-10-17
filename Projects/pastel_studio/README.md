# Pastel Studio

A desktop app that turns a photo (uploaded or taken with your webcam) into a
handmade-looking **oil pastel drawing on textured paper**, then plays the whole
drawing process full screen, from blank paper to finished artwork, and exports
it as PNG/JPEG and MP4.

It is a simulation. Paper tooth, waxy streaks and smudging are modelled
procedurally, so the result looks like oil pastel without being a real
physical medium.

## Install

Needs Python 3.11+ with Tkinter.

```bash
cd Projects/pastel_studio
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Tkinter, if it is missing:

| OS | Command |
| --- | --- |
| Arch / CachyOS | `sudo pacman -S tk` |
| Debian / Ubuntu | `sudo apt install python3-tk` |
| Fedora | `sudo dnf install python3-tkinter` |
| Windows / macOS | The python.org installer already includes Tk |

For video export, install **FFmpeg** (`sudo pacman -S ffmpeg`,
`sudo apt install ffmpeg`, `brew install ffmpeg`, or `winget install ffmpeg`).
Without FFmpeg the app falls back to OpenCV's MPEG-4 writer, which produces
larger files that some players won't open. On an NVIDIA GPU the
**NVENC** hardware encoder is detected and used automatically. Set
`PASTEL_NO_GPU=1` to force CPU encoding.

No GPU is required.

## Run

```bash
python main.py                   # open the app
python main.py photo.jpg         # open with a photo loaded

# Without the GUI (batch / servers):
python main.py photo.jpg --output art.png --video drawing.mp4 \
    --aspect "4:5 Portrait" --duration 30 --video-format "Portrait 9:16"
```

## Using it

1. Click **Import Image** (JPG, PNG, WebP) or **Take Photo** to use your webcam.
   The camera dialog has a mirror toggle, a 3-second timer and Retake.
2. Choose the canvas **aspect ratio**, **framing** (crop to fill, or fit with a
   paper margin) and **quality**, then adjust the artistic sliders.
3. Click **Generate Oil Pastel**. Generation runs in the background and can be
   cancelled. Use *Auto-regenerate* with *Draft* quality to experiment quickly,
   and *New variation* for a different stroke layout.
4. Click **Start Full-Screen Drawing**. Keys: `Space` pause/resume, `R` restart,
   `S`/`Enter` skip to final, `H` hide controls, `Esc` exit. Moving the mouse
   shows the controls.
5. Use **Export Artwork** (PNG/JPEG) and **Export Animation Video** (MP4: 15–120 s,
   24/30/60 fps, 720p–1440p, matching/16:9/1:1/9:16, optional captions and
   pastel stick).

The original photo file is never modified.

## How it works

```
photo ─► image_processor ─► stroke_generator ─► DrawingPlan ─► animation_engine ─► screen / MP4
          (analyse)           (plan + render)    (strokes,       (replay strokes
                                                  stages, final)  in time order)
```

| Module | Purpose |
| --- | --- |
| `main.py` | Entry point, dependency checks, headless CLI |
| `gui.py` | Main window, settings, previews, background tasks, export dialogs |
| `camera.py` | Webcam capture dialog (threaded live preview) |
| `fullscreen.py` | Cinematic full-screen player and its controls |
| `settings.py` | Settings dataclasses, presets, stage list, theme |
| `models.py` | `Stroke`, `Stage`, `DrawingPlan`, cancellation token |
| `image_processor.py` | Loading/validation, crop/fit, colour enhancement, edge-preserving abstraction, k-means palette, edge maps, structure-tensor stroke directions, importance map |
| `pastel_renderer.py` | Procedural paper (tooth, fibres, emboss), anisotropic streak textures, pastel/sketch/smudge stroke rasteriser |
| `stroke_generator.py` | Builds the ordered stroke list, layer by layer |
| `pipeline.py` | One call from image to `DrawingPlan` |
| `animation_engine.py` | Time-to-stroke mapping, incremental replay, frame composition, pastel-stick cursor, playback thread |
| `video_exporter.py` | PNG/JPEG export and MP4 export via FFmpeg (NVENC → x264 → MPEG-4) or OpenCV |

**Drawing layers**

1. Paper texture
2. Sketch: construction lines traced from the main contours
3. Base colour masses: wide strokes grouped by palette colour
4. Medium pastel strokes that follow the form
5. Layering (smaller strokes, cool shadows, warm highlights) followed by blending (smudges that avoid edges and facial features)
6. Fine and micro detail strokes on important features, dark outline accents, and highlight dabs

Strokes are placed where the canvas still differs most from an increasingly
sharp target (painterly rendering). Each stroke is a curved path through the
direction field and stops when the underlying colour changes. Every stroke
carries its own seed, so replaying the plan on blank paper reproduces the final
artwork **pixel for pixel**. The animation, the export and the preview all show
the same drawing.

**Performance.** Strokes are precomputed once. Playback only renders new
strokes, and only inside each stroke's bounding patch, on a worker thread. The Tk
thread just pastes finished frames, which keeps it at about 30 fps. Seeking
backwards replays from paper, and *Skip* copies the finished canvas
instantly. Stroke rendering stays on the CPU because it is thousands of tiny
patch operations, where GPU transfer overhead would cost more than it saves.
The GPU is used for video encoding.

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests cover portrait, landscape, fit-with-margin, tiny and extreme aspect
ratios, JPG/PNG/WebP/RGBA/grayscale loading, invalid files, cancellation,
replay matching the final image exactly, and video export and its cancellation.
