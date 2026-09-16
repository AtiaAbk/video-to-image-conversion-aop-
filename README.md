# Video → Image Conversion Toolkit

## Installation (Do this once)

```bash
pip install -r requirements.txt
```

## Main Tool: `video_to_frames_app.py`

This is the main tool for extracting frames from videos.

**How to run:**

```bash
python video_to_frames_app.py
```

1. A window will open — click the **"▶ Run"** button.
2. Select a video file.
3. Select the frame interval — extract **1 image every 5 frames** or **1 image every 10 frames**, or enter your own number.
4. A progress bar will show the conversion progress.
5. When finished, the output folder will open automatically.

## Fixes in This Version

| Problem                                             | Cause                                                                                           | Solution                                                                                         |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Images were not being saved                         | `cv2.imwrite()` can silently fail on Windows when the path contains Bangla/non-ASCII characters | Unicode-safe image writing using `cv2.imencode` + `tofile`                                       |
| Output folder was created in inconsistent locations | The relative path depended on the current working directory                                     | Output folders are now always created next to the script                                         |
| Folder names had to be changed manually every time  | A fixed folder name (`output_images`) was used, causing files to be overwritten                 | Folders are automatically created as `Output Image 1`, `Output Image 2`, etc.                    |
| Duplicate filenames appeared when merging outputs   | Each folder started numbering from 1 again                                                      | A global image sequence is maintained across all numbered output folders (`1.png`, `2.png`, ...) |

### File Naming

Images are saved using sequential filenames:

```text
1.png
2.png
3.png
...
```

If numbered output folders already exist, the next folder and image numbering will continue from the highest existing number.

For example:

```text
Output Image 1
├── 1.png
├── 2.png
└── 3.png

Output Image 2
├── 4.png
├── 5.png
└── 6.png
```

If all output folders are deleted, the next run will start again from:

```text
Output Image 1
1.png
```

## Other Utility Scripts

The following utility scripts remain unchanged and work as before:

* `rename.py` — Bulk renames `.png` images in a folder.
* `jpg to png.py` — Converts all `.jpg` images in a folder to `.png`.
* `suffleing image.py` — Randomizes the order of images for dataset preparation.

These three scripts have not been modified because no bugs have been reported with them. If you encounter any issues with these scripts, please let me know.
