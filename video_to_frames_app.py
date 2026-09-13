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
3. Unique, mergeable filenames: every run gets its own run-id (tied to the unique
   output folder name) baked into every filename, e.g.
   myvideo_20260913_201455_000001.jpg
   So even if you merge many output folders into one, filenames never collide.
4. No more manual folder renaming: a new, uniquely named output folder
   (output_images_<timestamp>) is created automatically every run. If a folder
   with that name somehow already exists, a counter is appended automatically.
"""

import os
import sys
import threading
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


def make_unique_output_folder(base_dir, prefix="output_images"):
    """Create a fresh output folder that never collides with an existing one."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{prefix}_{timestamp}"
    folder_path = os.path.join(base_dir, folder_name)

    counter = 1
    while os.path.exists(folder_path):
        folder_name = f"{prefix}_{timestamp}_{counter}"
        folder_path = os.path.join(base_dir, folder_name)
        counter += 1

    os.makedirs(folder_path)
    return folder_path, folder_name


def safe_imwrite(path, image, ext=".jpg"):
    """Unicode-safe replacement for cv2.imwrite (works with any path, any language)."""
    ok, buf = cv2.imencode(ext, image)
    if not ok:
        return False
    buf.tofile(path)
    return True


def extract_frames(video_path, output_dir, interval, run_id=None, progress_callback=None):
    """
    Save every `interval`-th frame from video_path into output_dir.
    Filenames: <video-name>_<run-id>_<sequence>.jpg  -> globally unique,
    safe to merge multiple output folders together.

    run_id should come from the *same* unique output folder name
    (see make_unique_output_folder) rather than a fresh timestamp here,
    so two runs started in the same second still can't collide.

    Returns the number of images saved.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    video_stem = sanitize_name(os.path.splitext(os.path.basename(video_path))[0])
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    frame_index = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index % interval == 0:
            saved_count += 1
            filename = f"{video_stem}_{run_id}_{saved_count:06d}.jpg"
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
                                        run_id=folder_name,
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
