import os
from tkinter import Tk, filedialog
from PIL import Image

# Hide the root Tkinter window
Tk().withdraw()

# Select folder containing .jpg images
folder_path = filedialog.askdirectory(title="Select a folder with JPG images")
if not folder_path:
    print("No folder selected. Exiting...")
    exit()

# Create output folder for PNG images
output_folder = os.path.join(folder_path, "Converted_PNGs")
os.makedirs(output_folder, exist_ok=True)

# Convert each .jpg image to .png
for file_name in os.listdir(folder_path):
    if file_name.lower().endswith(".jpg"):
        img_path = os.path.join(folder_path, file_name)
        img = Image.open(img_path)
        png_file_name = os.path.splitext(file_name)[0] + ".png"
        png_file_path = os.path.join(output_folder, png_file_name)
        img.save(png_file_path, "PNG")
        print(f"Converted: {file_name} -> {png_file_name}")

print(f"\nAll JPG images have been converted to PNG and saved in: {output_folder}")
