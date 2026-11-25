#!/usr/bin/env python3
"""Sum up Tuesday 24 November 2026's world news in one 1024x1024 image.

A newspaper front page, drawn from scratch with the Python standard
library only: a 5x7 bitmap font, flat vector pictograms and a fixed
palette. No network, no clock, no randomness, no environment reads:
two runs write byte-identical PNGs.

Layout, top to bottom:
  masthead  - date and title
  hero      - Riyadh: Houthi strike on the capital's tallest tower
  row one   - Gaza / Zaporizhzhia / Estonia
  row two   - Senegal / Nvidia / markets
  footer    - the rest of the day in one line
"""

import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
CREAM = (246, 241, 229)   # newsprint paper
PAPER = (255, 253, 247)   # panel paper
INK = (24, 24, 32)        # body ink
NAVY = (22, 50, 79)       # masthead + footer
NAVY_D = (16, 36, 58)
RED = (179, 38, 30)       # accent / kicker
GOLD = (201, 162, 39)
TEAL = (42, 127, 111)
GREY = (110, 108, 100)
LINE = (180, 172, 154)
SKY_TOP = (43, 58, 85)
SKY_MID = (120, 110, 130)
SKY_LOW = (232, 163, 76)
SMOKE = (96, 92, 88)
SMOKE_L = (150, 146, 140)
FLAME = (224, 110, 32)
FLAME_Y = (240, 190, 60)
GREEN = (0, 120, 60)
SEN_Y = (252, 210, 0)
SEN_R = (206, 17, 38)

# --- 5x7 bitmap font (uppercase; lowercase maps to uppercase) --------------
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
}

# The middle dot used between items in the footer strip.
FONT["·"] = ("00000", "00000", "01100", "01100", "01100", "00000", "00000")
FONT["—"] = ("00000", "00000", "00000", "11111", "00000", "00000", "00000")


def glyph(ch):
    """Bitmap rows for one character; unknown chars render blank."""
    return FONT.get(ch.upper(), FONT[" "])


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per char)."""
    return len(text) * 6 * scale - scale


# --- canvas ------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            n = (x1 - x0) * 3
            self.px[i:i + n] = bytes(color) * (x1 - x0)

    def hline(self, x0, x1, y, color):
        if y < 0 or y >= self.h:
            return
        a, b = max(0, min(x0, x1)), min(self.w - 1, max(x0, x1))
        for x in range(a, b + 1):
            self.set(x, y, color)

    def vline(self, x, y0, y1, color):
        if x < 0 or x >= self.w:
            return
        a, b = max(0, min(y0, y1)), min(self.h - 1, max(y0, y1))
        for y in range(a, b + 1):
            self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        """Filled disc."""
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def ring(self, cx, cy, r, color, thick=2):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cx - dx + thick - 1, cy + dy, color)
            self.hline(cx + dx - thick + 1, cx + dx, cy + dy, color)

    def poly(self, pts, color):
        """Filled polygon (scanline, even-odd)."""
        if len(pts) < 3:
            return
        ys = [y for _, y in pts]
        for y in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(int(xs[j]), int(xs[j + 1]), y, color)

    def text(self, s, x, y, scale, color):
        """Draw text left-aligned at (x, y); returns the pixel width."""
        cx = x
        for ch in s:
            rows = glyph(ch)
            for ry in range(7):
                row = rows[ry]
                for rx in range(5):
                    if row[rx] == "1":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx - x - scale

    def text_centred(self, s, cx, y, scale, color):
        w = text_width(s, scale)
        return self.text(s, cx - w // 2, y, scale, color)


def wrap_lines(text, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def write_png(path, canvas):
    """Deterministic RGB PNG: filter 0, zlib level 9, fixed chunks."""
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * canvas.w * 3:(y + 1) * canvas.w * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# --- small pictograms ---------------------------------------------------------
def burst(c, cx, cy, r, color):
    """Starburst: 12 spikes around a centre."""
    pts = []
    for i in range(24):
        ang = i * 3.14159265 / 12.0
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((int(cx + rr * _cos(ang)), int(cy + rr * _sin(ang))))
    c.poly(pts, color)


def _cos(a):
    # small cosine via the Taylor-free lookup of sin/cos pairs is overkill;
    # use the stdlib-free series instead (deterministic, no imports).
    return _trig(a, 1)


def _sin(a):
    return _trig(a, 0)


def _trig(a, kind):
    # a in radians; series to 1e-9, enough for pixel art.
    x = a % 6.283185307179586
    if kind == 0:  # sin
        t, s, n = x, x, 1.0
        term = x
        for k in range(1, 8):
            term *= -x * x / ((2 * k) * (2 * k + 1))
            s += term
        return s
    t = 1.0
    s = 1.0
    term = 1.0
    for k in range(1, 8):
        term *= -x * x / ((2 * k - 1) * (2 * k))
        s += term
    return s


def skyline(c, x, y_base, w, h, color, windows):
    """A row of dark towers of varied heights on a baseline."""
    n = 7
    step = w // n
    heights = [0.55, 0.8, 0.62, 1.0, 0.72, 0.9, 0.58]
    for i in range(n):
        bh = int(h * heights[i])
        bx = x + i * step + 2
        bw = step - 6
        c.rect(bx, y_base - bh, bw, bh, color)
        for wy in range(y_base - bh + 8, y_base - 6, 14):
            for wx in range(bx + 4, bx + bw - 4, 10):
                if (wx * 7 + wy * 13) % 29 < 12:
                    c.rect(wx, wy, 3, 4, windows)


def tower(c, x, y_base, w, h, color, windows):
    """One tall tapering tower, slightly twisted: the hero tower."""
    top_w = int(w * 0.55)
    pts = [(x, y_base), (x + w, y_base),
           (x + w - (w - top_w) // 2 - 6, y_base - h),
           (x + (w - top_w) // 2 + 6, y_base - h)]
    c.poly(pts, color)
    # crown fins
    c.rect(x + (w - top_w) // 2 + 2, y_base - h - 10, 6, 12, color)
    c.rect(x + w - (w - top_w) // 2 - 8, y_base - h - 10, 6, 12, color)
    # lit window bands, narrowing with the taper
    yy = y_base - 14
    while yy > y_base - h + 12:
        frac = (y_base - yy) / float(h)
        ww = int(w - frac * (w - top_w) * 0.85)
        x0 = x + (w - ww) // 2
        for wx in range(x0 + 4, x0 + ww - 4, 12):
            if (wx * 3 + yy * 5) % 23 < 11:
                c.rect(wx, yy, 4, 5, windows)
        yy -= 16


def smoke_plume(c, cx, cy, color, light):
    """Rising smoke: a stack of overlapping discs, light on top.

    Compact on purpose: the whole plume stays within ~45 px above its
    base so it never spills out of the picture or panel it belongs to.
    """
    puffs = [(0, 0, 15), (-9, -12, 12), (8, -16, 13),
             (-3, -28, 10), (6, -36, 8)]
    for dx, dy, r in puffs:
        c.disc(cx + dx, cy + dy, r, color)
    c.disc(cx - 3, cy - 28, 6, light)
    c.disc(cx + 6, cy - 36, 5, light)


def trophy(c, cx, cy, s):
    """A winner's cup, drawn at scale s (unit ~ s pixels)."""
    u = s
    # cup bowl
    c.poly([(cx - 5 * u, cy - 6 * u), (cx + 5 * u, cy - 6 * u),
            (cx + 4 * u, cy), (cx - 4 * u, cy)], GOLD)
    # handles
    c.ring(cx - 6 * u, cy - 4 * u, 3 * u, GOLD, 2 * u)
    c.ring(cx + 6 * u, cy - 4 * u, 3 * u, GOLD, 2 * u)
    # stem + base
    c.rect(cx - u, cy, 2 * u, 4 * u, GOLD)
    c.rect(cx - 5 * u, cy + 4 * u, 10 * u, 2 * u, GOLD)
    # star on the bowl
    burst(c, cx, cy - 3 * u, 2 * u, (255, 255, 255))


def chip(c, x, y, w, h):
    """A processor chip with pins."""
    c.rect(x - 6, y + 8, 6, h - 16, INK)
    c.rect(x + w, y + 8, 6, h - 16, INK)
    c.rect(x + 8, y - 6, w - 16, 6, INK)
    c.rect(x + 8, y + h, w - 16, 6, INK)
    c.rect(x, y, w, h, TEAL)
    c.rect(x + 6, y + 6, w - 12, h - 12, NAVY)
    c.text("NVDA", x + w // 2 - text_width("NVDA", 1) // 2,
           y + h // 2 - 4, 1, (255, 255, 255))


def chart_down(c, x, y, w, h, color):
    """A falling market line with an arrowhead."""
    pts = [(x, y + h // 4), (x + w // 4, y + h // 3),
           (x + w // 2, y + h // 2), (x + 3 * w // 4, y + 2 * h // 3),
           (x + w, y + h - 6)]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color)
        c.line(pts[i][0], pts[i][1] + 1, pts[i + 1][0], pts[i + 1][1] + 1,
               color)
    ex, ey = pts[-1]
    c.poly([(ex, ey), (ex - 12, ey - 2), (ex - 2, ey - 12)], color)


def barrier(c, x, y, w, h):
    """A border fence: posts, rails and a warning triangle."""
    for px in range(x, x + w, 26):
        c.rect(px, y, 5, h, INK)
    c.rect(x, y + 10, w, 5, INK)
    c.rect(x, y + h - 16, w, 5, INK)
    for px in range(x + 8, x + w - 4, 26):
        c.line(px, y + 15, px + 18, y + h - 16, INK)
    c.poly([(x + w - 46, y + h - 4), (x + w - 14, y + h - 4),
            (x + w - 30, y + 8)], RED)
    c.text("!", x + w - 33, y + h - 34, 3, (255, 255, 255))


# --- page ----------------------------------------------------------------------
def masthead(c):
    c.rect(0, 0, W, 104, NAVY)
    c.rect(0, 104, W, 5, RED)
    c.text_centred("THE WORLD IN ONE PICTURE", W // 2, 16, 4, (255, 255, 255))
    c.text_centred("TUESDAY 24 NOVEMBER 2026", W // 2, 66, 3, GOLD)
    c.text("MAKE.FUN", 24, 20, 2, (200, 210, 225))
    c.text("$100 IN PRIZES", W - 24 - text_width("$100 IN PRIZES", 2), 20, 2,
           (200, 210, 225))


def hero(c):
    x0, y0, w, h = 24, 122, W - 48, 322
    # dusk sky, band by band
    bands = [(SKY_TOP, 0.0), (SKY_MID, 0.45), (SKY_LOW, 0.8)]
    for yy in range(h):
        f = yy / float(h)
        if f < 0.45:
            col = SKY_TOP
        elif f < 0.8:
            col = SKY_MID
        else:
            col = SKY_LOW
        c.hline(x0, x0 + w - 1, y0 + yy, col)
    # low sun
    c.disc(x0 + w - 130, y0 + 62, 26, FLAME_Y)
    # skyline behind the hero tower
    skyline(c, x0 + 8, y0 + h - 58, 300, 150, NAVY_D, GOLD)
    skyline(c, x0 + w - 300, y0 + h - 58, 290, 120, NAVY_D, GOLD)
    # the tower, struck near its crown
    tx = x0 + w // 2 - 55
    tower(c, tx, y0 + h - 58, 110, 180, NAVY, GOLD)
    burst(c, tx + 55, y0 + h - 58 - 178, 34, FLAME)
    burst(c, tx + 55, y0 + h - 58 - 178, 20, FLAME_Y)
    smoke_plume(c, tx + 55, y0 + h - 58 - 190, SMOKE, SMOKE_L)
    # ground + street
    c.rect(x0, y0 + h - 58, w, 58, (30, 30, 38))
    c.rect(x0, y0 + h - 58, w, 4, GOLD)
    # caption bar over the picture's foot
    c.rect(x0, y0 + h - 96, w, 96, (18, 18, 26))
    c.rect(x0, y0 + h - 96, w, 3, RED)
    c.text("RIYADH STRUCK AGAIN", x0 + 18, y0 + h - 88, 3, (255, 255, 255))
    sub = ("Houthi missile hits the capital's tallest tower, 11 hurt; "
           "fighters close on Aden")
    for i, ln in enumerate(wrap_lines(sub, w - 36, 2)):
        c.text(ln, x0 + 18, y0 + h - 52 + i * 18, 2, (220, 220, 215))


def panel(c, x, y, w, h, kicker, headline, body, art):
    c.rect(x, y, w, h, PAPER)
    c.rect(x, y, w, 2, LINE)
    c.rect(x, y + h - 2, w, 2, LINE)
    c.rect(x, y, 2, h, LINE)
    c.rect(x + w - 2, y, 2, h, LINE)
    c.rect(x, y, w, 4, RED)
    art(c, x + 14, y + 14, w - 28, 88)
    c.text(kicker, x + 14, y + 112, 2, RED)
    lines = wrap_lines(headline, w - 28, 2)
    yy = y + 136
    for ln in lines:
        c.text(ln, x + 14, yy, 2, INK)
        yy += 18
    for ln in wrap_lines(body, w - 28, 2):
        c.text(ln, x + 14, yy + 4, 2, GREY)
        yy += 16


def art_gaza(c, x, y, w, h):
    c.rect(x, y, w, h, (232, 222, 205))
    c.rect(x, y + h - 34, w, 34, (52, 48, 44))
    for bx in range(x + 8, x + w - 30, 34):
        c.rect(bx, y + h - 62, 26, 28, (74, 70, 64))
    burst(c, x + w // 2, y + 42, 30, FLAME)
    burst(c, x + w // 2, y + 42, 18, FLAME_Y)
    smoke_plume(c, x + w // 2 + 8, y + 56, SMOKE, SMOKE_L)


def art_ukraine(c, x, y, w, h):
    c.rect(x, y, w, h, (214, 226, 238))
    bx, bw = x + 30, w - 60
    c.rect(bx, y + 22, bw, h - 22, (96, 92, 88))
    c.poly([(bx, y + 22), (bx + bw, y + 22), (bx + bw - 18, y + 4),
            (bx + 14, y + 4)], (60, 56, 52))
    for wy in range(y + 34, y + h - 8, 16):
        for wx in range(bx + 8, bx + bw - 8, 16):
            c.rect(wx, wy, 7, 9, GOLD)
    burst(c, bx + bw - 8, y + 14, 16, FLAME)
    smoke_plume(c, bx + bw // 2, y + 44, SMOKE, SMOKE_L)


def art_estonia(c, x, y, w, h):
    c.rect(x, y, w, h, (226, 232, 226))
    barrier(c, x + 12, y + 14, w - 24, h - 28)


def art_senegal(c, x, y, w, h):
    c.rect(x, y, w, h, (214, 238, 220))
    c.rect(x, y, w, 10, GREEN)
    c.rect(x, y + 10, w, 10, SEN_Y)
    c.rect(x, y + 20, w, 10, SEN_R)
    trophy(c, x + w // 2, y + h // 2 + 8, 3)


def art_nvidia(c, x, y, w, h):
    c.rect(x, y, w, h, (222, 232, 226))
    chip(c, x + w // 2 - 34, y + 18, 68, 56)


def art_markets(c, x, y, w, h):
    c.rect(x, y, w, h, (238, 228, 222))
    chart_down(c, x + 14, y + 14, w - 28, h - 28, RED)
    c.text("-0.95%", x + w - 86, y + 12, 2, RED)


def footer(c):
    c.rect(0, 952, W, 72, NAVY)
    c.rect(0, 952, W, 3, RED)
    line1 = ("ALSO TODAY: Spain amnesties Puigdemont  ·  China probes "
             "Chen Jining")
    line2 = ("UN seeks probe into Libya ship attack  ·  Pakistani astronaut "
             "to fly on Shenzhou-24")
    c.text(line1, 24, 966, 2, (225, 228, 232))
    c.text(line2, 24, 992, 2, (200, 205, 212))


def build():
    c = Canvas(W, H, CREAM)
    masthead(c)
    hero(c)
    gap, pw = 16, (W - 48 - 2 * 16) // 3
    y1, h1 = 460, 252
    panel(c, 24, y1, pw, h1, "GAZA",
          "ISRAELI STRIKES KILL HAMAS SECURITY CHIEF",
          "Naeem Abu Nahel among seven dead in Gaza, medics say.",
          art_gaza)
    panel(c, 24 + pw + gap, y1, pw, h1, "UKRAINE",
          "NIGHT STRIKE ON ZAPORIZHZHIA",
          "2 killed, 40 hurt, four of them children, in a hit on flats.",
          art_ukraine)
    panel(c, 24 + 2 * (pw + gap), y1, pw, h1, "ESTONIA",
          "RUSSIA WARNS OF 'OPEN WAR'",
          "Over Tallinn's plan to shut its border crossings on Dec 1.",
          art_estonia)
    y2, h2 = 724, 220
    panel(c, 24, y2, pw, h2, "SENEGAL",
          "SENEGAL ARE CHAMPIONS AGAIN",
          "Top court reinstates them as 2025 Africa Cup winners.",
          art_senegal)
    panel(c, 24 + pw + gap, y2, pw, h2, "NVIDIA",
          "HUANG BACK AT NVIDIA",
          "Chief executive reinstated days after resigning.",
          art_nvidia)
    panel(c, 24 + 2 * (pw + gap), y2, pw, h2, "MARKETS",
          "STOCKS SLIP AS RATES WORRY",
          "S&P 500 -0.95%. Brent crude $87.51.",
          art_markets)
    footer(c)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    canvas = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, canvas)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
