# -*- coding: utf-8 -*-
"""
Video -> Frames converter
--------------------------
Run -> Select video -> Select frame gap (5 / 10 / custom) -> images saved automatically.

Fixes vs. the old scripts:
1. Images not saving: cv2.imwrite() silently fails on Windows when the path has
   non-ASCII characters (e.g. Bengali folder/user names). Fixed with a unicode-safe
   write using cv2.imencode + numpy tofile().
2. Output folder location: old scripts used a relative "output_images" folder,
   which depends on the current working directory (can end up in a random place).
   Now the output folder is always created next to this script.
3. Unique, mergeable filenames: image numbers continue globally across all
   numbered output folders (1.jpg, 2.jpg, 3.jpg, ...), so merged folders have
   no duplicate names.
4. No more manual folder renaming: folders are created as Output Image 1,
   Output Image 2, Output Image 3, ... . If all such folders are deleted,
   the next run starts again from Output Image 1 and image 1.jpg.
"""

import os
import sys
import threading
import re
from datetime import datetime

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# ---------------------------------------------------------------------------
# Core logic (no tkinter dependency here -> easy to test on its own)
# ---------------------------------------------------------------------------

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def sanitize_name(name):
    """Keep the name filesystem-safe but preserve unicode characters."""
    bad_chars = '<>:"/\\|?*'
    cleaned = "".join(c for c in name if c not in bad_chars).strip()
    return cleaned or "video"


def make_unique_output_folder(base_dir, prefix="Output Image"):
    """Create the next numbered output folder (Output Image 1, 2, ...)."""
    pattern = re.compile(rf"^{re.escape(prefix)} (\d+)$", re.IGNORECASE)
    numbers = []
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        match = pattern.match(name)
        if match and os.path.isdir(path):
            numbers.append(int(match.group(1)))

    next_number = max(numbers, default=0) + 1
    folder_name = f"{prefix} {next_number}"
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=False)
    return folder_path, folder_name


def get_next_image_number(base_dir, folder_prefix="Output Image"):
    """Return the next global image number across all numbered output folders."""
    folder_pattern = re.compile(rf"^{re.escape(folder_prefix)} \d+$", re.IGNORECASE)
    highest = 0
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if not folder_pattern.match(folder) or not os.path.isdir(folder_path):
            continue
        for filename in os.listdir(folder_path):
            stem, ext = os.path.splitext(filename)
            if ext.lower() in {".jpg", ".jpeg", ".png"} and stem.isdigit():
                highest = max(highest, int(stem))
    return highest + 1


def safe_imwrite(path, image, ext=".jpg"):
    """Unicode-safe replacement for cv2.imwrite (works with any path, any language)."""
    ok, buf = cv2.imencode(ext, image)
    if not ok:
        return False
    buf.tofile(path)
    return True


def extract_frames(video_path, output_dir, interval, start_number=1, progress_callback=None):
    """
    Save every `interval`-th frame from video_path into output_dir.
    Filenames are global sequential numbers (1.jpg, 2.jpg, ...), so
    multiple output folders can be merged without collisions.

    Returns the number of images saved.
    """
    if not isinstance(interval, int) or interval <= 0:
        raise ValueError("interval must be a positive integer")
    if not isinstance(start_number, int) or start_number <= 0:
        raise ValueError("start_number must be a positive integer")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    frame_index = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index % interval == 0:
            saved_count += 1
            filename = f"{start_number + saved_count - 1}.jpg"
            out_path = os.path.join(output_dir, filename)
            if not safe_imwrite(out_path, frame):
                print(f"Warning: failed to save -> {out_path}")

        frame_index += 1

        if progress_callback:
            progress_callback(frame_index, total_frames, saved_count)

    cap.release()
    return saved_count


def open_folder(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa
        elif sys.platform == "darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')
    except Exception:
        pass


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

def ask_interval(parent):
    """Small dialog: choose every-5th or every-10th frame, or type a custom number."""
    result = {"value": None}

    dialog = tk.Toplevel(parent)
    dialog.title("Select Frame Gap")
    dialog.resizable(False, False)
    dialog.grab_set()

    tk.Label(
        dialog, text="How many frames apart should images be captured?", font=("Segoe UI", 11)
    ).pack(padx=20, pady=(15, 10))

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=5)

    def choose(v):
        result["value"] = v
        dialog.destroy()

    tk.Button(btn_frame, text="Every 5th frame", width=18,
              command=lambda: choose(5)).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(btn_frame, text="Every 10th frame", width=18,
              command=lambda: choose(10)).grid(row=0, column=1, padx=5, pady=5)

    custom_frame = tk.Frame(dialog)
    custom_frame.pack(pady=(5, 15))
    tk.Label(custom_frame, text="Or enter a custom number:").pack(side="left", padx=(0, 5))
    entry = tk.Entry(custom_frame, width=6)
    entry.pack(side="left")

    def choose_custom():
        val = entry.get().strip()
        if val.isdigit() and int(val) > 0:
            choose(int(val))
        else:
            messagebox.showerror("Invalid Input", "Please enter a valid number (1 or greater).", parent=dialog)

    tk.Button(custom_frame, text="OK", command=choose_custom).pack(side="left", padx=5)

    dialog.wait_window()
    return result["value"]


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video → Image Converter")
        self.root.geometry("380x170")
        self.root.resizable(False, False)

        tk.Label(self.root, text="Generate Images from Video",
                 font=("Segoe UI", 13, "bold")).pack(pady=(20, 10))

        self.run_btn = tk.Button(self.root, text="▶ Run", font=("Segoe UI", 11),
                                  width=15, command=self.on_run)
        self.run_btn.pack(pady=10)

        self.status_label = tk.Label(self.root, text="", fg="#555", wraplength=340, justify="center")
        self.status_label.pack(pady=5)

    def on_run(self):
        video_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv *.MP4 *.MOV *.AVI *.MKV"),
                       ("All files", "*.*")],
        )
        if not video_path:
            return

        interval = ask_interval(self.root)
        if not interval:
            return

        output_dir, folder_name = make_unique_output_folder(get_script_dir())
        start_number = get_next_image_number(get_script_dir())

        self.run_btn.config(state="disabled")
        self.status_label.config(text=f"Processing started... ({folder_name})")

        progress_win = tk.Toplevel(self.root)
        progress_win.title("Processing...")
        progress_win.geometry("320x100")
        progress_win.resizable(False, False)
        pb = ttk.Progressbar(progress_win, length=280, mode="determinate")
        pb.pack(pady=15)
        pct_label = tk.Label(progress_win, text="0%")
        pct_label.pack()

        def update_progress(frame_index, total_frames, saved_count):
            pct = int(frame_index / total_frames * 100) if total_frames else 0

            def apply():
                pb.config(value=pct)
                pct_label.config(text=f"{pct}%  |  {saved_count} images saved")
            self.root.after(0, apply)

        def worker():
            try:
                saved = extract_frames(video_path, output_dir, interval,
                                        start_number=start_number,
                                        progress_callback=update_progress)
                self.root.after(0, lambda: self.finish(True, saved, output_dir, progress_win))
            except Exception as e:
                err = str(e)
                self.root.after(0, lambda: self.finish(False, 0, output_dir, progress_win, error=err))

        threading.Thread(target=worker, daemon=True).start()

    def finish(self, success, saved, output_dir, progress_win, error=None):
        progress_win.destroy()
        self.run_btn.config(state="normal")
        if success:
            self.status_label.config(text=f"Done! {saved} images saved.")
            if messagebox.askyesno("Completed",
                                    f"{saved} images saved:\n{output_dir}\n\nOpen the folder now?"):
                open_folder(output_dir)
        else:
            self.status_label.config(text="Something went wrong.")
            messagebox.showerror("Error", f"An error occurred during processing:\n{error}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
