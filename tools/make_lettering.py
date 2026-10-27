"""Makes the puffy graffiti headline words for the home page, in the style of the art on Pappi's walls.

Each letter is cut from a chunky font, inflated like a balloon with a height map, lit with a glossy
white highlight, wrapped in a thick black outline, given a drip or two, and dropped on a soft
ground shadow. Letters tilt and bounce a little and overlap, the way hand painted graffiti does.
Output: PNG files with a transparent background in media/words/, two sizes each (phone and laptop).

Run:  FONT_DIR=/path/to/ttf/folder python3 tools/make_lettering.py [--sheet]
  --sheet also writes a contact sheet for a quick look.
"""
import math
import os
import random
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "media", "words")
FONT_DIR = os.environ.get("FONT_DIR", os.path.join(HERE, "..", "fonts"))

# Brand book colours (from the walls).
C = {
    "pink": (255, 79, 154),
    "blue": (47, 180, 240),
    "green": (143, 209, 79),
    "orange": (255, 138, 31),
    "purple": (139, 92, 246),
    "yellow": (255, 210, 63),
    "white": (250, 247, 240),
}
INK = (17, 17, 17)

# The words, one entry per headline. lines: list of lines; colours: one per word, in order; font: file name.
WORDS = [
    {"name": "nobody-leaves-alone", "lines": ["NOBODY", "LEAVES", "ALONE"], "colours": ["pink", "blue", "yellow"], "font": "LuckiestGuy.ttf"},
    {"name": "they-said-it", "lines": ["THEY SAID IT", "NOT US"], "colours": ["blue", "blue", "blue", "pink", "pink"], "font": "LuckiestGuy.ttf"},
    {"name": "tonight", "lines": ["TONIGHT"], "colours": ["purple"], "font": "LuckiestGuy.ttf"},
    {"name": "repeat-the-process", "lines": ["REPEAT", "THE PROCESS"], "colours": ["orange", "yellow", "green"], "font": "LuckiestGuy.ttf"},
    {"name": "book-direct", "lines": ["BOOK", "DIRECT"], "colours": ["pink", "orange"], "font": "LuckiestGuy.ttf"},
    {"name": "pappi-chulo", "lines": ["PAPPI", "CHULO"], "colours": ["blue", "pink"], "font": "LuckiestGuy.ttf"},
]

SIZE = 520          # letter height in pixels at full size
OUTLINE = 0.055     # outline thickness as a share of letter size
PUFF = 0.42         # how round the inflation is, as a share of the stroke width
OVERLAP = 0.06      # how much each letter overlaps the one before


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def letter_image(ch, font, rng):
    """One letter as a mask, tilted and scaled a little, plus its advance width."""
    pad = int(SIZE * 0.5)
    bbox = font.getbbox(ch, anchor="ls")
    w = bbox[2] - bbox[0]
    img = Image.new("L", (w + 2 * pad, SIZE + 2 * pad), 0)
    d = ImageDraw.Draw(img)
    d.text((pad - bbox[0], pad + SIZE), ch, font=font, fill=255, anchor="ls")
    scale = rng.uniform(0.94, 1.08)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    img = img.rotate(rng.uniform(-7, 7), resample=Image.BICUBIC, expand=False)
    return img, w * scale


def add_drips(mask, rng, n):
    """Hang a few drips off the bottom edge of a letter."""
    ys, xs = np.nonzero(mask > 127)
    if len(xs) == 0:
        return mask
    out = mask.copy()
    stroke = max(10, int(SIZE * 0.08))
    for _ in range(n):
        x = int(rng.choice(xs))
        col = np.nonzero(mask[:, x] > 127)[0]
        if len(col) == 0:
            continue
        y0 = int(col.max())
        w = int(stroke * rng.uniform(0.9, 1.3))
        length = int(SIZE * rng.uniform(0.12, 0.3))
        cv2.rectangle(out, (x - w // 2, y0 - w), (x + w // 2, y0 + length), 255, -1)
        cv2.circle(out, (x, y0 + length), int(w * 0.7), 255, -1)
    return out


def puff(mask, colour, light):
    """Inflate a mask and light it. Returns an RGBA float image (0 to 1) of the fill only."""
    m = (mask > 127).astype(np.uint8)
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    r = max(6.0, float(dist.max()) * 1.05)
    t = np.clip(dist / r, 0, 1)
    h = np.sqrt(1 - (1 - t) ** 2)                           # dome: steep at the edge, flat on top
    h = cv2.GaussianBlur(h.astype(np.float32), (0, 0), max(1, SIZE * 0.018))
    gy, gx = np.gradient(h * r * 0.9)
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.array(light, dtype=np.float32); L /= np.linalg.norm(L)
    V = np.array([0, 0, 1], dtype=np.float32)
    H = L + V; H /= np.linalg.norm(H)
    diff = np.clip(n @ L, 0, 1)
    spec = np.clip(n @ H, 0, 1) ** 36
    shine = smoothstep(0.22, 0.6, cv2.GaussianBlur(spec.astype(np.float32), (0, 0), max(1, SIZE * 0.01)))                      # crisp white blob, like the art
    rim = 0.72 + 0.28 * smoothstep(0, 0.35, t)                 # dark inner edge
    base = np.array(colour, dtype=np.float32) / 255
    dark = base * 0.55
    rgb = dark + (base - dark) * (0.45 + 0.55 * diff)[..., None]
    rgb *= rim[..., None]
    rgb = rgb + (1 - rgb) * shine[..., None] * 0.95
    # a faint second light from the lower right, the way glossy plastic bounces light
    L2 = np.array([0.5, 0.6, 0.35], dtype=np.float32); L2 /= np.linalg.norm(L2)
    rgb += (np.clip(n @ L2, 0, 1) ** 6 * 0.18)[..., None] * (base + 0.3)
    rgb = np.clip(rgb, 0, 1)
    alpha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)
    return np.dstack([rgb, alpha])


def over(dst, src):
    a = src[..., 3:4]
    dst[..., :3] = src[..., :3] * a + dst[..., :3] * (1 - a)
    dst[..., 3:4] = a + dst[..., 3:4] * (1 - a)


def render(word, seed=7):
    rng = random.Random(seed)
    nrng = np.random.default_rng(seed)
    font = ImageFont.truetype(os.path.join(FONT_DIR, word["font"]), SIZE)
    colours = list(word["colours"])
    outline = int(SIZE * OUTLINE)
    wi = 0
    line_gap = int(SIZE * 1.18)
    # place every letter first, then draw them back to front so each outline sits on the next letter
    placed = []   # (x, y, mask, colour)
    width = 0
    for li, line in enumerate(word["lines"]):
        x = 0
        y = li * line_gap
        if li:
            wi += 1
        for ch in line:
            if ch == " ":
                x += int(SIZE * 0.28)
                wi += 1
                continue
            img, adv = letter_image(ch, font, rng)
            m = np.array(img)
            if rng.random() < 0.2:
                m = add_drips(m, rng, 1)
            bounce = int(math.sin(len(placed) * 1.3) * SIZE * 0.05 + rng.uniform(-1, 1) * SIZE * 0.03)
            placed.append((x, y + bounce, m, C[colours[min(wi, len(colours) - 1)]]))
            x += int(adv * (1 - OVERLAP))
        width = max(width, x)
    pad = int(SIZE * 0.6)
    Wc = width + 2 * pad + int(SIZE * 1.2)
    Hc = line_gap * len(word["lines"]) + 2 * pad + int(SIZE * 1.4)
    canvas = np.zeros((Hc, Wc, 4), dtype=np.float32)
    full = np.zeros((Hc, Wc), dtype=np.uint8)
    light = (-0.45, -0.75, 0.55)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * outline + 1, 2 * outline + 1))
    for (x, y, m, colour) in reversed(placed):
        H, W = m.shape
        x, y = x + pad, y + pad
        edge = cv2.dilate(m, k)
        layer = np.zeros((H, W, 4), dtype=np.float32)
        layer[..., :3] = np.array(INK, dtype=np.float32) / 255
        layer[..., 3] = cv2.GaussianBlur((edge > 127).astype(np.float32), (0, 0), 0.9)
        fill = puff(m, colour, light)
        y0, x0 = max(0, y), max(0, x)
        y1, x1 = min(Hc, y + H), min(Wc, x + W)
        view = canvas[y0:y1, x0:x1]
        over(view, layer[y0 - y:y1 - y, x0 - x:x1 - x])
        over(view, fill[y0 - y:y1 - y, x0 - x:x1 - x])
        full[y0:y1, x0:x1] = np.maximum(full[y0:y1, x0:x1], edge[y0 - y:y1 - y, x0 - x:x1 - x])
    # ground shadow under the whole word
    sh = cv2.GaussianBlur((full > 127).astype(np.float32), (0, 0), SIZE * 0.05)
    sh = np.roll(sh, (int(SIZE * 0.07), int(SIZE * 0.05)), axis=(0, 1)) * 0.38
    out = np.zeros_like(canvas)
    out[..., :3] = 0.05
    out[..., 3] = sh
    over(out, canvas)
    # trim
    ys, xs = np.nonzero(out[..., 3] > 0.01)
    out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA")


def main():
    os.makedirs(OUT, exist_ok=True)
    sheet = []
    for i, w in enumerate(WORDS):
        im = render(w, seed=11 + i)
        im.save(os.path.join(OUT, f"{w['name']}.png"), optimize=True)
        small = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
        small.save(os.path.join(OUT, f"{w['name']}-phone.png"), optimize=True)
        sheet.append(im)
        print(w["name"], im.size)
    if "--sheet" in sys.argv:
        W = max(s.width for s in sheet) + 120
        H = sum(s.height for s in sheet) + 60 * (len(sheet) + 1)
        page = Image.new("RGB", (W, H), (250, 247, 240))
        y = 60
        for s in sheet:
            page.paste(s, (60, y), s)
            y += s.height + 60
        page.thumbnail((2000, 4000))
        page.save(os.path.join(OUT, "sheet.jpg"), quality=86)


if __name__ == "__main__":
    main()
