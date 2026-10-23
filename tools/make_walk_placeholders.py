#!/usr/bin/env python3
"""Make placeholder 360 photos and clips for the Pappi test walk.

It draws a small fake Pappi courtyard (gate, bar under a mango tree,
graffiti walls, dance floor, DJ booth) and saves it the same way a real
360 camera does: one 2:1 "equirectangular" picture that wraps all the way
around. Real footage replaces these files later, with the same file names.

Run:  python3 tools/make_walk_placeholders.py            (everything)
      python3 tools/make_walk_placeholders.py preview    (quick small test pictures)
Needs: numpy, Pillow, opencv-python, ffmpeg, the Poppins font (set FONT_DIR if it is not in the folder below).
"""
import math
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "walk", "media")
FONT_DIR = os.environ.get("FONT_DIR", "/usr/share/fonts/truetype/google-fonts")
FONT_BOLD = os.path.join(FONT_DIR, "Poppins-BoldItalic.ttf")
FONT_PLAIN = os.path.join(FONT_DIR, "Poppins-Bold.ttf")
F = np.float32
EPS = 2e-3
PPM = 150  # texture pixels per metre

# Stops along the walk (camera at eye height 1.6 m). Walk goes along +z.
# Walking in (facing +z), +x is on your LEFT and -x on your right. The real
# bar is on the left as you come in from the main gate, so the bar side is +x.
STOPS = {"gate": (0.0, 1.6, -2.2), "bar": (0.0, 1.6, 7.0), "floor": (0.0, 1.6, 14.4)}
FPS = 24

PAINT = [(236, 38, 143), (0, 196, 222), (255, 210, 0), (255, 112, 24), (128, 224, 40),
         (150, 64, 232), (28, 96, 232), (250, 250, 245), (255, 80, 80)]
INK = (24, 16, 34)


# ----------------------------------------------------------------- textures
def _font(path, size):
    return ImageFont.truetype(path, max(8, int(size)))


def _to_linear(img, mask):
    arr = (np.asarray(img).astype(F) / 255.0) ** 2.2
    m = np.asarray(mask).astype(F) / 255.0
    return np.dstack([arr, m]).astype(F)


def wall_tex(w_m, h_m, seed, words, base, backbar=None):
    """Graffiti wall. Alpha channel: 0.5 = paint (glows a bit under UV), 1.0 = neon."""
    W, H = int(w_m * PPM), int(h_m * PPM)
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (W, H), base)
    msk = Image.new("L", (W, H), 0)
    d, dm = ImageDraw.Draw(img), ImageDraw.Draw(msk)
    lw = int(0.045 * PPM)
    x = 0
    while x < W:
        x1 = min(W, x + int(rng.uniform(2.0, 4.0) * PPM))
        kind = int(rng.integers(0, 5))
        c1 = PAINT[int(rng.integers(len(PAINT)))]
        if kind == 0:  # colour field with a wavy top
            top = H * rng.uniform(0.25, 0.55)
            ph = rng.uniform(0, 6)
            pts = [(x, H)] + [(xx, top + 0.14 * PPM * math.sin(xx / (0.45 * PPM) + ph))
                              for xx in range(x, x1 + 1, 6)] + [(x1, H)]
            d.polygon(pts, fill=c1)
            dm.polygon(pts, fill=128)
            d.line(pts[1:-1], fill=INK, width=lw)
        elif kind == 1:  # suns and circles
            for _ in range(int(rng.integers(2, 5))):
                r = rng.uniform(0.25, 0.75) * PPM
                cx, cy = rng.uniform(x, x1), rng.uniform(0.25, 0.8) * H
                col = PAINT[int(rng.integers(len(PAINT)))]
                box = [cx - r, cy - r, cx + r, cy + r]
                d.ellipse(box, fill=col, outline=INK, width=lw)
                dm.ellipse(box, fill=128)
        elif kind == 2:  # waves
            for k in range(4):
                col = PAINT[int(rng.integers(len(PAINT)))]
                y0 = H * (0.35 + 0.13 * k)
                pts = [(xx, y0 + 0.1 * PPM * math.sin(xx / (0.3 * PPM) + k)) for xx in range(x, x1 + 1, 5)]
                d.line(pts, fill=col, width=int(0.09 * PPM))
                dm.line(pts, fill=128, width=int(0.09 * PPM))
        elif kind == 3:  # third eye
            cx, cy = (x + x1) / 2, H * rng.uniform(0.4, 0.6)
            rw, rh = 0.9 * PPM, 0.45 * PPM
            d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(250, 248, 240), outline=INK, width=lw)
            col = PAINT[int(rng.integers(len(PAINT)))]
            r = 0.36 * PPM
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=INK, width=lw)
            r2 = 0.15 * PPM
            d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=INK)
            dm.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=128)
            for a in range(0, 360, 30):  # lashes / rays
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                d.line([(cx + ca * rw * 1.08, cy + sa * rh * 1.15), (cx + ca * rw * 1.35, cy + sa * rh * 1.6)],
                       fill=col, width=int(0.05 * PPM))
        else:  # zigzag band
            col = PAINT[int(rng.integers(len(PAINT)))]
            y0, amp, step = H * rng.uniform(0.55, 0.8), 0.18 * PPM, int(0.3 * PPM)
            pts = [(xx, y0 + (amp if (i % 2) else -amp)) for i, xx in enumerate(range(x, x1 + step, step))]
            d.line(pts, fill=col, width=int(0.12 * PPM), joint="curve")
            dm.line(pts, fill=128, width=int(0.12 * PPM))
        x = x1
    for i, word in enumerate(words):
        f = _font(FONT_BOLD, rng.uniform(0.7, 0.95) * PPM)
        tw = d.textlength(word, font=f)
        wx = (i + 0.5) * W / len(words) - tw / 2 + rng.uniform(-0.4, 0.4) * PPM
        wy = rng.uniform(0.08, 0.3) * H
        col = PAINT[int(rng.integers(len(PAINT)))]
        d.text((wx, wy), word, font=f, fill=col, stroke_width=int(0.06 * PPM), stroke_fill=INK)
        dm.text((wx, wy), word, font=f, fill=128, stroke_width=int(0.06 * PPM), stroke_fill=128)
    if backbar:  # shelves of bottles behind the bar, with a neon sign
        u0, u1 = int(backbar[0] * PPM), int(backbar[1] * PPM)
        def row(y_m):
            return int((h_m - y_m) * PPM)
        d.rectangle([u0, row(2.75), u1, row(0.9)], fill=(58, 34, 22))
        dm.rectangle([u0, row(2.75), u1, row(0.9)], fill=0)
        for shelf in (1.25, 1.7, 2.15):
            d.rectangle([u0, row(shelf), u1, row(shelf - 0.04)], fill=(150, 100, 60))
            bx = u0 + int(0.08 * PPM)
            while bx < u1 - int(0.12 * PPM):
                hb = rng.uniform(0.2, 0.32)
                col = [(70, 140, 60), (200, 120, 30), (180, 210, 230), (120, 40, 40), (230, 200, 120)][int(rng.integers(5))]
                d.rectangle([bx, row(shelf + hb), bx + int(0.07 * PPM), row(shelf)], fill=col)
                d.rectangle([bx + int(0.02 * PPM), row(shelf + hb + 0.07), bx + int(0.05 * PPM), row(shelf + hb)], fill=col)
                bx += int(rng.uniform(0.11, 0.16) * PPM)
        f = _font(FONT_BOLD, 0.34 * PPM)
        text = "PAPPI BAR"
        tw = d.textlength(text, font=f)
        tx = (u0 + u1) / 2 - tw / 2
        d.text((tx, row(2.7)), text, font=f, fill=(90, 245, 255))
        dm.text((tx, row(2.7)), text, font=f, fill=255)
    arr = _to_linear(img, msk)
    yy = np.linspace(0, 1, H, dtype=F)[:, None]
    arr[..., :3] *= (0.78 + 0.22 * np.clip((1 - yy) * 1.4, 0, 1))[..., None]  # grime near the floor
    return arr


def board_tex(w_m, h_m, bg, text, color, size, sub=None, stripes=None):
    W, H = int(w_m * PPM * 2), int(h_m * PPM * 2)
    img = Image.new("RGB", (W, H), bg)
    msk = Image.new("L", (W, H), 0)
    d, dm = ImageDraw.Draw(img), ImageDraw.Draw(msk)
    if stripes:
        for k, col in enumerate(stripes):
            y = int(H * (0.78 + 0.07 * k))
            d.rectangle([0, y, W, y + int(H * 0.04)], fill=col)
            dm.rectangle([0, y, W, y + int(H * 0.04)], fill=128)
    f = _font(FONT_BOLD, size * PPM * 2)
    tw = d.textlength(text, font=f)
    ty = H * (0.08 if sub else 0.18)
    d.text(((W - tw) / 2, ty), text, font=f, fill=color, stroke_width=int(0.012 * PPM * 2), stroke_fill=(255, 255, 255))
    dm.text(((W - tw) / 2, ty), text, font=f, fill=255, stroke_width=int(0.012 * PPM * 2), stroke_fill=255)
    if sub:
        f2 = _font(FONT_PLAIN, size * 0.32 * PPM * 2)
        tw2 = d.textlength(sub, font=f2)
        d.text(((W - tw2) / 2, H * 0.68), sub, font=f2, fill=(255, 220, 120))
        dm.text(((W - tw2) / 2, H * 0.68), sub, font=f2, fill=255)
    return _to_linear(img, msk)


def bar_front_tex():
    W, H = int(4.0 * PPM), int(1.1 * PPM)
    img = Image.new("RGB", (W, H), (120, 70, 40))
    msk = Image.new("L", (W, H), 0)
    d, dm = ImageDraw.Draw(img), ImageDraw.Draw(msk)
    for k in range(0, W, int(0.18 * PPM)):  # planks
        d.line([(k, 0), (k, H)], fill=(80, 45, 25), width=3)
    f = _font(FONT_BOLD, 0.55 * PPM)
    tw = d.textlength("BAR", font=f)
    d.text(((W - tw) / 2, H * 0.22), "BAR", font=f, fill=(255, 210, 0), stroke_width=4, stroke_fill=INK)
    dm.text(((W - tw) / 2, H * 0.22), "BAR", font=f, fill=128, stroke_width=4, stroke_fill=128)
    d.rectangle([0, 0, W, int(0.05 * PPM)], fill=(90, 245, 255))  # neon strip
    dm.rectangle([0, 0, W, int(0.05 * PPM)], fill=255)
    return _to_linear(img, msk)


TEX = {}


def build_textures():
    if TEX:
        return TEX
    TEX["left"] = wall_tex(22, 3, 11, ["PAPPI", "LOVE", "GOA"], (236, 226, 206), backbar=(5.0, 10.0))
    TEX["right"] = wall_tex(22, 3, 23, ["VAGATOR", "CHULO", "VIBES"], (232, 214, 190))
    TEX["back"] = wall_tex(14.6, 3, 37, ["PAPPI", "CHULO"], (226, 222, 232))
    TEX["front"] = wall_tex(14.6, 3, 41, ["COME", "BACK"], (238, 230, 214))
    TEX["sign"] = board_tex(4.4, 0.8, (26, 18, 44), "PAPPI CHULO", (255, 58, 170), 0.42, sub="VAGATOR  GOA")
    TEX["dj"] = board_tex(3.2, 1.15, (18, 18, 24), "PAPPI CHULO", (170, 80, 255), 0.36,
                          stripes=[(255, 58, 170), (0, 196, 222)])
    TEX["barfront"] = bar_front_tex()
    return TEX


def sample(tex, u, v):
    """Bilinear sample of a texture (H, W, 4) at u, v in [0, 1]. Image top is v = 0."""
    H, W = tex.shape[:2]
    x = np.clip(u, 0, 1) * (W - 1)
    y = np.clip(v, 0, 1) * (H - 1)
    x0 = np.floor(x).astype(np.int32)
    y0 = np.floor(y).astype(np.int32)
    x1 = np.minimum(x0 + 1, W - 1)
    y1 = np.minimum(y0 + 1, H - 1)
    fx = (x - x0)[:, None]
    fy = (y - y0)[:, None]
    a = tex[y0, x0] * (1 - fx) + tex[y0, x1] * fx
    b = tex[y1, x0] * (1 - fx) + tex[y1, x1] * fx
    return a * (1 - fy) + b * fy


# ------------------------------------------------------------------- scene
# material ids
GROUND, WALL, PILLAR, SIGN, BAR, TRUNK, LEAF, TABLE, PINGPONG, DJ, SPEAKER, SHIRT, SKIN, DOG, BUILDING, CUSHION = range(1, 17)


class Prims:
    def __init__(self):
        self.box = []  # (min, max, mat, color, tag, shadow)
        self.sph = []  # (center, r, mat, color, shadow)
        self.cyl = []  # (cx, cz, r, y0, y1, mat, color, shadow)

    def add_box(self, mn, mx, mat, col=(1, 1, 1), tag="", shadow=True):
        self.box.append((np.array(mn, F), np.array(mx, F), mat, np.array(col, F), tag, shadow))

    def add_sph(self, c, r, mat, col=(1, 1, 1), shadow=True):
        self.sph.append((np.array(c, F), F(r), mat, np.array(col, F), shadow))

    def add_cyl(self, cx, cz, r, y0, y1, mat, col=(1, 1, 1), shadow=True):
        self.cyl.append((F(cx), F(cz), F(r), F(y0), F(y1), mat, np.array(col, F), shadow))

    def bounds(self):
        """Bounding spheres for every primitive (used to skip far-off work)."""
        out = []
        for i, (mn, mx, *_rest) in enumerate(self.box):
            out.append(("b", i, (mn + mx) / 2, float(np.linalg.norm(mx - mn) / 2)))
        for i, (c, r, *_rest) in enumerate(self.sph):
            out.append(("s", i, c, float(r)))
        for i, (cx, cz, r, y0, y1, *_rest) in enumerate(self.cyl):
            c = np.array([cx, (y0 + y1) / 2, cz], F)
            out.append(("c", i, c, float(math.hypot(r, (y1 - y0) / 2))))
        return out


def srgb(c):
    return tuple((np.array(c, F) / 255.0) ** 2.2)


SHIRTS = [srgb(c) for c in [(230, 40, 60), (250, 250, 250), (20, 20, 24), (40, 120, 230), (255, 200, 0),
                            (240, 100, 180), (30, 170, 120), (255, 120, 30), (120, 60, 200), (200, 200, 190)]]
SKINS = [srgb(c) for c in [(198, 140, 100), (150, 100, 70), (235, 190, 160), (110, 75, 55), (220, 170, 130)]]


def people(mode, t):
    """Where people stand (and how they move) at time t seconds."""
    rng = np.random.default_rng(7 if mode == "night" else 3)
    out = []  # (x, z, height, shirt, skin, y_offset)
    if mode == "night":
        for k in range(26):  # dancers
            x = rng.uniform(-2.9, 2.9)
            z = rng.uniform(15.7, 20.1)
            ph = rng.uniform(0, 1)
            h = rng.uniform(1.58, 1.86)
            bob = 0.06 * abs(math.sin(2 * math.pi * (2.0 * t + ph)))  # 120 bpm
            sway = 0.05 * math.sin(2 * math.pi * (1.0 * t + ph))
            out.append((x + sway, z, h, k, int(rng.integers(5)), bob))
        for k in range(6):  # at the bar
            out.append((2.75 + rng.uniform(0, 0.25), 5.9 + k * 0.62, rng.uniform(1.6, 1.85), k + 3, int(rng.integers(5)), 0.0))
        for k, (x, z) in enumerate([(-2.2, 4.4), (-2.8, 4.9), (-4.6, 10.5), (-5.0, 11.1), (-5.7, 10.4),
                                    (4.2, 12.2), (4.8, 12.6), (-3.2, 12.8), (1.6, 1.4), (-1.6, 1.8)]):
            sway = 0.03 * math.sin(2 * math.pi * (t / 3.0 + k * 0.1))
            out.append((x + sway, z, rng.uniform(1.6, 1.84), k + 1, int(rng.integers(5)), 0.0))
    else:
        for k, (x, z, h) in enumerate([(-2.0, 4.3, 1.15), (-2.9, 4.1, 1.12), (-4.9, 9.6, 1.12),
                                       (2.9, 7.1, 1.75), (2.85, 8.3, 1.68), (-4.3, 1.9, 1.72), (-6.1, 3.6, 1.66)]):
            out.append((x, z, h, k + 2, int(rng.integers(5)), 0.0))
    return out


def build_scene(mode, t):
    P = Prims()
    wall_h = 3.0
    # courtyard walls (x -7..7, z 0..22)
    P.add_box((7.0, 0, 0), (7.3, wall_h, 22), WALL, tag="left")
    P.add_box((-7.3, 0, 0), (-7.0, wall_h, 22), WALL, tag="right")
    P.add_box((-7.3, 0, 22), (7.3, wall_h, 22.3), WALL, tag="back")
    P.add_box((-7.3, 0, 0), (-1.6, 2.6, 0.3), WALL, tag="front")
    P.add_box((1.6, 0, 0), (7.3, 2.6, 0.3), WALL, tag="front")
    # gate pillars and sign
    P.add_box((-1.95, 0, -0.15), (-1.55, 3.7, 0.4), PILLAR, srgb((178, 82, 52)))
    P.add_box((1.55, 0, -0.15), (1.95, 3.7, 0.4), PILLAR, srgb((178, 82, 52)))
    P.add_box((-2.2, 3.0, -0.12), (2.2, 3.8, 0.22), SIGN, tag="sign")
    # hostel buildings behind the walls
    P.add_box((-14, 0, 3), (-7.3, 6.6, 17), BUILDING, srgb((236, 184, 96)), tag="bright")
    P.add_box((7.3, 0, 11), (14, 5.2, 21), BUILDING, srgb((96, 178, 170)), tag="bleft")
    # bar counter on the left
    P.add_box((3.2, 0, 5.5), (6.0, 1.1, 9.5), BAR, srgb((120, 70, 40)), tag="bar")
    # mango tree on the right
    P.add_cyl(-3.6, 8.0, 0.42, 0, 3.6, TRUNK, srgb((92, 62, 40)))
    P.add_cyl(-3.0, 8.4, 0.22, 2.2, 4.4, TRUNK, srgb((92, 62, 40)))
    for c, r in [((-3.6, 5.3, 8.0), 2.7), ((-1.9, 4.8, 9.1), 2.0), ((-5.2, 4.6, 6.9), 2.1),
                 ((-3.9, 4.4, 10.3), 1.9), ((-2.4, 5.6, 6.6), 1.7)]:
        P.add_sph(c, r, LEAF, srgb((52, 104, 40)))
    # seating under the tree, ping pong near the gate
    P.add_box((-3.4, 0, 3.6), (-1.4, 0.42, 5.2), CUSHION, srgb((220, 70, 60)))
    P.add_box((-5.8, 0, 8.9), (-4.3, 0.45, 10.4), CUSHION, srgb((40, 150, 200)))
    P.add_box((-6.4, 0.72, 1.8), (-4.0, 0.78, 3.2), PINGPONG, srgb((30, 120, 70)))
    P.add_box((-5.5, 0, 2.3), (-4.9, 0.72, 2.7), TABLE, srgb((40, 40, 40)), shadow=False)
    # dance floor end: DJ booth and speakers
    P.add_box((-1.6, 0, 20.6), (1.6, 1.15, 21.4), DJ, tag="dj")
    P.add_box((-3.2, 0, 20.5), (-2.3, 1.9, 21.4), SPEAKER, srgb((22, 22, 26)))
    P.add_box((2.3, 0, 20.5), (3.2, 1.9, 21.4), SPEAKER, srgb((22, 22, 26)))
    # palms outside and a treeline on the horizon
    for (x, z, h) in [(10, -6, 8.5), (-9, -8, 9.5), (11, 4, 9.0), (-12, 21, 8.0), (3, 27, 9.2), (-5, 28, 8.4)]:
        P.add_cyl(x, z, 0.2, 0, h, TRUNK, srgb((120, 100, 80)))
        for a in range(5):
            ang = a * 2 * math.pi / 5
            P.add_sph((x + 1.0 * math.cos(ang), h - 0.2, z + 1.0 * math.sin(ang)), 1.0, LEAF, srgb((60, 120, 50)))
    for a in range(14):
        ang = a * 2 * math.pi / 14
        P.add_sph((36 * math.cos(ang), 1.5, 10 + 36 * math.sin(ang)), 8.0, LEAF, srgb((40, 82, 36)), shadow=False)
    # dogs (day)
    if mode == "day":
        for (x, z, col) in [(1.2, 2.2, (196, 150, 100)), (-1.4, -1.0, (40, 32, 28))]:
            P.add_sph((x, 0.26, z), 0.28, DOG, srgb(col))
            P.add_sph((x - 0.3, 0.36, z + 0.12), 0.15, DOG, srgb(col))
    # people
    for (x, z, h, shirt, skin, yo) in people(mode, t):
        P.add_cyl(x, z, 0.2, yo, yo + h - 0.24, SHIRT, SHIRTS[shirt % len(SHIRTS)])
        P.add_sph((x, yo + h - 0.13, z), 0.13, SKIN, SKINS[skin])
    return P


def string_lights(mode):
    """Points (and colours) of the string lights across the courtyard."""
    pts, cols = [], []
    warm = np.array([1.0, 0.72, 0.38], F)
    rows = [2.6, 6.2, 9.8, 13.0, 16.2, 18.8]
    for zi, z in enumerate(rows):
        n = 26
        for k in range(n + 1):
            x = -7 + 14 * k / n
            y = 3.05 - 0.5 * (1 - (x / 7) ** 2)
            pts.append((x, y, z))
            if z > 15:
                cols.append(np.array([[1, .2, .7], [.2, .8, 1], [.6, .3, 1], [1, .85, .2]][k % 4], F))
            else:
                cols.append(warm)
    return np.array(pts, F), np.array(cols, F)


def lights(mode, t):
    if mode == "day":
        return []
    beat = 0.65 + 0.35 * abs(math.cos(2 * math.pi * 2.0 * t))
    swap = 0.5 + 0.5 * math.sin(2 * math.pi * t / 3.0)
    L = [
        ((5.0, 2.8, 17.5), (0.55, 0.2, 1.0), 9 * beat),
        ((-5.0, 2.8, 17.5), (1.0, 0.15, 0.6), 9 * (1.2 - beat * 0.5)),
        ((0.0, 3.3, 21.0), (0.1, 0.75 + 0.2 * swap, 1.0), 7 * beat),
        ((4.6, 2.6, 7.5), (1.0, 0.62, 0.28), 4.5),
        ((0.0, 3.2, -0.9), (1.0, 0.7, 0.35), 5),
        ((4.0, 4.6, -6.0), (1.0, 0.55, 0.2), 6),
        ((-2.5, 3.0, 4.5), (1.0, 0.72, 0.4), 2.2),
        ((-3.0, 3.0, 11.5), (1.0, 0.72, 0.4), 2.2),
        ((3.5, 3.0, 12.5), (1.0, 0.72, 0.4), 2.0),
    ]
    return [(np.array(p, F), np.array(c, F), F(i)) for p, c, i in L]


# ----------------------------------------------------------------- tracing
def trace(O, D, P, cand=None, shadow=False, tmax=None):
    """Closest hit of rays O + t*D. Returns t, kind (0 sky, 1 ground, 2 box, 3 sphere, 4 cylinder), index.
    With shadow=True, returns a bool array: hit anything that casts shadows closer than tmax."""
    n = D.shape[0]
    Ob = np.broadcast_to(O, D.shape)
    best = np.full(n, np.inf, F) if not shadow else None
    kind = np.zeros(n, np.int8)
    idx = np.zeros(n, np.int16)
    blocked = np.zeros(n, bool) if shadow else None
    with np.errstate(divide="ignore", invalid="ignore"):
        invD = 1.0 / np.where(np.abs(D) < 1e-9, 1e-9, D)

        def take(t, k, i):
            nonlocal best
            if shadow:
                np.logical_or(blocked, (t > EPS) & (t < tmax), out=blocked)
                return
            m = (t > EPS) & (t < best)
            best = np.where(m, t, best)
            kind[m] = k
            idx[m] = i

        if not shadow:
            tg = np.where(D[:, 1] < -1e-6, -Ob[:, 1] * invD[:, 1], np.inf).astype(F)
            take(tg, 1, 0)
        boxes = range(len(P.box)) if cand is None else cand["b"]
        for i in boxes:
            mn, mx, _m, _c, _tag, sh = P.box[i]
            if shadow and not sh:
                continue
            t1 = (mn - Ob) * invD
            t2 = (mx - Ob) * invD
            tn = np.minimum(t1, t2).max(axis=1)
            tf = np.maximum(t1, t2).min(axis=1)
            t = np.where((tf >= tn) & (tf > EPS), np.where(tn > EPS, tn, tf), np.inf)
            take(t, 2, i)
        sphs = range(len(P.sph)) if cand is None else cand["s"]
        for i in sphs:
            c, r, _m, _c, sh = P.sph[i]
            if shadow and not sh:
                continue
            oc = Ob - c
            b = np.einsum("ij,ij->i", oc, D)
            cc = np.einsum("ij,ij->i", oc, oc) - r * r
            disc = b * b - cc
            sq = np.sqrt(np.maximum(disc, 0))
            t = np.where(disc > 0, -b - sq, np.inf)
            take(t, 3, i)
        cyls = range(len(P.cyl)) if cand is None else cand["c"]
        for i in cyls:
            cx, cz, r, y0, y1, _m, _c, sh = P.cyl[i]
            if shadow and not sh:
                continue
            ox = Ob[:, 0] - cx
            oz = Ob[:, 2] - cz
            a = D[:, 0] ** 2 + D[:, 2] ** 2
            b = ox * D[:, 0] + oz * D[:, 2]
            cc = ox * ox + oz * oz - r * r
            disc = b * b - a * cc
            t = (-b - np.sqrt(np.maximum(disc, 0))) / np.maximum(a, 1e-9)
            y = Ob[:, 1] + t * D[:, 1]
            t = np.where((disc > 0) & (y >= y0) & (y <= y1), t, np.inf)
            take(t, 4, i)
    if shadow:
        return blocked
    return best, kind, idx


def candidates(P, bounds, O, lat0, lat1, lon0, lon1):
    """Which primitives can show up inside this tile of the picture (seen from point O)."""
    out = {"b": [], "s": [], "c": []}
    for kind, i, c, r in bounds:
        v = c - O
        dist = float(np.linalg.norm(v))
        if dist <= r * 1.05:
            out[kind].append(i)
            continue
        lat = math.asin(max(-1, min(1, v[1] / dist)))
        lon = math.atan2(v[2], v[0])
        ang = math.asin(min(1, r / dist)) + 0.02
        if lat + ang < lat0 or lat - ang > lat1:
            continue
        if abs(lat) + ang < math.pi / 2 - 0.05:  # not covering a pole: check longitude too
            span = ang / max(0.05, math.cos(min(math.pi / 2 - 0.05, abs(lat) + ang)))
            mid = (lon0 + lon1) / 2
            half = (lon1 - lon0) / 2
            dl = abs((lon - mid + math.pi) % (2 * math.pi) - math.pi)
            if dl > half + span:
                continue
        out[kind].append(i)
    return out


# ----------------------------------------------------------------- shading
def hash2(a, b):
    return np.modf(np.abs(np.sin(a * 12.9898 + b * 78.233) * 43758.5453))[0].astype(F)


def sky(D, mode):
    y = np.clip(D[:, 1], -1, 1)[:, None]
    if mode == "day":
        hor = np.array([0.78, 0.86, 0.95], F)
        zen = np.array([0.22, 0.45, 0.85], F)
        c = hor + (zen - hor) * np.clip(y, 0, 1) ** 0.6
        sun = np.array([-0.45, 0.78, -0.43], F)
        sun /= np.linalg.norm(sun)
        s = np.clip(D @ sun, 0, 1)[:, None]
        c = c + np.array([1.0, 0.92, 0.75], F) * (s ** 600 * 8 + s ** 12 * 0.25)
        return c
    hor = np.array([0.035, 0.025, 0.06], F)
    zen = np.array([0.004, 0.004, 0.016], F)
    c = hor + (zen - hor) * np.clip(y, 0, 1) ** 0.5
    # stars
    lon = np.arctan2(D[:, 2], D[:, 0])
    lat = np.arcsin(y[:, 0])
    gx, gy = np.floor(lon * 240), np.floor(lat * 240)
    h = hash2(gx, gy)
    star = ((h > 0.9975) & (lat > 0.08)).astype(F)[:, None] * (0.4 + 0.6 * hash2(gy, gx)[:, None])
    return c + star * 0.9


def shade(O, D, P, t, kind, idx, mode, time_s, lit):
    n = D.shape[0]
    T = build_textures()
    col = sky(D, mode)
    hit = kind > 0
    if not hit.any():
        return col
    Dh = D[hit]
    th = t[hit]
    Ph = O + Dh * th[:, None]
    kh = kind[hit]
    ih = idx[hit]
    m = Ph.shape[0]
    Nrm = np.zeros((m, 3), F)
    alb = np.ones((m, 3), F) * 0.6
    emi = np.zeros((m, 3), F)
    night = mode == "night"

    # --- ground
    g = kh == 1
    if g.any():
        x, z = Ph[g, 0], Ph[g, 2]
        Nrm[g] = (0, 1, 0)
        gx, gz = np.floor(x / 0.6), np.floor(z / 0.6)
        h = hash2(gx, gz)[:, None]
        fx, fz = x / 0.6 - gx, z / 0.6 - gz
        grout = ((fx < 0.05) | (fz < 0.05))[:, None]
        c = np.array(srgb((168, 92, 62)), F) * (0.75 + 0.45 * h)
        c = np.where(grout, c * 0.45, c)
        road = (z < 0)[:, None]
        rh = hash2(np.floor(x * 9), np.floor(z * 9))[:, None]
        c = np.where(road, np.array(srgb((70, 66, 64)), F) * (0.85 + 0.3 * rh), c)
        df = ((np.abs(x) < 3.3) & (z > 15) & (z < 20.5))
        if df.any():
            tx, tz = np.floor(x[df] / 0.8), np.floor(z[df] / 0.8)
            th2 = hash2(tx + 3, tz + 5)
            pal = np.array([srgb(p) for p in [(236, 38, 143), (0, 196, 222), (255, 210, 0), (150, 64, 232), (30, 30, 40)]], F)
            k = (np.floor(th2 * 5 + (time_s * 2 if night else 0)).astype(int)) % 5
            ftx, ftz = x[df] / 0.8 - tx, z[df] / 0.8 - tz
            edge = ((ftx < 0.06) | (ftz < 0.06))[:, None]
            tc = np.where(edge, 0.05, pal[k])
            sub = c[df]
            sub[:] = tc * (0.5 if night else 0.85)
            c[df] = sub
            if night:
                pulse = 0.6 + 0.4 * abs(math.cos(2 * math.pi * 2.0 * time_s))
                e = np.zeros((df.sum(), 3), F)
                e[:] = np.where(edge, 0, pal[k] * 1.4 * pulse)
                eg = emi[g]
                eg[df] = e
                emi[g] = eg
        alb[g] = c

    # --- boxes
    b = kh == 2
    if b.any():
        bi = ih[b]
        Pb = Ph[b]
        mn = np.stack([P.box[i][0] for i in bi])
        mx = np.stack([P.box[i][1] for i in bi])
        dmin = np.abs(Pb - mn)
        dmax = np.abs(Pb - mx)
        dd = np.minimum(dmin, dmax)
        ax = dd.argmin(axis=1)
        sign = np.where(dmin[np.arange(len(ax)), ax] < dmax[np.arange(len(ax)), ax], -1.0, 1.0).astype(F)
        nb = np.zeros_like(Pb)
        nb[np.arange(len(ax)), ax] = sign
        Nrm[b] = nb
        ab = np.stack([P.box[i][3] for i in bi])
        eb = np.zeros_like(ab)
        tags = np.array([P.box[i][4] for i in bi])
        mats = np.array([P.box[i][2] for i in bi])

        def tex_face(sel, tex, u, v):
            s = sample(tex, u, v)
            ab[sel] = s[:, :3]
            msk = s[:, 3]
            if night:
                neon = np.clip((msk - 0.75) * 4, 0, 1)[:, None]
                paint = (np.clip(msk * 2, 0, 1) - neon[:, 0])[:, None]
                eb[sel] = s[:, :3] * (neon * 5.0 + paint * 0.07)
            else:
                neon = np.clip((msk - 0.75) * 4, 0, 1)[:, None]
                eb[sel] = s[:, :3] * neon * 0.35

        def plain(sel, c):
            ab[sel] = c
        whitewash = np.array(srgb((228, 222, 210)), F)
        for tag, face_ax, face_sign, umap in [
            ("left", 0, -1.0, lambda p: (p[:, 2] / 22, (3 - p[:, 1]) / 3)),
            ("right", 0, 1.0, lambda p: ((22 - p[:, 2]) / 22, (3 - p[:, 1]) / 3)),
            ("back", 2, -1.0, lambda p: ((7.3 - p[:, 0]) / 14.6, (3 - p[:, 1]) / 3)),
            ("front", 2, 1.0, lambda p: ((p[:, 0] + 7.3) / 14.6, (3 - p[:, 1]) / 3)),
        ]:
            ist = tags == tag
            if not ist.any():
                continue
            face = ist & (ax == face_ax) & (sign == face_sign)
            plain(ist & ~face, whitewash)
            if face.any():
                u, v = umap(Pb[face])
                tex_face(face, T[tag], u, v)
        s = tags == "sign"
        if s.any():
            face = s & (ax == 2) & (sign < 0)
            plain(s & ~face, np.array(srgb((26, 18, 44)), F))
            if face.any():
                p = Pb[face]
                tex_face(face, T["sign"], (2.2 - p[:, 0]) / 4.4, (3.8 - p[:, 1]) / 0.8)
        s = tags == "dj"
        if s.any():
            face = s & (ax == 2) & (sign < 0)
            plain(s & ~face, np.array(srgb((18, 18, 24)), F))
            if face.any():
                p = Pb[face]
                tex_face(face, T["dj"], (1.6 - p[:, 0]) / 3.2, (1.15 - p[:, 1]) / 1.15)
        s = tags == "bar"
        if s.any():
            face = s & (ax == 0) & (sign < 0)
            top = s & (ax == 1)
            plain(top, np.array(srgb((70, 40, 24)), F))
            if face.any():
                p = Pb[face]
                tex_face(face, T["barfront"], (p[:, 2] - 5.5) / 4.0, (1.1 - p[:, 1]) / 1.1)
        for tag in ("bright", "bleft"):
            s = tags == tag
            if not s.any():
                continue
            p = Pb[s]
            along = np.where(ax[s] == 0, p[:, 2], p[:, 0])
            wx = np.mod(along, 2.6)
            win = ((wx > 0.7) & (wx < 1.9) & (((p[:, 1] > 3.6) & (p[:, 1] < 5.0)) | ((p[:, 1] > 0.8) & (p[:, 1] < 2.2))))
            roof = ax[s] == 1
            base = ab[s]
            wc = np.array(srgb((40, 60, 70)), F)
            base = np.where(win[:, None], wc, base)
            base = np.where(roof[:, None], np.array(srgb((150, 60, 40)), F), base)
            ab[s] = base
            if night:
                wid = hash2(np.floor(along / 2.6), np.floor(p[:, 1] / 2.4))
                on = (win & (wid > 0.35))[:, None]
                ee = eb[s]
                ee = np.where(on, np.array([1.0, 0.62, 0.3], F) * 1.6, ee)
                eb[s] = ee
        sp = mats == SPEAKER
        if sp.any():
            face = sp & (ax == 2) & (sign < 0)
            if face.any():
                p = Pb[face]
                cx = np.where(p[:, 0] < 0, -2.75, 2.75)
                r1 = np.hypot(p[:, 0] - cx, p[:, 1] - 1.35)
                r2 = np.hypot(p[:, 0] - cx, p[:, 1] - 0.6)
                cone = ((r1 < 0.3) | (r2 < 0.38))
                ab[face] = np.where(cone[:, None], np.array(srgb((70, 70, 78)), F), ab[face])
        pp = mats == PINGPONG
        if pp.any():
            p = Pb[pp]
            line = (np.abs(p[:, 2] - 2.5) < 0.02) | (np.abs(p[:, 0] + 5.2) < 0.015) | \
                   (np.abs(p[:, 0] + 4.03) < 0.03) | (np.abs(p[:, 0] + 6.37) < 0.03)
            ab[pp] = np.where(line[:, None], 0.85, ab[pp])
        alb[b] = ab
        emi[b] = eb

    # --- spheres
    s = kh == 3
    if s.any():
        si = ih[s]
        c = np.stack([P.sph[i][0] for i in si])
        r = np.array([P.sph[i][1] for i in si], F)[:, None]
        Ns = (Ph[s] - c) / r
        Nrm[s] = Ns
        a = np.stack([P.sph[i][3] for i in si])
        mats = np.array([P.sph[i][2] for i in si])
        leaf = mats == LEAF
        if leaf.any():
            p = Ph[s][leaf]
            hh = hash2(np.floor(p[:, 0] * 4) + np.floor(p[:, 2] * 4) * 7, np.floor(p[:, 1] * 4))[:, None]
            a[leaf] = a[leaf] * (0.6 + 0.8 * hh)
        alb[s] = a

    # --- cylinders
    cy = kh == 4
    if cy.any():
        ci = ih[cy]
        cx = np.array([P.cyl[i][0] for i in ci], F)
        cz = np.array([P.cyl[i][1] for i in ci], F)
        r = np.array([P.cyl[i][2] for i in ci], F)
        p = Ph[cy]
        Nrm[cy] = np.stack([(p[:, 0] - cx) / r, np.zeros_like(r), (p[:, 2] - cz) / r], 1)
        a = np.stack([P.cyl[i][6] for i in ci])
        mats = np.array([P.cyl[i][5] for i in ci])
        legs = (mats == SHIRT) & (p[:, 1] < np.array([P.cyl[i][3] for i in ci], F) + 0.85)
        a = np.where(legs[:, None], np.array(srgb((40, 50, 80)), F), a)
        alb[cy] = a

    # --- lighting
    Nrm /= np.maximum(np.linalg.norm(Nrm, axis=1, keepdims=True), 1e-6)
    if not night:
        sun = np.array([-0.45, 0.78, -0.43], F)
        sun /= np.linalg.norm(sun)
        ndl = np.clip(Nrm @ sun, 0, 1)
        lit_idx = np.nonzero(ndl > 0)[0]
        shadow = np.zeros(m, bool)
        if len(lit_idx):
            Os = Ph[lit_idx] + Nrm[lit_idx] * 0.01
            Ds = np.broadcast_to(sun, (len(lit_idx), 3)).astype(F)
            shadow[lit_idx] = trace(Os, Ds, P, shadow=True, tmax=60.0)
        sky_amb = 0.42 + 0.18 * Nrm[:, 1:2]
        light = np.array([1.0, 0.95, 0.85], F) * (ndl * (~shadow))[:, None] * 1.05 + \
            np.array([0.62, 0.72, 0.95], F) * sky_amb
        out = alb * light + emi
    else:
        acc = np.full((m, 3), 0.018, F) + np.array([0.01, 0.006, 0.02], F)
        for (lp, lc, li) in lit:
            v = lp - Ph
            d2 = np.einsum("ij,ij->i", v, v)
            l = v / np.sqrt(d2)[:, None]
            ndl = np.clip(np.einsum("ij,ij->i", Nrm, l), 0, 1)
            acc += lc * (li * ndl / (1 + d2 * 0.9))[:, None]
        out = alb * acc + emi
    # distance haze for the far treeline
    fog = np.clip((th - 25) / 40, 0, 0.6)[:, None]
    out = out * (1 - fog) + (np.array([0.7, 0.8, 0.9], F) if not night else np.array([0.02, 0.015, 0.035], F)) * fog
    col[hit] = out
    return col


# ---------------------------------------------------------------- rendering
def directions(W, H, r0, r1, c0, c1):
    j = np.arange(r0, r1, dtype=F) + 0.5
    i = np.arange(c0, c1, dtype=F) + 0.5
    u = i / W
    v = 1 - j / H
    lon = (u - 0.5) * 2 * np.pi
    lat = (v - 0.5) * np.pi
    LON, LAT = np.meshgrid(lon, lat)
    cl = np.cos(LAT)
    D = np.stack([cl * np.cos(LON), np.sin(LAT), cl * np.sin(LON)], -1).reshape(-1, 3).astype(F)
    return D, (lat.min(), lat.max()), (lon.min(), lon.max())


def to_pixel(Dirs, W, H):
    lon = np.arctan2(Dirs[:, 2], Dirs[:, 0])
    lat = np.arcsin(np.clip(Dirs[:, 1], -1, 1))
    x = (lon / (2 * np.pi) + 0.5) * W - 0.5
    y = (1 - (lat / np.pi + 0.5)) * H - 0.5
    return x, y


def tonemap(c):
    c = np.maximum(c, 0)
    a = c * (2.51 * c + 0.03) / (c * (2.43 * c + 0.59) + 0.14)
    return np.clip(a, 0, 1) ** (1 / 2.2)


def render(cam, W, mode, time_s=0.0):
    H = W // 2
    O = np.array(cam, F)
    P = build_scene(mode, time_s)
    bounds = P.bounds()
    lit = lights(mode, time_s)
    img = np.zeros((H, W, 3), F)
    TH, TW = max(32, H // 8), max(64, W // 8)
    for r0 in range(0, H, TH):
        for c0 in range(0, W, TW):
            r1, c1 = min(H, r0 + TH), min(W, c0 + TW)
            D, (la0, la1), (lo0, lo1) = directions(W, H, r0, r1, c0, c1)
            pad = math.pi / H * 2
            cand = candidates(P, bounds, O, la0 - pad, la1 + pad, lo0 - pad, lo1 + pad)
            t, kind, idx = trace(O, D, P, cand)
            col = shade(O, D, P, t, kind, idx, mode, time_s, lit)
            img[r0:r1, c0:c1] = col.reshape(r1 - r0, c1 - c0, 3)
    # string lights: a thin wire and glowing bulbs, hidden where something is in front
    pts, cols = string_lights(mode)
    dense = []
    for row in range(0, len(pts), 27):
        seg = pts[row:row + 27]
        for a, b2 in zip(seg[:-1], seg[1:]):
            for f in np.linspace(0, 1, 14, endpoint=False):
                dense.append(a + (b2 - a) * f)
    dense = np.array(dense, F)
    for arr, is_bulb in ((dense, False), (pts, True)):
        v = arr - O
        dist = np.linalg.norm(v, axis=1)
        Dv = v / dist[:, None]
        tt, kk, _ = trace(O, Dv, P)
        vis = ~((kk > 0) & (tt < dist - 0.05))
        x, y = to_pixel(Dv, W, H)
        for k in np.nonzero(vis)[0]:
            xi, yi = int(round(x[k])) % W, int(round(y[k]))
            if not (0 <= yi < H):
                continue
            if not is_bulb:
                img[yi, xi] = img[yi, xi] * 0.3 + 0.01
                continue
            c = cols[k] * (6.0 if mode == "night" else 0.25)
            rad = max(1.0, W / 2048 * 9.0 / dist[k])
            R = int(math.ceil(rad * 3))
            ys, xs = np.mgrid[-R:R + 1, -R:R + 1]
            wgt = np.exp(-(xs ** 2 + ys ** 2) / (2 * rad * rad)).astype(F)
            y0, y1 = max(0, yi - R), min(H, yi + R + 1)
            xx = (xi + np.arange(-R, R + 1)) % W
            wv = wgt[(y0 - yi + R):(y1 - yi + R)]
            img[y0:y1][:, xx] += wv[..., None] * c
    if mode == "night":  # soft glow around bright things
        bright = np.maximum(img - 0.7, 0)
        g1 = cv2.GaussianBlur(bright, (0, 0), W / 600)
        g2 = cv2.GaussianBlur(bright, (0, 0), W / 160)
        img = img + g1 * 0.6 + g2 * 0.5
    out = (tonemap(img) * 255 + 0.5).astype(np.uint8)
    return out


# -------------------------------------------------------------- the files
def ease(f):
    return f * f * (3 - 2 * f)


def clip_job(args):
    a, b, f, n, W, mode = args
    p = ease(f / (n - 1))
    A, B = np.array(STOPS[a]), np.array(STOPS[b])
    cam = A + (B - A) * p
    cam[1] += 0.018 * math.sin(2 * math.pi * 1.8 * f / FPS) * math.sin(math.pi * f / (n - 1))
    return render(tuple(cam), W, mode, time_s=f / FPS)


def loop_job(args):
    f, W = args
    return render(STOPS["floor"], W, "night", time_s=f / FPS)


def write_video(frames_iter, path, W, crf=23):
    H = W // 2
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2", "-g", str(FPS),
           "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in frames_iter:
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed for " + path)


def save_photo(img, name):
    Image.fromarray(img).save(os.path.join(OUT, name + ".jpg"), quality=86, optimize=True, progressive=True)
    small = Image.fromarray(img).resize((1024, 512), Image.LANCZOS)
    small.save(os.path.join(OUT, name + "-small.jpg"), quality=78, optimize=True, progressive=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    build_textures()
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        prev = os.path.join(ROOT, "tools", "preview")
        os.makedirs(prev, exist_ok=True)
        for stop in STOPS:
            for mode in ("day", "night"):
                t0 = time.time()
                img = render(STOPS[stop], 1024, mode)
                Image.fromarray(img).save(os.path.join(prev, f"{stop}-{mode}.jpg"), quality=88)
                print(stop, mode, f"{time.time() - t0:.1f}s", flush=True)
        return
    W_PHOTO = int(os.environ.get("PHOTO_W", 4096))
    W_CLIP = int(os.environ.get("CLIP_W", 2048))
    n_clip = int(os.environ.get("CLIP_FRAMES", 72))
    n_loop = int(os.environ.get("LOOP_FRAMES", 72))
    names = {"gate": "stop1-gate", "bar": "stop2-bar", "floor": "stop3-floor"}
    with Pool(int(os.environ.get("JOBS", os.cpu_count() or 2))) as pool:
        t0 = time.time()
        photo_jobs = [(STOPS[s], W_PHOTO, m) for s in STOPS for m in ("day", "night")]
        for (s, m), img in zip([(s, m) for s in STOPS for m in ("day", "night")],
                               pool.starmap(render, photo_jobs)):
            save_photo(img, f"{names[s]}-{m}")
        print(f"photos done {time.time() - t0:.0f}s", flush=True)
        for (a, b, name) in [("gate", "bar", "clip1-gate-to-bar"), ("bar", "floor", "clip2-bar-to-floor")]:
            for mode in ("day", "night"):
                jobs = [(a, b, f, n_clip, W_CLIP, mode) for f in range(n_clip)]
                write_video(pool.imap(clip_job, jobs), os.path.join(OUT, f"{name}-{mode}.mp4"), W_CLIP)
                print(f"{name}-{mode} done {time.time() - t0:.0f}s", flush=True)
        jobs = [(f, W_CLIP) for f in range(n_loop)]
        write_video(pool.imap(loop_job, jobs), os.path.join(OUT, "loop3-floor-night.mp4"), W_CLIP)
        print(f"loop done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
