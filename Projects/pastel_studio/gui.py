"""Main Pastel Studio window: import, settings, previews, generation and export.

All heavy work (analysis + stroke planning, video export) runs in a
BackgroundTask thread; results and progress reach the UI through a queue that
is drained with `after()`, so Tk is only ever touched from the main thread.
"""

from __future__ import annotations

import os
import queue
import random
import threading
import tkinter as tk
import tkinter.font as tkfont
from dataclasses import asdict
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageTk

from camera import CameraDialog
from fullscreen import DrawingScreen
from image_processor import ImageLoadError, load_image
from models import CancelToken, Cancelled, DrawingPlan
from pipeline import create_artwork
from settings import (ANIMATION_DURATIONS, APP_NAME, ASPECTS, FRAMING_MODES, RESOLUTIONS,
                      SUPPORTED_EXTENSIONS, THEME, VIDEO_FORMATS, VIDEO_FPS, VIDEO_RESOLUTIONS,
                      ArtSettings, ExportSettings)
from video_exporter import VideoExportError, describe_encoder, export_image, export_video

SLIDERS = (
    ("texture", "Pastel texture", "Waxy streaks and ragged stroke edges"),
    ("stroke_size", "Stroke size", "From fine marks to chunky strokes"),
    ("color_richness", "Colour richness", "Saturation, contrast and palette size"),
    ("edge_detail", "Edge detail", "Sketch lines and dark outline accents"),
    ("paper_grain", "Paper grain", "How much paper tooth shows through"),
    ("blending", "Blending", "Smudged, softened transitions"),
    ("detail_level", "Drawing detail", "Density of fine strokes on features"),
)


# --------------------------------------------------------------------------- tasks
class BackgroundTask:
    """Run `work(cancel, progress)` on a thread; deliver callbacks on the Tk thread."""

    def __init__(self, root: tk.Misc, work, on_done, on_error, on_progress) -> None:
        self.root = root
        self.cancel = CancelToken()
        self._q: queue.Queue = queue.Queue()
        self._callbacks = (on_done, on_error, on_progress)
        self.thread = threading.Thread(target=self._run, args=(work,), daemon=True)
        self.thread.start()
        self.root.after(40, self._drain)

    def _run(self, work) -> None:
        try:
            result = work(self.cancel, lambda f, m="": self._q.put(("progress", f, m)))
            self._q.put(("done", result))
        except BaseException as exc:  # forwarded to the UI thread
            self._q.put(("error", exc))

    def _drain(self) -> None:
        on_done, on_error, on_progress = self._callbacks
        try:
            while True:
                item = self._q.get_nowait()
                if item[0] == "progress":
                    on_progress(item[1], item[2])
                elif item[0] == "done":
                    on_done(item[1])
                    return
                else:
                    on_error(item[1])
                    return
        except queue.Empty:
            pass
        self.root.after(40, self._drain)


# --------------------------------------------------------------------------- widgets
class ScrollFrame(ttk.Frame):
    """A vertically scrollable frame for the settings sidebar."""

    def __init__(self, master, **kw) -> None:
        super().__init__(master, **kw)
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=THEME["panel"], width=300)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas, style="Panel.TFrame")
        self._win = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.inner.bind_all(seq, self._on_wheel, add="+")

    def _on_wheel(self, event) -> None:
        widget = event.widget
        while widget is not None:
            if widget is self:
                break
            widget = getattr(widget, "master", None)
        else:
            return
        if isinstance(event.widget, (ttk.Scale, ttk.Combobox)):
            return
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(delta, "units")


class PreviewPanel(ttk.Frame):
    """A titled card showing an image scaled to fit, with a placeholder."""

    def __init__(self, master, title: str, placeholder: str, fonts: dict) -> None:
        super().__init__(master, style="Card.TFrame", padding=(14, 10, 14, 14))
        head = ttk.Frame(self, style="Panel.TFrame")
        head.pack(fill="x")
        ttk.Label(head, text=title, style="CardTitle.TLabel").pack(side="left")
        self.info = ttk.Label(head, text="", style="CardMuted.TLabel")
        self.info.pack(side="right")
        self.canvas = tk.Canvas(self, bg=THEME["panel"], highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True, pady=(8, 0))
        self.placeholder = placeholder
        self.fonts = fonts
        self.image: Image.Image | None = None
        self._photo = None
        self._job = None
        self.canvas.bind("<Configure>", lambda e: self._schedule())

    def set_image(self, image: Image.Image | None, info: str = "") -> None:
        self.image = image
        self.info.configure(text=info)
        self._schedule()

    def _schedule(self) -> None:
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(30, self._redraw)

    def _redraw(self) -> None:
        self._job = None
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 10 or h < 10:
            return
        if self.image is None:
            c.create_rectangle(8, 8, w - 8, h - 8, outline=THEME["panel_edge"], dash=(6, 5), width=2)
            c.create_text(w / 2, h / 2, text=self.placeholder, fill=THEME["muted"],
                          font=self.fonts["body"], justify="center", width=max(100, w - 60))
            return
        iw, ih = self.image.size
        scale = min((w - 16) / iw, (h - 16) / ih)
        tw, th = max(1, int(iw * scale)), max(1, int(ih * scale))
        shown = self.image.resize((tw, th), Image.Resampling.LANCZOS if scale < 1
                                  else Image.Resampling.BICUBIC)
        self._photo = ImageTk.PhotoImage(shown)
        x, y = (w - tw) // 2, (h - th) // 2
        c.create_rectangle(x + 3, y + 4, x + tw + 3, y + th + 4, fill="#e2d4c0", outline="")
        c.create_image(x, y, anchor="nw", image=self._photo)


# --------------------------------------------------------------------------- app
class PastelStudioApp:
    def __init__(self, root: tk.Tk, initial_image: str | None = None) -> None:
        self.root = root
        self.settings = ArtSettings()
        self.export_settings = ExportSettings()
        self.source_path: str | None = None
        self.source_image: Image.Image | None = None
        self.source_name = "artwork"
        self.plan: DrawingPlan | None = None
        self.plan_settings: dict | None = None
        self.task: BackgroundTask | None = None
        self.task_kind: str | None = None
        self.pending_regen = False
        self.start_after_generate = False
        self._regen_job = None

        self._setup_root()
        self._build_ui()
        self._update_buttons()
        if initial_image:
            self.root.after(150, lambda: self.open_image(initial_image))

    # ------------------------------------------------------------------ setup
    def _setup_root(self) -> None:
        r = self.root
        r.title(APP_NAME)
        r.geometry("1320x840")
        r.minsize(1040, 680)
        r.configure(bg=THEME["bg"])
        r.protocol("WM_DELETE_WINDOW", self.quit)
        try:
            r.iconphoto(True, ImageTk.PhotoImage(_app_icon()))
        except tk.TclError:
            pass

        families = set(tkfont.families(r))
        serif = next((f for f in ("Georgia", "Palatino Linotype", "DejaVu Serif", "Noto Serif",
                                  "Times New Roman", "Times") if f in families), "TkDefaultFont")
        sans = next((f for f in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter", "Cantarell",
                                 "Noto Sans", "DejaVu Sans", "Helvetica", "Arial")
                     if f in families), "TkDefaultFont")
        self.fonts = {
            "title": (serif, 26, "bold"),
            "subtitle": (sans, 11),
            "section": (sans, 10, "bold"),
            "body": (sans, 10),
            "small": (sans, 9),
            "card": (serif, 14, "bold"),
            "button": (sans, 10, "bold"),
            "stage": (serif, 20, "italic"),
        }

        st = ttk.Style(r)
        st.theme_use("clam")
        T = THEME
        st.configure(".", background=T["bg"], foreground=T["text"], font=self.fonts["body"],
                     bordercolor=T["panel_edge"], lightcolor=T["panel"], darkcolor=T["panel_edge"],
                     troughcolor="#eadfcd", focuscolor=T["accent_soft"])
        st.configure("TFrame", background=T["bg"])
        st.configure("Panel.TFrame", background=T["panel"])
        st.configure("Card.TFrame", background=T["panel"], relief="solid", borderwidth=1)
        st.configure("TLabel", background=T["bg"])
        st.configure("Title.TLabel", font=self.fonts["title"], foreground=T["text"])
        st.configure("Subtitle.TLabel", font=self.fonts["subtitle"], foreground=T["muted"])
        st.configure("Panel.TLabel", background=T["panel"])
        st.configure("Section.TLabel", background=T["panel"], foreground=T["accent_dark"],
                     font=self.fonts["section"])
        st.configure("Hint.TLabel", background=T["panel"], foreground=T["muted"],
                     font=self.fonts["small"])
        st.configure("Value.TLabel", background=T["panel"], foreground=T["accent_dark"],
                     font=self.fonts["section"])
        st.configure("CardTitle.TLabel", background=T["panel"], font=self.fonts["card"])
        st.configure("CardMuted.TLabel", background=T["panel"], foreground=T["muted"],
                     font=self.fonts["small"])
        st.configure("Status.TLabel", background=T["bg"], foreground=T["muted"])
        st.configure("TButton", padding=(12, 7), background="#efe4d4", foreground=T["text"],
                     font=self.fonts["button"], borderwidth=1)
        st.map("TButton", background=[("disabled", "#efe8de"), ("pressed", "#e2d3bd"),
                                      ("active", "#f6ecdf")],
               foreground=[("disabled", "#b9a999")])
        st.configure("Accent.TButton", background=T["accent"], foreground="white",
                     bordercolor=T["accent_dark"], lightcolor=T["accent"], darkcolor=T["accent_dark"])
        st.map("Accent.TButton", background=[("disabled", "#e2c3b6"), ("pressed", T["accent_dark"]),
                                             ("active", "#d0654a")],
               foreground=[("disabled", "#fbefe9")])
        st.configure("Panel.TCheckbutton", background=T["panel"])
        st.map("Panel.TCheckbutton", background=[("active", T["panel"])])
        st.configure("Horizontal.TScale", background=T["panel"], troughcolor="#eadfcd",
                     sliderthickness=16)
        st.configure("Horizontal.TProgressbar", background=T["accent"], troughcolor="#eadfcd",
                     bordercolor=T["panel_edge"], lightcolor=T["accent"], darkcolor=T["accent"])
        st.configure("TCombobox", fieldbackground="white", background="#efe4d4", padding=4)
        st.configure("Stage.TCombobox", fieldbackground="#2d251f", foreground="#efe4d4",
                     background="#2d251f", arrowcolor="#efe4d4", bordercolor="#3a2f27")
        st.map("Stage.TCombobox", fieldbackground=[("readonly", "#2d251f")],
               foreground=[("readonly", "#efe4d4")])
        r.option_add("*TCombobox*Listbox.font", self.fonts["body"])

    def _build_ui(self) -> None:
        r = self.root
        header = ttk.Frame(r, padding=(22, 16, 22, 6))
        header.pack(fill="x")
        ttk.Label(header, text="Pastel Studio", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="   Turn a photo into a handmade oil pastel drawing",
                  style="Subtitle.TLabel").pack(side="left", pady=(10, 0))

        body = ttk.Frame(r, padding=(22, 6, 22, 6))
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        side_card = ttk.Frame(body, style="Card.TFrame")
        side_card.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        self.sidebar = ScrollFrame(side_card, style="Panel.TFrame")
        self.sidebar.pack(fill="both", expand=True, padx=1, pady=1)
        self._build_sidebar(self.sidebar.inner)

        content = ttk.Frame(body)
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure((0, 1), weight=1, uniform="prev")
        content.rowconfigure(0, weight=1)
        self.original_panel = PreviewPanel(content, "Original", "Import a photo or take one\n"
                                           "with your camera to begin\n\nJPG · PNG · WebP", self.fonts)
        self.original_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.result_panel = PreviewPanel(content, "Oil Pastel", "Your oil pastel drawing\n"
                                         "will appear here", self.fonts)
        self.result_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        actions = ttk.Frame(content, padding=(0, 14, 0, 0))
        actions.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.btn_import = ttk.Button(actions, text="Import Image", command=self.choose_image)
        self.btn_camera = ttk.Button(actions, text="Take Photo", command=self.take_photo)
        self.btn_generate = ttk.Button(actions, text="Generate Oil Pastel",
                                       command=self.generate, style="Accent.TButton")
        self.btn_draw = ttk.Button(actions, text="Start Full-Screen Drawing",
                                   command=self.start_drawing, style="Accent.TButton")
        self.btn_export_img = ttk.Button(actions, text="Export Artwork", command=self.export_artwork)
        self.btn_export_vid = ttk.Button(actions, text="Export Animation Video",
                                         command=self.export_video_dialog)
        self.btn_import.pack(side="left")
        self.btn_camera.pack(side="left", padx=(8, 0))
        self.btn_generate.pack(side="left", padx=(8, 0))
        self.btn_draw.pack(side="left", padx=(8, 0))
        self.btn_export_vid.pack(side="right")
        self.btn_export_img.pack(side="right", padx=(0, 8))

        status = ttk.Frame(r, padding=(22, 4, 22, 14))
        status.pack(fill="x")
        self.progress = ttk.Progressbar(status, mode="determinate", maximum=1.0, length=260)
        self.progress.pack(side="left")
        self.status_var = tk.StringVar(value="Welcome! Import a photo or take one with your camera.")
        ttk.Label(status, textvariable=self.status_var, style="Status.TLabel").pack(
            side="left", padx=12)
        self.btn_cancel = ttk.Button(status, text="Cancel", command=self.cancel_task)
        self.btn_cancel.pack(side="right")

    def _build_sidebar(self, parent: ttk.Frame) -> None:
        pad = dict(padx=16)

        def section(text):
            ttk.Label(parent, text=text.upper(), style="Section.TLabel").pack(
                anchor="w", pady=(16, 6), **pad)

        section("Canvas")
        self.aspect_var = tk.StringVar(value=self.settings.aspect)
        self.framing_var = tk.StringVar(value=self.settings.framing)
        self.res_var = tk.StringVar(value=self.settings.resolution)
        for label, var, values in (("Aspect ratio", self.aspect_var, list(ASPECTS)),
                                   ("Framing", self.framing_var, list(FRAMING_MODES)),
                                   ("Quality", self.res_var, list(RESOLUTIONS))):
            row = ttk.Frame(parent, style="Panel.TFrame")
            row.pack(fill="x", pady=3, **pad)
            ttk.Label(row, text=label, style="Panel.TLabel").pack(side="left")
            cb = ttk.Combobox(row, textvariable=var, values=values, state="readonly", width=19)
            cb.pack(side="right")
            cb.bind("<<ComboboxSelected>>", lambda e: self._settings_changed())

        section("Artistic settings")
        self.slider_vars: dict[str, tk.DoubleVar] = {}
        self.slider_values: dict[str, ttk.Label] = {}
        for key, label, hint in SLIDERS:
            box = ttk.Frame(parent, style="Panel.TFrame")
            box.pack(fill="x", pady=(2, 6), **pad)
            top = ttk.Frame(box, style="Panel.TFrame")
            top.pack(fill="x")
            ttk.Label(top, text=label, style="Panel.TLabel").pack(side="left")
            val = ttk.Label(top, text="", style="Value.TLabel")
            val.pack(side="right")
            var = tk.DoubleVar(value=getattr(self.settings, key) * 100)
            scale = ttk.Scale(box, from_=0, to=100, variable=var,
                              command=lambda v, k=key: self._on_slider(k))
            scale.pack(fill="x", pady=(2, 0))
            scale.bind("<ButtonRelease-1>", lambda e: self._settings_changed())
            ttk.Label(box, text=hint, style="Hint.TLabel").pack(anchor="w")
            self.slider_vars[key] = var
            self.slider_values[key] = val
            self._on_slider(key)

        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=(8, 2), **pad)
        ttk.Button(row, text="Reset", command=self.reset_settings).pack(side="left")
        ttk.Button(row, text="New variation", command=self.new_variation).pack(side="left", padx=6)
        self.auto_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text="Auto-regenerate when settings change",
                        variable=self.auto_var, style="Panel.TCheckbutton").pack(
            anchor="w", pady=(6, 0), **pad)
        ttk.Label(parent, text="Tip: use Draft quality for quick experiments.",
                  style="Hint.TLabel").pack(anchor="w", pady=(2, 0), **pad)

        section("Animation")
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=3, **pad)
        ttk.Label(row, text="Duration", style="Panel.TLabel").pack(side="left")
        self.duration_var = tk.StringVar(value=f"{self.export_settings.duration} s")
        ttk.Combobox(row, textvariable=self.duration_var, state="readonly", width=8,
                     values=[f"{d} s" for d in ANIMATION_DURATIONS]).pack(side="right")
        ttk.Label(parent, text="In full screen: Space pause · R restart\nS skip · H hide · Esc exit",
                  style="Hint.TLabel", justify="left").pack(anchor="w", pady=(4, 18), **pad)

    # ------------------------------------------------------------------ settings
    def _on_slider(self, key: str) -> None:
        v = self.slider_vars[key].get()
        self.slider_values[key].configure(text=f"{int(round(v))}")

    def _collect_settings(self) -> ArtSettings:
        values = {k: round(v.get() / 100.0, 3) for k, v in self.slider_vars.items()}
        return self.settings.copy(aspect=self.aspect_var.get(), framing=self.framing_var.get(),
                                  resolution=self.res_var.get(), **values)

    def _settings_changed(self) -> None:
        self.settings = self._collect_settings()
        if self.plan is not None and asdict(self.settings) != self.plan_settings:
            self.status_var.set("Settings changed. Click Generate Oil Pastel to apply them.")
        if self.auto_var.get() and self.source_image is not None:
            if self._regen_job:
                self.root.after_cancel(self._regen_job)
            self._regen_job = self.root.after(500, self._auto_regenerate)

    def _auto_regenerate(self) -> None:
        self._regen_job = None
        if self.task is not None:
            if self.task_kind == "generate":
                self.pending_regen = True
                self.task.cancel.cancel()
            return
        self.generate()

    def reset_settings(self) -> None:
        defaults = ArtSettings()
        for key, var in self.slider_vars.items():
            var.set(getattr(defaults, key) * 100)
            self._on_slider(key)
        self.aspect_var.set(defaults.aspect)
        self.framing_var.set(defaults.framing)
        self.res_var.set(defaults.resolution)
        self.settings = defaults
        self._settings_changed()

    def new_variation(self) -> None:
        self.settings = self._collect_settings().copy(seed=random.randint(1, 1_000_000))
        self.status_var.set("New stroke variation. Generating...")
        if self.source_image is not None and self.task is None:
            self.generate()

    # ------------------------------------------------------------------ import
    def choose_image(self) -> None:
        pattern = " ".join(f"*{e}" for e in SUPPORTED_EXTENSIONS)
        pattern_upper = " ".join(f"*{e.upper()}" for e in SUPPORTED_EXTENSIONS)
        path = filedialog.askopenfilename(
            parent=self.root, title="Choose a photo",
            filetypes=[("Images", f"{pattern} {pattern_upper}"), ("All files", "*.*")])
        if path:
            self.open_image(path)

    def open_image(self, path: str) -> None:
        try:
            image = load_image(path)
        except ImageLoadError as exc:
            messagebox.showerror(APP_NAME, str(exc), parent=self.root)
            return
        self._set_source(image, os.path.basename(path), path)

    def take_photo(self) -> None:
        dlg = CameraDialog(self.root, self.fonts)
        self.root.wait_window(dlg)
        if dlg.result is not None:
            self._set_source(dlg.result, "camera photo", None)

    def _set_source(self, image: Image.Image, name: str, path: str | None) -> None:
        self.source_path = path
        self.source_name = "camera_photo" if path is None else os.path.splitext(name)[0]
        self.source_image = image
        self.plan = None
        self.plan_settings = None
        self.original_panel.set_image(image, f"{image.width} × {image.height}")
        self.result_panel.set_image(None)
        self.status_var.set(f"Loaded {name}. Click Generate Oil Pastel.")
        self.progress["value"] = 0
        self._update_buttons()
        if self.auto_var.get():
            self.generate()

    # ------------------------------------------------------------------ generation
    def generate(self) -> None:
        if self.source_image is None:
            messagebox.showinfo(APP_NAME, "Please import an image first.", parent=self.root)
            return
        if self.task is not None:
            return
        settings = self._collect_settings()
        self.settings = settings
        image = self.source_image

        def work(cancel, progress):
            return create_artwork(image, settings, cancel, progress)

        def done(plan: DrawingPlan):
            self._task_finished()
            self.plan = plan
            self.plan_settings = asdict(settings)
            w, h = plan.size
            self.result_panel.set_image(Image.fromarray(plan.final_uint8()),
                                        f"{w} × {h} · {len(plan.strokes):,} strokes")
            self.status_var.set(f"Oil pastel ready: {len(plan.strokes):,} strokes. "
                                "Start the drawing or export it.")
            self.progress["value"] = 1.0
            self._update_buttons()
            if self.pending_regen:
                self.pending_regen = False
                self.generate()
            elif self.start_after_generate:
                self.start_after_generate = False
                self.start_drawing()

        self._run_task("generate", work, done, "Generating oil pastel...")

    def _run_task(self, kind: str, work, done, message: str) -> None:
        self.task_kind = kind
        self.status_var.set(message)
        self.progress["value"] = 0

        def error(exc):
            self._task_finished()
            if isinstance(exc, Cancelled):
                self.status_var.set("Cancelled.")
                self.progress["value"] = 0
                if kind == "generate" and self.pending_regen:
                    self.pending_regen = False
                    self.generate()
                return
            self.start_after_generate = False
            if isinstance(exc, MemoryError):
                msg = ("Not enough memory to finish. Try a lower Quality setting "
                       "or a smaller video resolution.")
            else:
                msg = str(exc) or exc.__class__.__name__
            self.status_var.set("Something went wrong.")
            messagebox.showerror(APP_NAME, msg, parent=self.root)

        def progress(frac, msg):
            self.progress["value"] = max(0.0, min(1.0, frac))
            if msg:
                self.status_var.set(msg)

        self.task = BackgroundTask(self.root, work, done, error, progress)
        self._update_buttons()

    def _task_finished(self) -> None:
        self.task = None
        self.task_kind = None
        self._update_buttons()

    def cancel_task(self) -> None:
        if self.task is not None:
            self.pending_regen = False
            self.start_after_generate = False
            self.task.cancel.cancel()
            self.status_var.set("Cancelling...")

    def _update_buttons(self) -> None:
        busy = self.task is not None
        has_img = self.source_image is not None
        has_plan = self.plan is not None

        def state(widget, enabled):
            widget.state(["!disabled"] if enabled else ["disabled"])

        state(self.btn_import, not busy)
        state(self.btn_camera, not busy)
        state(self.btn_generate, has_img and not busy)
        state(self.btn_draw, has_img and not busy)
        state(self.btn_export_img, has_plan and not busy)
        state(self.btn_export_vid, has_plan and not busy)
        state(self.btn_cancel, busy)

    # ------------------------------------------------------------------ drawing
    def _duration(self) -> int:
        return int(self.duration_var.get().split()[0])

    def start_drawing(self) -> None:
        if self.plan is None:
            if self.source_image is None:
                return
            self.start_after_generate = True
            self.generate()
            return
        self.root.withdraw()

        def restore():
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.status_var.set("Drawing closed. Export the artwork or the video when ready.")

        try:
            DrawingScreen(self.root, self.plan, self._duration(), self.fonts, on_close=restore)
        except Exception as exc:
            restore()
            messagebox.showerror(APP_NAME, f"Could not open the drawing screen:\n{exc}",
                                 parent=self.root)

    # ------------------------------------------------------------------ export
    def _default_name(self, ext: str) -> str:
        return f"{self.source_name}_oil_pastel{ext}"

    def export_artwork(self) -> None:
        if self.plan is None:
            return
        path = filedialog.asksaveasfilename(
            parent=self.root, title="Export artwork", defaultextension=".png",
            initialfile=self._default_name(".png"),
            filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg *.jpeg")])
        if not path:
            return
        if self.source_path and os.path.abspath(path) == os.path.abspath(self.source_path):
            messagebox.showerror(APP_NAME, "Please choose a different file name so the "
                                 "original photo is not overwritten.", parent=self.root)
            return
        try:
            export_image(self.plan, path)
        except (VideoExportError, ValueError, OSError) as exc:
            messagebox.showerror(APP_NAME, str(exc), parent=self.root)
            return
        self.status_var.set(f"Artwork saved to {path}")

    def export_video_dialog(self) -> None:
        if self.plan is None:
            return
        dlg = VideoDialog(self.root, self.export_settings, self._duration(), self.fonts)
        self.root.wait_window(dlg)
        if dlg.result is None:
            return
        settings = dlg.result
        self.export_settings = settings
        path = filedialog.asksaveasfilename(
            parent=self.root, title="Export drawing video", defaultextension=".mp4",
            initialfile=self._default_name(".mp4"), filetypes=[("MP4 video", "*.mp4")])
        if not path:
            return
        plan = self.plan

        def work(cancel, progress):
            return export_video(plan, path, settings, progress, cancel)

        def done(encoder):
            self._task_finished()
            self.progress["value"] = 1.0
            self.status_var.set(f"Video saved to {path}  ({encoder})")

        self._run_task("export", work, done, "Exporting video...")

    def quit(self) -> None:
        if self.task is not None:
            if not messagebox.askyesno(APP_NAME, "A task is still running. Quit anyway?",
                                       parent=self.root):
                return
            self.task.cancel.cancel()
        self.root.destroy()


class VideoDialog(tk.Toplevel):
    """Modal dialog with the MP4 export options."""

    def __init__(self, master, current: ExportSettings, duration: int, fonts: dict) -> None:
        super().__init__(master)
        self.title("Export Animation Video")
        self.configure(bg=THEME["panel"])
        self.resizable(False, False)
        self.transient(master)
        self.result: ExportSettings | None = None
        frm = ttk.Frame(self, style="Panel.TFrame", padding=20)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Drawing video", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.vars = {
            "duration": tk.StringVar(value=f"{duration} s"),
            "fps": tk.StringVar(value=str(current.fps)),
            "resolution": tk.StringVar(value=current.resolution),
            "video_format": tk.StringVar(value=current.video_format),
        }
        rows = (("Duration", "duration", [f"{d} s" for d in ANIMATION_DURATIONS]),
                ("Frames per second", "fps", [str(f) for f in VIDEO_FPS]),
                ("Resolution", "resolution", list(VIDEO_RESOLUTIONS)),
                ("Format", "video_format", list(VIDEO_FORMATS)))
        for i, (label, key, values) in enumerate(rows, start=1):
            ttk.Label(frm, text=label, style="Panel.TLabel").grid(row=i, column=0, sticky="w", pady=4)
            ttk.Combobox(frm, textvariable=self.vars[key], values=values, state="readonly",
                         width=18).grid(row=i, column=1, sticky="e", pady=4, padx=(16, 0))
        self.captions = tk.BooleanVar(value=current.show_captions)
        self.cursor = tk.BooleanVar(value=current.show_cursor)
        ttk.Checkbutton(frm, text="Show stage captions", variable=self.captions,
                        style="Panel.TCheckbutton").grid(row=5, column=0, columnspan=2,
                                                         sticky="w", pady=(10, 0))
        ttk.Checkbutton(frm, text="Show pastel stick", variable=self.cursor,
                        style="Panel.TCheckbutton").grid(row=6, column=0, columnspan=2, sticky="w")
        ttk.Label(frm, text=f"Encoder: {describe_encoder()}", style="Hint.TLabel",
                  wraplength=320).grid(row=7, column=0, columnspan=2, sticky="w", pady=(12, 0))
        btns = ttk.Frame(frm, style="Panel.TFrame")
        btns.grid(row=8, column=0, columnspan=2, sticky="e", pady=(16, 0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(btns, text="Choose file & export", style="Accent.TButton",
                   command=self._ok).pack(side="right", padx=(0, 8))
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self._ok())
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.grab_set()
        self.focus_set()

    def _ok(self) -> None:
        self.result = ExportSettings(
            duration=int(self.vars["duration"].get().split()[0]),
            fps=int(self.vars["fps"].get()),
            resolution=self.vars["resolution"].get(),
            video_format=self.vars["video_format"].get(),
            show_captions=self.captions.get(),
            show_cursor=self.cursor.get())
        self.destroy()


def _app_icon() -> Image.Image:
    """A tiny procedurally drawn palette of pastel sticks."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([4, 4, 60, 60], 14, fill=THEME["accent"])
    for i, c in enumerate(("#f6d365", "#7ec4cf", "#f4ece0", "#3b2a20")):
        x = 14 + i * 10
        d.rounded_rectangle([x, 16, x + 7, 48], 3, fill=c)
    return img
