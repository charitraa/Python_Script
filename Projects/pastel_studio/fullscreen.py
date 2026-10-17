"""The distraction-free full-screen drawing screen.

Rendering happens on a PlaybackThread; this window only polls for the most
recent frame with `after()` and pastes it into a PhotoImage, so the Tk event
loop never blocks on image processing.

Keys: Space pause/resume, R restart, S or Enter skip to final,
H hide/show controls, Esc exit.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from animation_engine import PlaybackThread, stage_background
from models import DrawingPlan
from settings import ANIMATION_DURATIONS, THEME

POLL_MS = 15
HIDE_AFTER_MS = 2600


class DrawingScreen(tk.Toplevel):
    def __init__(self, master: tk.Misc, plan: DrawingPlan, duration: int, fonts: dict,
                 on_close=None) -> None:
        super().__init__(master)
        self.plan = plan
        self.fonts = fonts
        self.on_close = on_close
        self.player: PlaybackThread | None = None
        self.photo: ImageTk.PhotoImage | None = None
        self.bg_photo: ImageTk.PhotoImage | None = None
        self.last_frame_id = -1
        self.controls_pinned_hidden = False
        self._hide_job = None
        self._poll_job = None
        self._closed = False
        self.duration_var = tk.StringVar(value=f"{duration} s")

        bg = THEME["stage_bg"]
        self.title("Pastel Studio - Drawing")
        self.configure(bg=bg, cursor="none")
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            self.attributes("-fullscreen", True)
        except tk.TclError:
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.protocol("WM_DELETE_WINDOW", self.close)

        for key, fn in (("<Escape>", self.close), ("<space>", self.toggle_pause),
                        ("r", self.restart), ("R", self.restart), ("s", self.skip),
                        ("S", self.skip), ("<Return>", self.skip),
                        ("h", self.toggle_controls), ("H", self.toggle_controls)):
            self.bind(key, lambda e, f=fn: f())
        self.bind("<Motion>", self._on_motion)

        self._build_controls()
        self.focus_force()
        # Lay out once the window has its real full-screen size.
        self.after(120, self._start)

    # ------------------------------------------------------------------ layout
    def _build_controls(self) -> None:
        bar = tk.Frame(self.canvas, bg="#241d18", padx=10, pady=6)
        style = dict(bg="#241d18", fg=THEME["stage_text"], activebackground="#3a2f27",
                     activeforeground="white", relief="flat", bd=0, padx=12, pady=6,
                     font=self.fonts["body"], cursor="hand2")
        self.btn_restart = tk.Button(bar, text="Restart", command=self.restart, **style)
        self.btn_pause = tk.Button(bar, text="Pause", command=self.toggle_pause, **style)
        self.btn_skip = tk.Button(bar, text="Skip to final", command=self.skip, **style)
        self.btn_exit = tk.Button(bar, text="Exit", command=self.close, **style)
        for b in (self.btn_restart, self.btn_pause, self.btn_skip):
            b.pack(side="left", padx=2)
        tk.Label(bar, text="Duration", bg="#241d18", fg="#a89684",
                 font=self.fonts["small"]).pack(side="left", padx=(14, 4))
        combo = ttk.Combobox(bar, textvariable=self.duration_var, state="readonly", width=6,
                             values=[f"{d} s" for d in ANIMATION_DURATIONS],
                             style="Stage.TCombobox")
        combo.pack(side="left", padx=(0, 10))
        combo.bind("<<ComboboxSelected>>", self._on_duration)
        self.btn_exit.pack(side="left", padx=2)
        self.controls = bar
        self.hint = "Space pause · R restart · S skip · H hide controls · Esc exit"

    def _start(self) -> None:
        self.update_idletasks()
        sw, sh = max(self.winfo_width(), 320), max(self.winfo_height(), 240)
        aw, ah = self.plan.size
        scale = min(sw * 0.9 / aw, (sh * 0.80) / ah)
        dw, dh = max(2, int(aw * scale)), max(2, int(ah * scale))
        x0, y0 = (sw - dw) // 2, int(sh * 0.085) + (int(sh * 0.80) - dh) // 2
        self.rect = (x0, y0, dw, dh)

        bg = stage_background((sw, sh), self.rect, _hex_to_rgb(THEME["stage_bg"]))
        self.bg_photo = ImageTk.PhotoImage(Image.fromarray(bg))
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        self.photo = ImageTk.PhotoImage(Image.new("RGB", (dw, dh), THEME["stage_bg"]))
        self.canvas.create_image(x0, y0, anchor="nw", image=self.photo)

        ty = max(18, y0 - 30)
        self.stage_text = self.canvas.create_text(
            x0, ty, anchor="w", text="", fill=THEME["stage_text"], font=self.fonts["stage"])
        self.pct_text = self.canvas.create_text(
            x0 + dw, ty, anchor="e", text="", fill="#9c8b7a", font=self.fonts["body"])
        by = y0 + dh + 14
        self.canvas.create_rectangle(x0, by, x0 + dw, by + 3, fill="#3a3029", width=0)
        self.bar = self.canvas.create_rectangle(x0, by, x0, by + 3, fill=THEME["accent"], width=0)
        self.controls_item = self.canvas.create_window(sw // 2, sh - 34, window=self.controls)
        self.hint_item = self.canvas.create_text(sw // 2, sh - 72, text=self.hint,
                                                 fill="#6f6155", font=self.fonts["small"])

        self.player = PlaybackThread(self.plan, self._duration(), (dw, dh), fps=30,
                                     background=_hex_to_rgb(THEME["stage_bg"]))
        self.player.start()
        self._show_controls()
        self._poll()

    # ------------------------------------------------------------------ loop
    def _poll(self) -> None:
        if self._closed or self.player is None:
            return
        if self.player.error is not None:
            err = self.player.error
            self.close()
            from tkinter import messagebox
            messagebox.showerror("Pastel Studio", f"The animation stopped:\n{err}")
            return
        latest = self.player.latest()
        if latest is not None and latest[0] != self.last_frame_id:
            frame_id, img, info, paused = latest
            self.last_frame_id = frame_id
            self.photo.paste(img)
            label = info.stage_label
            if info.stage_key == "final" and not info.finished:
                label = "Final Touches"
            self.canvas.itemconfigure(self.stage_text, text=label + ("  ·  paused" if paused else ""))
            self.canvas.itemconfigure(self.pct_text, text=f"{int(info.progress * 100)}%")
            x0, _, dw, _ = self.rect
            coords = self.canvas.coords(self.bar)
            self.canvas.coords(self.bar, x0, coords[1], x0 + dw * info.progress, coords[3])
            if info.finished:
                self.btn_pause.configure(text="Play again", command=self.restart)
            else:
                self.btn_pause.configure(text="Resume" if paused else "Pause",
                                         command=self.toggle_pause)
        self._poll_job = self.after(POLL_MS, self._poll)

    # ------------------------------------------------------------------ controls
    def _duration(self) -> int:
        return int(self.duration_var.get().split()[0])

    def _on_duration(self, _event=None) -> None:
        if self.player:
            self.player.set_duration(self._duration())
        self.focus_set()

    def toggle_pause(self) -> None:
        if self.player:
            self.player.toggle()
            self._show_controls()

    def restart(self) -> None:
        if self.player:
            self.player.restart()
            self._show_controls()

    def skip(self) -> None:
        if self.player:
            self.player.skip()

    def toggle_controls(self) -> None:
        self.controls_pinned_hidden = not self.controls_pinned_hidden
        if self.controls_pinned_hidden:
            self._hide_controls()
        else:
            self._show_controls()

    def _on_motion(self, _event=None) -> None:
        if not self.controls_pinned_hidden:
            self._show_controls()

    def _show_controls(self) -> None:
        if not hasattr(self, "controls_item") or self.controls_pinned_hidden:
            return
        self.canvas.itemconfigure(self.controls_item, state="normal")
        self.canvas.itemconfigure(self.hint_item, state="normal")
        self.configure(cursor="")
        if self._hide_job:
            self.after_cancel(self._hide_job)
        self._hide_job = self.after(HIDE_AFTER_MS, self._hide_controls)

    def _hide_controls(self) -> None:
        self._hide_job = None
        if self._closed or not hasattr(self, "controls_item"):
            return
        self.canvas.itemconfigure(self.controls_item, state="hidden")
        self.canvas.itemconfigure(self.hint_item, state="hidden")
        self.configure(cursor="none")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self.player:
            self.player.stop()
        for job in (self._hide_job, self._poll_job):
            if job:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
        try:
            self.attributes("-fullscreen", False)
        except tk.TclError:
            pass
        self.destroy()
        if self.on_close:
            self.on_close()


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
