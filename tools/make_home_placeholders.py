#!/usr/bin/env python3
"""Make sample videos and photos for the Pappi home page.

Every file is clearly marked SAMPLE. Real guest videos and photos replace
these files later, with the same file names (see docs/assets-needed.md).

Run:  python3 tools/make_home_placeholders.py
Needs: numpy, Pillow, ffmpeg, the Poppins font (set FONT_DIR if it is not in the folder below).
"""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "media")
FONT_DIR = os.environ.get("FONT_DIR", "/usr/share/fonts/truetype/google-fonts")
FPS = 24

# The Pappi palette (same as index.html): paper, ink and three flat street-poster colours.
INK = (20, 20, 20)
NIGHT = (20, 20, 20)
PAPER = (246, 242, 234)
SAND = (236, 230, 218)
CLAY = (255, 59, 141)  # pink
MANGO = (255, 210, 0)  # yellow
GREEN = (43, 92, 255)  # blue
SEA = (43, 92, 255)
WARM = (255, 184, 96)
AMBER = (255, 150, 60)


def font(size, style="Bold"):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"Poppins-{style}.ttf"), max(8, int(size)))


# ----------------------------------------------------------------- drawing
def gradient(W, H, top, bottom):
    t = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    top, bottom = np.array(top, np.float32), np.array(bottom, np.float32)
    return np.ascontiguousarray(np.broadcast_to(top * (1 - t) + bottom * t, (H, W, 3)))


def glow(img, cx, cy, r, col, k=1.0):
    """Soft round light added onto img (float, 0 to 255)."""
    H, W = img.shape[:2]
    gx = np.exp(-((np.arange(W, dtype=np.float32) - cx) ** 2) / (2 * r * r))
    gy = np.exp(-((np.arange(H, dtype=np.float32) - cy) ** 2) / (2 * r * r))
    img += (gy[:, None] * gx[None, :])[..., None] * (np.array(col, np.float32) * k)


def chip(d, xy, text, bg=MANGO, fg=INK, size=22):
    f = font(size)
    tw = d.textlength(text, font=f)
    x, y = xy
    pad = size * 0.5
    d.rounded_rectangle([x, y, x + tw + 2 * pad, y + size * 1.7], radius=size * 0.5, fill=bg)
    d.text((x + pad, y + size * 0.28), text, font=f, fill=fg)


def label(pil, big, small, y_frac=0.5, big_size=None, small_size=None, chip_text="SAMPLE"):
    """Big centred text, a smaller line under it, and a SAMPLE chip in the corner."""
    W, H = pil.size
    d = ImageDraw.Draw(pil)
    bs = big_size or min(W, H) * 0.085
    ss = small_size or bs * 0.42
    fb, fs = font(bs, "BoldItalic"), font(ss)
    lines = big.split("\n")
    y = H * y_frac - (len(lines) * bs * 1.15 + ss * 1.6) / 2
    for line in lines:
        tw = d.textlength(line, font=fb)
        d.text(((W - tw) / 2, y), line, font=fb, fill=PAPER, stroke_width=int(bs * 0.08), stroke_fill=INK)
        y += bs * 1.15
    if small:
        tw = d.textlength(small, font=fs)
        d.text(((W - tw) / 2, y + ss * 0.4), small, font=fs, fill=PAPER, stroke_width=int(ss * 0.1), stroke_fill=INK)
    if chip_text:
        chip(d, (W * 0.04, W * 0.04), chip_text, size=max(14, min(W, H) * 0.028))
    return pil


def to_pil(img):
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def palm(d, x, ground, h, lean, col):
    pts = [(x + lean * (k / 20) ** 2 * h, ground - (k / 20) * h) for k in range(21)]
    for i in range(20):
        d.line([pts[i], pts[i + 1]], fill=col, width=int(max(2, (1 - i / 22) * h * 0.06)))
    top = pts[-1]
    for a in range(0, 360, 30):
        ang = math.radians(a)
        L = h * 0.5
        fp = [(top[0] + math.cos(ang) * L * f, top[1] - math.sin(ang) * L * f * 0.6 + f * f * L * 0.6)
              for f in [k / 12 for k in range(13)]]
        for i in range(12):
            d.line([fp[i], fp[i + 1]], fill=col, width=int(max(2, h * 0.035 * (1 - i / 12))))


def crowd(d, ground, W, n, col, seed):
    """Simple people shapes along the ground (heads and shoulders)."""
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x = rng.uniform(0, W)
        h = rng.uniform(0.12, 0.2) * W * 0.5
        r = h * 0.18
        d.rounded_rectangle([x - h * 0.22, ground - h * 0.72, x + h * 0.22, ground], radius=h * 0.12, fill=col)
        d.ellipse([x - r, ground - h, x + r, ground - h + 2 * r], fill=col)


# ------------------------------------------------------------------ videos
def write_video(frames, path, W, H, crf=26):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1", "-g", str(FPS * 2),
           "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in frames:
        p.stdin.write(np.ascontiguousarray(fr).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed for " + path)


def make_lights(W, H, n, seed, cols):
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n):
        out.append((rng.uniform(0, W), rng.uniform(H * 0.05, H * 0.95), rng.uniform(-14, 14),
                    rng.uniform(0.02, 0.07) * max(W, H), cols[k % len(cols)], rng.uniform(0, 6.3)))
    return out


def party_frame(W, H, t, L, top, bottom, big, small, y_frac, chip_text="SAMPLE"):
    img = gradient(W, H, top, bottom)
    for (x0, y0, vx, r, col, ph) in L:
        x = (x0 + vx * t + r) % (W + 2 * r) - r
        y = y0 + 0.02 * H * math.sin(2 * math.pi * t / 4 + ph)
        k = 0.7 + 0.3 * abs(math.sin(2 * math.pi * 1.0 * t + ph))  # 120 bpm pulse
        glow(img, x, y, r, col, 0.9 * k)
        glow(img, x, y, r * 0.22, PAPER, 0.6 * k)
    return np.asarray(label(to_pil(img), big, small, y_frac, chip_text=chip_text))


def hero(name, W, H, seconds=8):
    L = make_lights(W, H, 22, 5, [WARM, AMBER, MANGO, PAPER, CLAY, WARM])
    frames = (party_frame(W, H, f / FPS, L, NIGHT, (70, 38, 28), "SAMPLE VIDEO", "A real Pappi night goes here", 0.3)
              for f in range(seconds * FPS))
    first = party_frame(W, H, 0, L, NIGHT, (70, 38, 28), "SAMPLE VIDEO", "A real Pappi night goes here", 0.3)
    Image.fromarray(first).save(os.path.join(OUT, name + ".jpg"), quality=80, optimize=True, progressive=True)
    write_video(frames, os.path.join(OUT, name + ".mp4"), W, H)


STORY_THEMES = [((40, 20, 16), CLAY), ((16, 40, 34), (40, 150, 110)), ((60, 40, 14), MANGO),
                ((30, 20, 15), AMBER), ((40, 36, 32), SAND), ((20, 18, 16), (120, 50, 40))]


def story(i, W=540, H=960, seconds=5):
    top, bottom = STORY_THEMES[i % len(STORY_THEMES)]
    L = make_lights(W, H, 10, 100 + i, [PAPER, WARM, MANGO])
    big, small = f"SAMPLE\nGUEST VIDEO {i + 1}", "A real guest talking goes here"
    first = party_frame(W, H, 0, L, top, bottom, big, small, 0.38, None)
    Image.fromarray(first).save(os.path.join(OUT, f"story-{i + 1}.jpg"), quality=78, optimize=True, progressive=True)
    write_video((party_frame(W, H, f / FPS, L, top, bottom, big, small, 0.38, None) for f in range(seconds * FPS)),
                os.path.join(OUT, f"story-{i + 1}.mp4"), W, H)


# ------------------------------------------------------------------ photos
DAY = [  # (file, time, sky top, sky bottom, sun colour and height, number of string lights, people)
    ("day-1", "10 am", (90, 160, 235), (225, 238, 250), (PAPER, 0.3), 0, 2),
    ("day-2", "1 pm", (40, 120, 230), (160, 210, 245), (PAPER, 0.12), 0, 7),
    ("day-3", "5 pm", (90, 60, 110), (255, 150, 70), (MANGO, 0.82), 0, 8),
    ("day-4", "9 pm", (24, 18, 36), (110, 60, 50), None, 24, 12),
    ("day-5", "1 am", (12, 9, 12), (50, 28, 22), None, 30, 16),
    ("day-6", "6 am", (60, 70, 140), (255, 190, 120), (WARM, 0.86), 0, 4),
]


def scene(W, H, top, bottom, sun, n_lights, people, seed, big, small, chip_text="SAMPLE PHOTO"):
    img = gradient(W, H, top, bottom)
    horizon = H * 0.72
    if sun:
        col, hf = sun
        glow(img, W * 0.68, H * hf, W * 0.18, col, 0.55)
        glow(img, W * 0.68, H * hf, W * 0.035, col, 1.2)
    rng = np.random.default_rng(seed)
    for _ in range(n_lights):
        x = rng.uniform(0, W)
        y = H * 0.35 + 0.08 * H * math.sin(x / W * 9) + rng.uniform(-8, 8)
        glow(img, x, y, W * 0.012, [WARM, MANGO, PAPER, AMBER][int(rng.integers(4))], 1.4)
    pil = to_pil(img)
    d = ImageDraw.Draw(pil)
    dark = tuple(int(c * 0.35) for c in bottom) if n_lights else (40, 30, 50)
    d.rectangle([0, horizon, W, H], fill=dark)
    for (x, h, lean) in [(0.08, 0.5, 0.25), (0.22, 0.42, -0.2), (0.9, 0.55, -0.3), (0.78, 0.38, 0.22)]:
        palm(d, W * x, horizon + 4, H * h, lean, dark if not n_lights else (10, 6, 16))
    crowd(d, horizon + H * 0.06, W, people, (14, 8, 20) if n_lights else (30, 22, 40), seed)
    return label(pil, big, small, 0.46, chip_text=chip_text)


def day_photos(W=1200, H=800):
    for i, (name, when, top, bottom, sun, nl, people) in enumerate(DAY):
        pil = scene(W, H, top, bottom, sun, nl, people, 20 + i, f"{when} AT PAPPI", "A real photo goes here")
        pil.save(os.path.join(OUT, name + ".jpg"), quality=80, optimize=True, progressive=True)


def era_photos(W=900, H=675):
    looks = [("ERA ONE", (120, 90, 50), (200, 170, 120), 1), ("ERA TWO", (40, 30, 50), (230, 120, 80), 2),
             ("ERA THREE", NIGHT, (95, 50, 40), 3)]
    for i, (big, top, bottom, seed) in enumerate(looks):
        pil = scene(W, H, top, bottom, None, 18, 12, 40 + i, big, "An old photo goes here", chip_text="SAMPLE OLD PHOTO")
        if i == 0:  # faded print
            arr = np.asarray(pil).astype(np.float32)
            grey = arr.mean(axis=2, keepdims=True)
            arr = grey * np.array([1.08, 0.95, 0.78]) * 0.9 + 25
            pil = to_pil(arr)
        if i == 1:  # old video tape look
            arr = np.asarray(pil).astype(np.float32)
            arr[::3] *= 0.75
            pil = to_pil(arr)
        pil.save(os.path.join(OUT, f"era-{i + 1}.jpg"), quality=78, optimize=True, progressive=True)


def family(n_people=4, n_dogs=2, S=480):
    cols = [CLAY, GREEN, MANGO, SEA, (120, 90, 70), (255, 150, 60)]
    for i in range(n_people + n_dogs):
        col = cols[i % len(cols)]
        pil = Image.new("RGB", (S, S), col)
        d = ImageDraw.Draw(pil)
        if i < n_people:
            d.ellipse([S * 0.36, S * 0.2, S * 0.64, S * 0.48], fill=PAPER)
            d.rounded_rectangle([S * 0.22, S * 0.56, S * 0.78, S * 1.1], radius=S * 0.14, fill=PAPER)
            text = f"STAFF {i + 1}"
        else:
            d.ellipse([S * 0.3, S * 0.28, S * 0.7, S * 0.68], fill=PAPER)  # head
            d.ellipse([S * 0.22, S * 0.24, S * 0.38, S * 0.54], fill=PAPER)  # ears
            d.ellipse([S * 0.62, S * 0.24, S * 0.78, S * 0.54], fill=PAPER)
            d.ellipse([S * 0.44, S * 0.48, S * 0.56, S * 0.58], fill=col)  # nose
            text = f"DOG {i - n_people + 1}"
        label(pil, text, "", 0.86, big_size=S * 0.09)
        pil.save(os.path.join(OUT, f"family-{i + 1}.jpg"), quality=80, optimize=True)


def og(W=1200, H=630):
    L = make_lights(W, H, 16, 9, [WARM, AMBER, MANGO, PAPER])
    img = gradient(W, H, NIGHT, (70, 38, 28))
    for (x0, y0, _vx, r, col, _ph) in L:
        glow(img, x0, y0, r, col, 0.8)
    pil = to_pil(img)
    d = ImageDraw.Draw(pil)
    f1, f2 = font(96, "BoldItalic"), font(40)
    for text, f, y, col in [("PAPPI CHULO", f1, 190, PAPER), ("Come alone. Leave with a crew.", f2, 330, PAPER),
                            ("Vagator, North Goa", font(30), 400, MANGO)]:
        tw = d.textlength(text, font=f)
        d.text(((W - tw) / 2, y), text, font=f, fill=col, stroke_width=4, stroke_fill=INK)
    pil.save(os.path.join(OUT, "og.jpg"), quality=82, optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    day_photos()
    era_photos()
    family()
    og()
    print("photos done", flush=True)
    for i in range(6):
        story(i)
        print(f"story {i + 1} done", flush=True)
    hero("hero-phone", 720, 1280)
    print("hero phone done", flush=True)
    hero("hero-laptop", 1280, 720)
    print("hero laptop done", flush=True)


if __name__ == "__main__":
    main()
