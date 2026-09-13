import os
import random
import tkinter as tk
from tkinter import filedialog
from PIL import Image

# Function to select input folder using Tkinter
def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory(title="Select Input Folder")
    return folder_selected

# Select input folder
input_folder = select_folder()
if not input_folder:
    print("No folder selected. Exiting.")
    exit()

# Define output folder
output_folder = os.path.join(os.path.dirname(input_folder), "output")
os.makedirs(output_folder, exist_ok=True)

# Image settings
output_size = (1920, 1080)  # Resize output images (width, height)

# Load images in sequential order (sorted numerically)
image_files = sorted(
    [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
    key=lambda x: int(os.path.splitext(x)[0])  # Sort by numeric filename
)

# Shuffle images to change their order
shuffled_files = image_files.copy()
random.shuffle(shuffled_files)

# Process and save images in new sequential order
for new_index, img_name in enumerate(shuffled_files, start=1):
    img_path = os.path.join(input_folder, img_name)
    img = Image.open(img_path).convert("RGBA")

    # Resize image
    img = img.resize(output_size)

    # Save with new sequential name
    output_path = os.path.join(output_folder, f"{new_index}.png")
    img.save(output_path)

    print(f"Saved: {output_path}")

print(f"Processing complete! Images saved in: {output_folder}")
