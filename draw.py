#!/usr/bin/env python3
"""Draw the front page for Tuesday 24 November 2026.

Pure standard library: builds the pixels in memory and writes a PNG with
zlib. No network, no clock, no randomness, so the same run always writes
the same bytes. Run: python3 draw.py  (writes entry.png next to this file).
"""

import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# --- palette: paper white, ink, one red accent, one navy band --------------
PAPER = (255, 255, 255)
INK = (20, 20, 20)
RED = (200, 16, 46)
NAVY = (11, 44, 74)
GREY = (107, 114, 128)
RULE = (176, 176, 176)
SKY = (220, 233, 242)
SEA = (31, 111, 139)
SUN = (232, 163, 23)
FLAME = (224, 82, 6)
SMOKE = (138, 138, 138)
PALE_BLUE = (226, 236, 244)
PALE_GREY = (235, 235, 232)
PALE_SAND = (243, 236, 220)
PALE_ROSE = (246, 228, 228)
STEEL = (70, 90, 110)
GOLD = (201, 162, 39)

# --- 5x7 bitmap font: each glyph is 7 rows of 5 cells ----------------------
# Uppercase, lowercase, digits and punctuation, drawn from a plain grid.
FONT = {}
_UC = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
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
}
_LC = {
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01111", "10000", "10000", "10000", "01111"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01000", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00000", "00100", "00000", "01100", "00100", "00100", "01110"),
    "j": ("00000", "00010", "00000", "00110", "00010", "00010", "00010", "11000"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10001", "01110"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
}
_DG = {
    "0": ("01110", "10011", "10101", "11001", "10001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "00100", "00100", "00100"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
}
_PU = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    "'": ("00100", "00100", "00100", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "(": ("00011", "00100", "01000", "01000", "01000", "00100", "00011"),
    ")": ("11000", "00100", "00010", "00010", "00010", "00100", "11000"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "%": ("10001", "10010", "00010", "00100", "01000", "01001", "10001"),
    "&": ("01100", "10010", "10010", "01000", "10101", "10010", "01101"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}
FONT.update(_UC)
FONT.update(_LC)
FONT.update(_DG)
FONT.update(_PU)


class Canvas:
    """An RGB pixel buffer with small drawing helpers."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:(base + (x1 - x0) * 3)] = bytes(color) * (x1 - x0)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = (1 if x1 > x0 else -1), (1 if y1 > y0 else -1)
        err = dx - dy
        while True:
            self.put(x0, y0, color)
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
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.rect(cx - dx, yy, dx * 2 + 1, 1, color)

    def tri(self, x0, y0, x1, y1, x2, y2, color):
        # Fill a triangle by scanning its rows.
        ys = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        if ay == cy:
            return
        def edge_x(p, q, y):
            if p[1] == q[1]:
                return p[0]
            return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])
        for y in range(ay, cy + 1):
            if y < by:
                xa, xb = edge_x((ax, ay), (bx, by), y), edge_x((ax, ay), (cx, cy), y)
            else:
                xa, xb = edge_x((bx, by), (cx, cy), y), edge_x((ax, ay), (cx, cy), y)
            self.rect(int(min(xa, xb)), y, int(abs(xb - xa)) + 1, 1, color)

    # --- text ---------------------------------------------------------------
    def glyph(self, x, y, ch, scale, color, bold=False):
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT["?"]
        off = max(1, scale // 3) if bold else 0
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                if cell == "1":
                    self.rect(x + c * scale, y + r * scale, scale, scale, color)
                    if bold:
                        self.rect(x + c * scale + off, y + r * scale, scale, scale, color)

    def text_w(self, s, scale, bold=False):
        n = len(s)
        if n == 0:
            return 0
        w = n * 6 * scale - scale
        if bold:
            w += max(1, scale // 3)
        return w

    def text(self, x, y, s, scale, color, bold=False):
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, color, bold)
            cx += 6 * scale

    def wrap(self, s, max_w, scale, bold=False):
        """Greedy word wrap; returns a list of lines that fit max_w."""
        lines, cur = [], ""
        for word in s.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, scale, bold) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def png_bytes(w, h, px):
    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    head = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(px[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


# --- story art ---------------------------------------------------------------
def art_hormuz(c, x, y, w, h):
    """Strait at dusk: sun, sea, a tanker on fire, spiked mines."""
    c.rect(x, y, w, h, SKY)
    c.disc(x + w - 52, y + 34, 22, SUN)
    c.rect(x, y + 96, w, h - 96, SEA)
    c.rect(x, y + 96, w, 3, STEEL)
    # tanker hull and bridge
    c.rect(x + 60, y + 150, 240, 26, INK)
    c.tri(x + 300, y + 150, x + 330, y + 150, x + 300, y + 168, INK)
    c.rect(x + 96, y + 128, 34, 22, INK)
    c.rect(x + 140, y + 136, 12, 14, INK)
    c.rect(x + 240, y + 132, 16, 18, INK)
    # flames rising from the deck, smoke above them
    c.tri(x + 168, y + 150, x + 192, y + 150, x + 180, y + 118, FLAME)
    c.tri(x + 196, y + 150, x + 214, y + 150, x + 205, y + 124, RED)
    c.disc(x + 182, y + 108, 10, SMOKE)
    c.disc(x + 196, y + 94, 13, SMOKE)
    c.disc(x + 210, y + 80, 9, SMOKE)
    # mines: spiked circles in the water
    for mx, my in ((x + 40, y + 200), (x + 330, y + 212)):
        for ang in range(0, 360, 45):
            import math
            r = math.radians(ang)
            c.line(mx, my, mx + int(12 * math.cos(r)), my + int(12 * math.sin(r)), INK)
        c.disc(mx, my, 10, INK)
    # wave lines
    c.line(x + 20, y + 190, x + 90, y + 190, (255, 255, 255))
    c.line(x + 250, y + 224, x + 330, y + 224, (255, 255, 255))


def art_chip(c, x, y, w, h):
    c.rect(x, y, w, h, PALE_BLUE)
    cx, cy = x + w // 2, y + h // 2
    for dx in (-34, -12, 12, 34):
        c.rect(cx + dx - 3, cy - 44, 6, 12, STEEL)
        c.rect(cx + dx - 3, cy + 32, 6, 12, STEEL)
        c.rect(cx - 44, cy + dx - 3, 12, 6, STEEL)
        c.rect(cx + 32, cy + dx - 3, 12, 6, STEEL)
    c.rect(cx - 32, cy - 32, 64, 64, NAVY)
    c.rect(cx - 18, cy - 18, 36, 36, GOLD)
    c.rect(cx - 8, cy - 8, 16, 16, NAVY)


def art_skyline(c, x, y, w, h):
    c.rect(x, y, w, h, PALE_GREY)
    c.rect(x + 14, y + 46, 24, 58, STEEL)
    c.rect(x + 44, y + 30, 26, 74, NAVY)
    c.rect(x + 76, y + 54, 22, 50, STEEL)
    for wx in (20, 50, 82):
        for wy in (56, 72, 88):
            c.rect(x + wx, y + wy, 8, 8, (255, 214, 64))
    c.disc(x + 57, y + 20, 9, SMOKE)
    c.disc(x + 66, y + 10, 12, SMOKE)
    c.tri(x + 78, y + 54, x + 92, y + 54, x + 85, y + 38, FLAME)


def art_flats(c, x, y, w, h):
    c.rect(x, y, w, h, PALE_SAND)
    c.rect(x + 24, y + 18, 56, 86, STEEL)
    for r in range(4):
        for col in range(3):
            c.rect(x + 30 + col * 17, y + 26 + r * 19, 10, 11, (255, 214, 64))
    # blast hole and cracks
    c.disc(x + 52, y + 52, 12, INK)
    c.line(x + 52, y + 40, x + 40, y + 26, INK)
    c.line(x + 52, y + 64, x + 64, y + 78, INK)
    c.line(x + 40, y + 52, x + 26, y + 46, INK)


def art_store(c, x, y, w, h):
    c.rect(x, y, w, h, PALE_ROSE)
    c.rect(x + 16, y + 44, 72, 60, INK)
    c.rect(x + 14, y + 26, 76, 20, INK)
    for i in range(6):
        c.rect(x + 16 + i * 12, y + 28, 12, 16, RED if i % 2 == 0 else PAPER)
    c.rect(x + 28, y + 62, 20, 42, PAPER)
    c.rect(x + 58, y + 62, 34, 24, SKY)


def art_scales(c, x, y, w, h):
    c.rect(x, y, w, h, PALE_BLUE)
    cx = x + w // 2
    c.rect(cx - 3, y + 22, 6, 62, NAVY)
    c.rect(cx - 26, y + 84, 52, 6, NAVY)
    c.line(cx - 34, y + 30, cx + 34, y + 30, NAVY)
    c.line(cx - 34, y + 30, cx - 44, y + 58, NAVY)
    c.line(cx - 34, y + 30, cx - 24, y + 58, NAVY)
    c.line(cx + 34, y + 30, cx + 24, y + 58, NAVY)
    c.line(cx + 34, y + 30, cx + 44, y + 58, NAVY)
    c.tri(cx - 48, y + 58, cx - 20, y + 58, cx - 34, y + 72, GOLD)
    c.tri(cx + 20, y + 58, cx + 48, y + 58, cx + 34, y + 72, GOLD)
    c.disc(cx, y + 18, 5, GOLD)


def art_virus(c, x, y, w, h):
    import math
    c.rect(x, y, w, h, PALE_ROSE)
    cx, cy = x + w // 2, y + h // 2
    for ang in range(0, 360, 30):
        r = math.radians(ang)
        c.line(cx + int(20 * math.cos(r)), cy + int(20 * math.sin(r)),
               cx + int(34 * math.cos(r)), cy + int(34 * math.sin(r)), RED)
        c.disc(cx + int(36 * math.cos(r)), cy + int(36 * math.sin(r)), 4, RED)
    c.disc(cx, cy, 20, RED)
    c.disc(cx - 7, cy - 6, 4, PAPER)
    c.disc(cx + 6, cy + 5, 3, PAPER)


# --- the page -----------------------------------------------------------------
def draw():
    c = Canvas(W, H, PAPER)

    # Masthead: navy band, paper name in bold display caps.
    c.rect(0, 0, W, 92, NAVY)
    title = "THE DAILY GLOBE"
    c.text((W - c.text_w(title, 6, bold=True)) // 2, 26, title, 6, PAPER, bold=True)
    # The red rule is the page's single accent: top and bottom frame.
    c.rect(0, 92, W, 4, RED)

    # Dateline: one plain line, date left, section right, no dot-joined meta.
    c.text(20, 106, "Tuesday, 24 November 2026", 2, INK)
    section = "World News"
    c.text(W - 20 - c.text_w(section, 2), 106, section, 2, INK)
    c.rect(20, 134, W - 40, 1, RULE)

    # Lead story: headline first, deck left, art right.
    lead_head = ["IRAN SAYS FOUR TANKERS HIT MINES", "IN THE STRAIT OF HORMUZ"]
    for line in lead_head:
        assert c.text_w(line, 5, bold=True) <= W - 40, line
    y = 148
    for line in lead_head:
        c.text(20, y, line, 5, INK, bold=True)
        y += 52
    deck = ("Iran's Revolutionary Guard says four oil tankers caught fire after "
            "striking naval mines in the strait, and a container ship was also "
            "hit, as Tehran confronts a US naval blockade. Brent crude settled "
            "at $91.40 a barrel.")
    lines = c.wrap(deck, 584, 3)
    assert 264 + (len(lines) - 1) * 30 + 21 <= 516, "lead deck runs into the rule"
    y = 264
    for line in lines:
        c.text(20, y, line, 3, INK)
        y += 30
    # lead art panel, bordered
    c.rect(624, 262, 380, 242, INK)
    art_hormuz(c, 626, 264, 376, 238)

    c.rect(20, 516, W - 40, 2, INK)

    # Six stories in two columns: art left, headline and deck right.
    stories = [
        ("HUAWEI FOUND GUILTY", "OF TRADE SECRETS",
         "A US jury convicts Huawei of trade secrets and bank fraud, but clears it of racketeering.",
         art_chip),
        ("ISRAEL KILLS HAMAS", "SECURITY CHIEF",
         "Hamas security chief Naeem Abu Nahel is killed with six others in a Gaza air strike.",
         art_skyline),
        ("ATTACK HITS FLATS", "IN ZAPORIZHZHIA",
         "An overnight attack kills two and wounds 40, including four children, the governor says.",
         art_flats),
        ("GUNMEN HOLD 25", "HOSTAGE IN CARTAGENA",
         "Armed men seize a supermarket in the Colombian port city, holding 25 people inside.",
         art_store),
        ("RIGHTS COURT BACKS", "MIGRANT EXPULSIONS",
         "Europe's human rights court says states may expel migrants during hybrid border emergencies.",
         art_scales),
        ("US LOSES MEASLES", "FREE STATUS",
         "The United States loses its measles elimination status after more than 25 years.",
         art_virus),
    ]
    col_x = [20, 522]
    row_y = [530, 662, 794]
    for i, (h1, h2, deck, art) in enumerate(stories):
        x = col_x[i % 2]
        y = row_y[i // 2]
        art(c, x, y, 104, 104)
        tx = x + 118
        assert c.text_w(h1, 3, bold=True) <= 366 and c.text_w(h2, 3, bold=True) <= 366, (h1, h2)
        c.text(tx, y + 2, h1, 3, INK, bold=True)
        c.text(tx, y + 29, h2, 3, INK, bold=True)
        dlines = c.wrap(deck, 366, 2)
        dy = y + 62
        for line in dlines:
            c.text(tx, dy, line, 2, INK)
            dy += 19
    # structural dividers: one vertical between columns, two horizontal rows
    c.rect(511, 530, 1, 392, RULE)
    c.rect(20, 660, W - 40, 1, RULE)
    c.rect(20, 792, W - 40, 1, RULE)

    # Bottom strip: navy band, four more items, divided by thin rules.
    c.rect(0, 934, W, 66, NAVY)
    strip = [
        "Turkish helicopter crash kills five",
        "Drone hits Riyadh tower, 11 hurt",
        "Houthis near Aden, ready to attack",
        "Sanofi buys Insmed in $41bn deal",
    ]
    for i, item in enumerate(strip):
        x = 20 + i * 246
        if i:
            c.rect(x - 12, 944, 1, 46, (90, 110, 140))
        slines = c.wrap(item, 222, 2)
        sy = 946 + max(0, (2 - len(slines))) * 10
        for line in slines:
            c.text(x, sy, line, 2, PAPER)
            sy += 19
    c.rect(0, 1000, W, 4, RED)

    return c


def main():
    canvas = draw()
    out = Path(__file__).with_name("entry.png")
    out.write_bytes(png_bytes(W, H, canvas.px))
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
