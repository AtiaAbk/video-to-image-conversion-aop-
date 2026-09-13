import os
import tkinter as tk
from tkinter import filedialog


def rename_images(directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    files = [f for f in os.listdir(directory) if f.endswith('.png')]
    files.sort()  # Sort the files to maintain order

    for index, file in enumerate(files, start=7000):
        old_path = os.path.join(directory, file)
        new_path = os.path.join(output_directory, f"{index}.png")
        os.rename(old_path, new_path)

    print(f"Renamed and moved {len(files)} files successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="Select Input Folder")
    output_folder = os.path.join(folder_path, "output")

    if folder_path:
        rename_images(folder_path, output_folder)
    else:
        print("No folder selected!")
