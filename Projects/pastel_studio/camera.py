"""Take a photo with a webcam and hand it to the app as the source image.

Frames are read on a background thread (camera reads block); the dialog
polls the newest frame with `after()` and shows it as a live preview.
"""

from __future__ import annotations

import sys
import threading
import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

from settings import THEME

MAX_CAMERAS = 4


def _open_camera(index: int) -> cv2.VideoCapture:
    if sys.platform == "win32":
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # opens much faster than MSMF
    else:
        cap = cv2.VideoCapture(index)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap


class _Grabber(threading.Thread):
    """Continuously reads frames so the preview never blocks the UI."""

    def __init__(self, index: int) -> None:
        super().__init__(daemon=True)
        self.index = index
        self.frame = None          # newest RGB numpy frame
        self.error: str | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()

    def run(self) -> None:
        cap = _open_camera(self.index)
        if not cap.isOpened():
            self.error = (f"Camera {self.index} could not be opened.\n"
                          "Check that it is connected and not used by another app.")
            return
        failures = 0
        try:
            while not self._stop.is_set():
                ok, bgr = cap.read()
                if not ok or bgr is None:
                    failures += 1
                    if failures > 50:
                        self.error = "The camera stopped sending pictures."
                        return
                    continue
                failures = 0
                with self._lock:
                    self.frame = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        finally:
            cap.release()

    def latest(self):
        with self._lock:
            return None if self.frame is None else self.frame.copy()

    def stop(self) -> None:
        self._stop.set()


class CameraDialog(tk.Toplevel):
    """Modal webcam dialog. After closing, `result` is a PIL image or None."""

    def __init__(self, master: tk.Misc, fonts: dict) -> None:
        super().__init__(master)
        self.title("Take a Photo")
        self.configure(bg=THEME["panel"])
        self.transient(master)
        self.minsize(560, 480)
        self.fonts = fonts
        self.result: Image.Image | None = None
        self.captured: Image.Image | None = None
        self.grabber: _Grabber | None = None
        self._photo = None
        self._poll_job = None
        self._countdown = 0

        top = ttk.Frame(self, style="Panel.TFrame", padding=(16, 12, 16, 0))
        top.pack(fill="x")
        ttk.Label(top, text="Camera", style="Panel.TLabel").pack(side="left")
        self.cam_var = tk.StringVar(value="Camera 1")
        cam_box = ttk.Combobox(top, textvariable=self.cam_var, state="readonly", width=10,
                               values=[f"Camera {i + 1}" for i in range(MAX_CAMERAS)])
        cam_box.pack(side="left", padx=(8, 16))
        cam_box.bind("<<ComboboxSelected>>", lambda e: self._start_camera())
        self.mirror_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Mirror", variable=self.mirror_var,
                        style="Panel.TCheckbutton").pack(side="left")
        self.timer_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="3 s timer", variable=self.timer_var,
                        style="Panel.TCheckbutton").pack(side="left", padx=(12, 0))

        self.canvas = tk.Canvas(self, bg="#1d1814", highlightthickness=0, width=640, height=420)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=12)

        bottom = ttk.Frame(self, style="Panel.TFrame", padding=(16, 0, 16, 14))
        bottom.pack(fill="x")
        self.btn_cancel = ttk.Button(bottom, text="Cancel", command=self.close)
        self.btn_cancel.pack(side="right")
        self.btn_use = ttk.Button(bottom, text="Use This Photo", style="Accent.TButton",
                                  command=self._use)
        self.btn_retake = ttk.Button(bottom, text="Retake", command=self._retake)
        self.btn_capture = ttk.Button(bottom, text="Capture", style="Accent.TButton",
                                      command=self._capture)
        self.btn_capture.pack(side="right", padx=(0, 8))

        self.bind("<Escape>", lambda e: self.close())
        self.bind("<space>", lambda e: self._capture() if self.captured is None else None)
        self.bind("<Return>", lambda e: self._use() if self.captured is not None else None)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.grab_set()
        self.focus_set()
        self._start_camera()

    # ------------------------------------------------------------------ camera
    def _start_camera(self) -> None:
        if self.grabber:
            self.grabber.stop()
        index = int(self.cam_var.get().split()[-1]) - 1
        self.grabber = _Grabber(index)
        self.grabber.start()
        self.captured = None
        self._show_capture_buttons()
        if self._poll_job is None:
            self._poll()

    def _poll(self) -> None:
        self._poll_job = None
        if self.captured is None and self.grabber is not None:
            if self.grabber.error:
                self._message(self.grabber.error)
            else:
                frame = self.grabber.latest()
                if frame is None:
                    self._message("Starting camera...")
                else:
                    self._show(self._to_image(frame), self._countdown)
        self._poll_job = self.after(33, self._poll)

    def _to_image(self, frame) -> Image.Image:
        img = Image.fromarray(frame)
        if self.mirror_var.get():
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return img

    # ------------------------------------------------------------------ drawing
    def _show(self, img: Image.Image, countdown: int = 0) -> None:
        c = self.canvas
        w, h = max(c.winfo_width(), 50), max(c.winfo_height(), 50)
        scale = min(w / img.width, h / img.height)
        shown = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))),
                           Image.Resampling.BILINEAR)
        self._photo = ImageTk.PhotoImage(shown)
        c.delete("all")
        c.create_image(w // 2, h // 2, image=self._photo)
        if countdown:
            c.create_text(w // 2, h // 2, text=str(countdown), fill="white",
                          font=(self.fonts["title"][0], 72, "bold"))

    def _message(self, text: str) -> None:
        c = self.canvas
        c.delete("all")
        c.create_text(c.winfo_width() // 2, c.winfo_height() // 2, text=text, fill="#cbbba8",
                      font=self.fonts["body"], justify="center")

    # ------------------------------------------------------------------ actions
    def _capture(self) -> None:
        if self.grabber is None or self.grabber.latest() is None:
            return
        if self.timer_var.get() and self._countdown == 0:
            self._countdown = 3
            self.btn_capture.state(["disabled"])
            self.after(1000, self._tick)
            return
        self._take()

    def _tick(self) -> None:
        self._countdown -= 1
        if self._countdown > 0:
            self.after(1000, self._tick)
        else:
            self.btn_capture.state(["!disabled"])
            self._take()

    def _take(self) -> None:
        frame = self.grabber.latest() if self.grabber else None
        if frame is None:
            return
        self.captured = self._to_image(frame)
        self._show(self.captured)
        self.btn_capture.pack_forget()
        self.btn_use.pack(side="right", padx=(0, 8))
        self.btn_retake.pack(side="right", padx=(0, 8))

    def _retake(self) -> None:
        self.captured = None
        self._show_capture_buttons()

    def _show_capture_buttons(self) -> None:
        self.btn_use.pack_forget()
        self.btn_retake.pack_forget()
        self.btn_capture.pack(side="right", padx=(0, 8))

    def _use(self) -> None:
        if self.captured is not None:
            self.result = self.captured
            self.close()

    def close(self) -> None:
        if self.grabber:
            self.grabber.stop()
        if self._poll_job:
            self.after_cancel(self._poll_job)
            self._poll_job = None
        self.grab_release()
        self.destroy()
