# Video → Image Conversion Toolkit

## Install (প্রথমবার একবার করুন)

```bash
pip install -r requirements.txt
```

## Main tool: `video_to_frames_app.py`

এটাই আপনার মূল টুল — ভিডিও থেকে ফ্রেম বের করার জন্য।

**চালানোর নিয়ম:**

```bash
python video_to_frames_app.py
```

1. একটা উইন্ডো খুলবে — **"▶ Run"** বাটনে ক্লিক করুন
2. ভিডিও ফাইল সিলেক্ট করুন
3. ফ্রেম গ্যাপ সিলেক্ট করুন — **প্রতি ৫টি** অথবা **প্রতি ১০টি** ফ্রেমে ১টি ছবি (অথবা নিজের সংখ্যা লিখুন)
4. Progress bar দেখাবে, শেষে output folder খুলে দেখাবে

**এই ভার্সনে যা ঠিক করা হয়েছে (পুরনো scripts-এর তুলনায়):**

| সমস্যা | কারণ | সমাধান |
|---|---|---|
| Image save হচ্ছিল না | `cv2.imwrite()` Windows-এ বাংলা/non-ASCII path-এ চুপচাপ fail করে | Unicode-safe write (`cv2.imencode` + `tofile`) |
| Output folder এলোমেলো জায়গায় তৈরি হতো | Relative path, working directory-র উপর নির্ভরশীল ছিল | এখন সবসময় script-এর পাশেই তৈরি হয় |
| বারবার folder-এর নাম manually বদলাতে হতো | Fixed folder name (`output_images`) — প্রতি run-এ overwrite হতো | `Output Image 1`, `Output Image 2`—এভাবে automatic sequence |
| Merge করলে filename duplicate হয়ে যেত | প্রতিটি folder-এ আবার ১ থেকে শুরু হওয়া নাম | সব numbered output folder জুড়ে global image sequence (`1.png`, `2.png`, ...) |

ফাইলের নামের ধরন: `1.png`, `2.png`, `3.png` ...

আগের numbered output folder থাকলে নতুন folder এবং ছবির numbering সেখানকার সর্বোচ্চ নম্বরের পর থেকে চলবে। সব output folder মুছে দিলে পরবর্তী run আবার `Output Image 1` এবং `1.png` থেকে শুরু হবে।

## অন্যান্য utility scripts (আগের মতোই আছে)

- `rename.py` — একটা ফোল্ডারের `.png` ছবি bulk rename করে
- `jpg to png.py` — একটা ফোল্ডারের সব `.jpg` কে `.png`-তে convert করে
- `suffleing image.py` — dataset randomization-এর জন্য ছবির ক্রম এলোমেলো করে দেয়

এই তিনটা script আগের মতোই কাজ করে, এগুলোতে কোনো bug রিপোর্ট হয়নি তাই পরিবর্তন করা হয়নি। যদি এগুলোতেও কোনো সমস্যা থাকে, জানাবেন।
