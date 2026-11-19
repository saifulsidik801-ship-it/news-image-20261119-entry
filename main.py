#!/usr/bin/env python3
"""Sum up Thursday 19 November 2026's world news in one image.

A Python 3.13 program, standard library only. It draws a newspaper front
page ("THE WORLD TODAY") with a hand-rolled 5x7 bitmap font and a small
zlib PNG encoder, and writes it to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png outside the grader). No network, no random
input, no timestamps: every run writes the same bytes.

The front page covers the day's biggest stories, as first reported on
19 November 2026:
  * WAR IN THE GULF - Iran fires drones at US bases in Kuwait (Ali Al
    Salem) and Bahrain (5th Fleet) after US jets strike an IRGC missile
    site on Qeshm Island in the Strait of Hormuz; Brent crude $92.70.
  * SHENZHEN SUMMIT - Trump, Xi and Putin meet for the first-ever
    three-way talks, on the sidelines of the APEC summit.
  * VICE CITY OPENS - Grand Theft Auto VI rolls out worldwide at
    midnight local time, 13 years after GTA V, on PS5 and Xbox.
  * ONE LIGHT-DAY - NASA confirms Voyager 1 has reached one light-day
    from Earth, a new distance record.
Also in the ticker: Israel's ground operation in central Gaza, the
Crimea bridge attacked again, and the EU's proposed 45bn Ukraine loan.
"""
import os
import struct
import zlib

W = H = 1024

# 5x7 bitmap font: each glyph is 7 rows of 5 "0"/"1" characters.
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
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "'": ("00100", "00100", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
}

INK = (17, 17, 17)
PAPER = (247, 242, 231)
RED = (185, 28, 28)
BLUE = (29, 78, 216)
WHITE = (255, 255, 255)
SEA = (186, 220, 235)
LAND = (232, 214, 170)
GOLD = (217, 119, 6)


class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def fill(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:base + len(row)] = row

    def pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            base = (y * self.w + x) * 3
            self.px[base:base + 3] = bytes(color)

    def rect(self, x, y, w, h, color, t=1):
        self.fill(x, y, w, t, color)
        self.fill(x, y + h - t, w, t, color)
        self.fill(x, y, t, h, color)
        self.fill(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.fill(cx - dx, yy, dx * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= t / 2 + 0.5:
                    self.pixel(xx, yy, color)

    def arrow(self, x0, y0, x1, y1, color, t=3):
        self.line(x0, y0, x1, y1, color, t)
        dx = x1 - x0
        dy = y1 - y0
        ln = max(1, (dx * dx + dy * dy) ** 0.5)
        ux, uy = dx / ln, dy / ln
        hx, hy = -uy, ux
        s = 14
        bx, by = int(x1 - ux * s), int(y1 - uy * s)
        for t in range(-7, 8):
            self.line(bx + int(hx * t), by + int(hy * t), x1, y1, color, 1)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "1":
                    cv.fill(cx + col_i * scale, y + row_i * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def draw_center(cv, y, s, scale, color, cx=512):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_w, scale):
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, color, max_w, lh=None):
    lh = lh or (9 * scale)
    for line in wrap(s, max_w, scale):
        draw_text(cv, x, y, line, scale, color)
        y += lh
    return y


def png_bytes(cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def gulf_map(cv, x, y, w, h):
    """Schematic map of the Gulf: Iran top-right, Arabia below, the water
    channel between them, Qeshm Island in the Strait of Hormuz, and the
    night's exchanges drawn as arrows."""
    cv.fill(x, y, w, h, SEA)
    # Iran: land mass top-right.
    cv.fill(x + int(w * 0.52), y, int(w * 0.48), int(h * 0.46), LAND)
    # Arabian peninsula: land mass bottom.
    cv.fill(x + int(w * 0.08), y + int(h * 0.62), int(w * 0.84), int(h * 0.38), LAND)
    # Iraq / Kuwait corner top-left.
    cv.fill(x, y, int(w * 0.30), int(h * 0.30), LAND)
    # The Gulf: a diagonal water channel between Iran and Arabia.
    cv.line(x + int(w * 0.30), y + int(h * 0.30), x + int(w * 0.62),
            y + int(h * 0.62), SEA, 26)
    # Strait of Hormuz narrows at the channel's lower end.
    cv.line(x + int(w * 0.62), y + int(h * 0.62), x + int(w * 0.78),
            y + int(h * 0.72), SEA, 12)
    # Qeshm Island: red island in the strait.
    qx, qy = x + int(w * 0.68), y + int(h * 0.66)
    cv.disc(qx, qy, 16, RED)
    cv.ring(qx, qy, 24, RED, 3)
    # Kuwait: US base Ali Al Salem.
    kx, ky = x + int(w * 0.34), y + int(h * 0.34)
    cv.disc(kx, ky, 9, WHITE)
    cv.ring(kx, ky, 13, INK, 2)
    # Bahrain: home of the US 5th Fleet.
    bx, by = x + int(w * 0.44), y + int(h * 0.56)
    cv.disc(bx, by, 9, WHITE)
    cv.ring(bx, by, 13, INK, 2)
    # Red drone arrows: Iran -> Kuwait and Iran -> Bahrain.
    cv.arrow(x + int(w * 0.56), y + int(h * 0.40), kx + 16, ky - 6, RED, 4)
    cv.arrow(x + int(w * 0.58), y + int(h * 0.48), bx + 16, by - 4, RED, 4)
    # Gold jet arrow: from the sea -> Qeshm (the US strike).
    cv.arrow(x + int(w * 0.86), y + int(h * 0.86), qx + 18, qy + 10, GOLD, 4)
    draw_text(cv, x + int(w * 0.56), y + 10, "IRAN", 3, INK)
    draw_text(cv, x + 10, y + 10, "IRAQ", 2, INK)
    draw_text(cv, kx - 96, ky - 34, "KUWAIT", 3, RED)
    draw_text(cv, bx - 110, by + 22, "BAHRAIN", 3, RED)
    draw_text(cv, qx - 40, qy - 46, "QESHM ISLAND", 2, RED)
    draw_text(cv, x + w - text_w("STRAIT OF HORMUZ", 2) - 10, y + h - 30,
              "STRAIT OF HORMUZ", 2, INK)
    draw_text(cv, x + int(w * 0.30), y + h - 56, "SAUDI ARABIA", 2, INK)


def build_front_page():
    cv = Canvas(bg=PAPER)
    cv.rect(20, 20, 984, 984, INK, 4)
    cv.rect(30, 30, 964, 964, INK, 1)
    draw_center(cv, 46, "THE WORLD TODAY", 7, INK)
    cv.fill(48, 116, 928, 4, INK)
    draw_center(cv, 130, "THURSDAY 19 NOVEMBER 2026", 3, RED)
    cv.fill(48, 168, 928, 2, INK)
    draw_center(cv, 182, "WAR IN THE GULF", 3, RED)
    draw_center(cv, 212, "IRAN STRIKES BACK", 6, INK)
    draw_center(cv, 258, "AT US GULF BASES", 6, INK)
    draw_center(cv, 312, "US JETS HIT MISSILE SITE", 3, INK)
    draw_center(cv, 338, "ON IRAN'S QESHM ISLAND", 3, INK)
    # Map panel.
    cv.rect(48, 376, 928, 272, INK, 3)
    gulf_map(cv, 51, 379, 922, 266)
    draw_text(cv, 66, 654, "IRANIAN DRONES TARGET US BASES IN KUWAIT AND BAHRAIN",
              2, INK)
    # Oil tag.
    cv.fill(700, 388, 258, 30, INK)
    draw_text(cv, 712, 394, "BRENT OIL $92.70", 2, WHITE)
    # Three story columns.
    cols = [
        ("SHENZHEN SUMMIT", "TRUMP, XI AND PUTIN MEET",
         "FIRST-EVER THREE-WAY TALKS AT APEC", BLUE),
        ("VICE CITY OPENS", "GTA VI ROLLS OUT WORLDWIDE",
         "AFTER 13 YEARS - PS5 AND XBOX", (190, 24, 120)),
        ("ONE LIGHT-DAY", "VOYAGER 1 SETS DISTANCE RECORD",
         "NASA CONFIRMS MILESTONE TODAY", (4, 120, 87)),
    ]
    for i, (kick, head, sub, col) in enumerate(cols):
        cx = 48 + i * 316
        cv.rect(cx, 680, 296, 252, INK, 2)
        cv.fill(cx, 680, 296, 8, col)
        draw_text(cv, cx + 14, 704, kick, 2, RED)
        draw_para(cv, cx + 14, 736, head, 3, INK, 268, 30)
        draw_para(cv, cx + 14, 826, sub, 2, (70, 70, 70), 268, 22)
        # Simple icon strip at the bottom of each column.
        if i == 0:
            for j, c in enumerate([(178, 34, 34), (222, 0, 0), (0, 60, 160)]):
                cv.fill(cx + 14 + j * 92, 888, 84, 30, c)
        elif i == 1:
            for j, hh in enumerate([26, 40, 32, 48, 22]):
                cv.fill(cx + 14 + j * 54, 918 - hh, 44, hh,
                        (190, 24, 120) if j % 2 else (0, 180, 200))
            cv.disc(cx + 248, 874, 16, GOLD)
        else:
            cv.disc(cx + 40, 894, 8, GOLD)
            cv.disc(cx + 90, 878, 5, GOLD)
            cv.disc(cx + 150, 900, 6, GOLD)
            cv.disc(cx + 220, 882, 18, WHITE)
            cv.ring(cx + 220, 882, 18, (4, 120, 87), 2)
            cv.line(cx + 232, 882, cx + 268, 882, (4, 120, 87), 2)
    # Bottom ticker.
    cv.fill(48, 960, 928, 40, INK)
    draw_text(cv, 62, 972,
              "ALSO TODAY: GAZA GROUND OP - CRIMEA BRIDGE HIT - EU 45BN UKRAINE LOAN",
              2, WHITE)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build_front_page())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
