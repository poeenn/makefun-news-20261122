"""Sum up 22 November 2026's world news in one image.

Entry for make.fun's news-image-20261122 bounty. Python 3.13, standard
library only, no network. Draws a one-page English newspaper front page
for Sunday 22 November 2026 onto a 1024x1024 canvas and writes it as a
PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png). The drawing
uses only fixed data and integer geometry, so two runs write the same
bytes.
"""
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 242, 231)
CARD = (253, 251, 245)
INK = (23, 27, 38)
RED = (176, 32, 40)
BLUE = (28, 66, 124)
TEAL = (24, 104, 110)
GOLD = (186, 132, 34)
GREY = (96, 96, 92)
LIGHT = (224, 216, 196)
SEA = (86, 132, 168)
SMOKE = (128, 128, 124)
SKIN = (216, 168, 128)

BUF = bytearray(W * H * 3)


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i:i + 3] = bytes(color)


def fill_rect(x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, color)


def fill_circle(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, color)


def ring(cx, cy, r, thick, color):
    lo = (r - thick) * (r - thick)
    hi = r * r
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
            if lo <= d <= hi:
                px(xx, yy, color)


def line(x0, y0, x1, y1, thick, color):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    r = max(thick // 2, 1)
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i // steps
        y = y0 + (y1 - y0) * i // steps
        fill_circle(x, y, r, color)


def polygon(points, color):
    ys = [p[1] for p in points]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= yy < y1) or (y1 <= yy < y0):
                xs.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            fill_rect(xs[i], yy, xs[i + 1] - xs[i] + 1, 1, color)


# A 5x7 bitmap font, drawn by hand for this entry. Text is upper case.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##."),
    "(": ("...#.", "..#..", "..#..", "..#..", "..#..", "..#..", "...#."),
    ")": (".#...", "..#..", "..#..", "..#..", "..#..", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, color):
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "#":
                    fill_rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(y, s, scale, color):
    draw_text((W - text_width(s, scale)) // 2, y, s, scale, color)


def wrap(s, scale, max_width):
    words = s.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, scale, color, max_width, leading):
    for ln in wrap(s, scale, max_width):
        draw_text(x, y, ln, scale, color)
        y += leading
    return y


# --- Small pictograms, one per story, drawn with the helpers above. ---

def icon_globe_crack(x, y):
    ring(x + 45, y + 45, 34, 5, TEAL)
    line(x + 18, y + 30, x + 72, y + 30, 3, TEAL)
    line(x + 18, y + 60, x + 72, y + 60, 3, TEAL)
    line(x + 45, y + 11, x + 45, y + 79, 3, TEAL)
    pts = [(48, 14), (40, 30), (52, 42), (42, 58), (50, 76)]
    for i in range(len(pts) - 1):
        line(x + pts[i][0], y + pts[i][1], x + pts[i + 1][0], y + pts[i + 1][1], 5, RED)


def icon_tanker(x, y):
    polygon([(x + 8, y + 58), (x + 82, y + 58), (x + 74, y + 74), (x + 18, y + 74)], INK)
    fill_rect(x + 20, y + 46, 44, 12, RED)
    fill_rect(x + 66, y + 38, 8, 20, INK)
    fill_rect(x + 28, y + 34, 16, 12, GOLD)
    for wx in (6, 30, 54):
        line(x + wx, y + 84, x + wx + 14, y + 84, 4, SEA)
        line(x + wx + 4, y + 90, x + wx + 18, y + 90, 4, SEA)
    for dx, dy in ((0, -9), (7, -6), (9, 2), (6, 8)):
        line(x + 78, y + 14, x + 78 + dx, y + 14 + dy, 4, RED)
    fill_circle(x + 78, y + 14, 4, GOLD)


def icon_building(x, y):
    fill_rect(x + 22, y + 10, 48, 76, GREY)
    for r in range(4):
        for c in range(3):
            fill_rect(x + 29 + c * 14, y + 18 + r * 17, 8, 10, LIGHT)
    polygon([(x + 58, y + 10), (x + 70, y + 10), (x + 70, y + 40), (x + 50, y + 30)], INK)
    fill_circle(x + 62, y + 6, 7, SMOKE)
    fill_circle(x + 72, y + 2, 5, SMOKE)
    line(x + 30, y + 52, x + 44, y + 66, 4, RED)
    line(x + 44, y + 52, x + 30, y + 66, 4, RED)


def icon_capitol(x, y):
    polygon([(x + 45, y + 8), (x + 70, y + 38), (x + 20, y + 38)], BLUE)
    fill_rect(x + 43, y + 0, 4, 10, BLUE)
    fill_rect(x + 14, y + 38, 62, 6, BLUE)
    for c in range(5):
        fill_rect(x + 18 + c * 13, y + 48, 6, 26, BLUE)
    fill_rect(x + 12, y + 76, 66, 6, BLUE)
    fill_circle(x + 45, y + 30, 5, GOLD)


def icon_ship_smoke(x, y):
    polygon([(x + 6, y + 56), (x + 84, y + 56), (x + 76, y + 72), (x + 16, y + 72)], RED)
    fill_rect(x + 34, y + 42, 26, 14, INK)
    fill_rect(x + 40, y + 30, 6, 12, INK)
    fill_circle(x + 46, y + 22, 7, SMOKE)
    fill_circle(x + 56, y + 14, 9, SMOKE)
    fill_circle(x + 68, y + 8, 6, SMOKE)
    for wx in (4, 32, 60):
        line(x + wx, y + 82, x + wx + 16, y + 82, 4, SEA)


def icon_boat(x, y):
    polygon([(x + 10, y + 52), (x + 80, y + 52), (x + 68, y + 70), (x + 24, y + 70)], GOLD)
    line(x + 45, y + 52, x + 45, y + 16, 4, INK)
    polygon([(x + 45, y + 18), (x + 45, y + 46), (x + 66, y + 46)], PAPER)
    for hx in (28, 42, 56):
        fill_circle(x + hx, y + 44, 5, SKIN)
    for wx in (6, 34, 62):
        line(x + wx, y + 80, x + wx + 15, y + 80, 4, SEA)
        line(x + wx + 3, y + 87, x + wx + 18, y + 87, 4, SEA)


ICONS = {
    "globe": icon_globe_crack,
    "tanker": icon_tanker,
    "building": icon_building,
    "capitol": icon_capitol,
    "ship": icon_ship_smoke,
    "boat": icon_boat,
}

# The day's stories, as reported on 22 November 2026 (see README).
LEAD = {
    "icon": "globe",
    "kicker": "CLIMATE - ANTALYA, TURKIYE",
    "headline": "COP31 TALKS COLLAPSE WITH NO DEAL",
    "body": "The UN climate summit ended two days into overtime after the EU "
            "and island states rejected a draft that never mentioned fossil "
            "fuels. Nations failed to agree a final text on cutting the "
            "emissions that are heating the planet.",
}
PANELS = [
    {
        "icon": "tanker",
        "kicker": "MIDDLE EAST - BAHRAIN",
        "headline": "IRAN HITS BAHRAIN AND TANKERS",
        "body": "An Iranian attack damaged a Bahrain industrial site, "
                "wounding two, as tankers were struck near the Strait "
                "of Hormuz.",
    },
    {
        "icon": "building",
        "kicker": "UKRAINE - DYMER",
        "headline": "STRIKE COLLAPSES FLATS",
        "body": "A Russian strike partly collapsed an apartment block in "
                "Dymer, near Kyiv, killing 2 people and wounding 4.",
    },
    {
        "icon": "capitol",
        "kicker": "US POLITICS - WASHINGTON",
        "headline": "DEMOCRATS CLINCH 258 SEATS",
        "body": "A North Carolina win on Sunday gave Democrats their "
                "largest House majority since 1992. Four races are "
                "still uncalled.",
    },
    {
        "icon": "ship",
        "kicker": "LIBYA - BENGHAZI PORT",
        "headline": "EXPLOSION DAMAGES RUSSIAN SHIP",
        "body": "A Russian vessel docked at Benghazi was damaged. Officials "
                "suspect a drone attack; a second ship was also hit.",
    },
]
WIDE = {
    "icon": "boat",
    "kicker": "AFRICA - NIGERIA",
    "headline": "BOAT CAPSIZES IN NIGERIA: 24 DEAD",
    "body": "A boat taking people to a funeral capsized, and the death toll "
            "rose to at least 24 as rescuers searched the river.",
}
BRIEFS = ("IN BRIEF - MEXICO: SPECIAL FORCES CAPTURE CARTEL BOSS "
          "'EL CHAPO ISIDRO' IN SINALOA. INDONESIA: CANDY-FACTORY FIRE "
          "KILLS 3, WITH 37 WORKERS MISSING. MARKETS: STOCKS SLIDE AS THE "
          "AI SELL-OFF DEEPENS, S&P 500 -3.7%, NIKKEI -5.1%. WEST BANK: "
          "SETTLERS TORCH VEHICLES NEAR RAMALLAH.")


def panel(x, y, w, h, story, headline_scale, body_scale):
    fill_rect(x, y, w, h, CARD)
    for t in range(3):
        fill_rect(x, y + t, w, 1, INK)
        fill_rect(x, y + h - 1 - t, w, 1, INK)
        fill_rect(x + t, y, 1, h, INK)
        fill_rect(x + w - 1 - t, y, 1, h, INK)
    ICONS[story["icon"]](x + 14, y + 16)
    tx = x + 118
    tw = x + w - 16 - tx
    draw_text(tx, y + 14, story["kicker"], 2, RED)
    yy = draw_wrapped(tx, y + 34, story["headline"], headline_scale, INK,
                      tw, 7 * headline_scale + 3)
    draw_wrapped(tx, yy + 8, story["body"], body_scale, INK, tw,
                 7 * body_scale + 3)


def draw_page():
    fill_rect(0, 0, W, H, PAPER)
    # Masthead.
    fill_rect(0, 0, W, 14, RED)
    draw_centered(30, "THE WORLD IN ONE DAY", 7, INK)
    draw_centered(96, "SUNDAY, 22 NOVEMBER 2026", 4, RED)
    fill_rect(36, 138, W - 72, 4, INK)
    draw_text(36, 150, "ONE IMAGE, THE WHOLE DAY", 2, GREY)
    r = "ALL TIMES AND PLACES, ONE PAGE"
    draw_text(W - 36 - text_width(r, 2), 150, r, 2, GREY)
    fill_rect(36, 172, W - 72, 2, INK)
    # Lead story.
    panel(36, 186, W - 72, 190, LEAD, 4, 2)
    # Four panels in a 2x2 grid.
    pw = (W - 72 - 16) // 2
    for i, story in enumerate(PANELS):
        panel(36 + (i % 2) * (pw + 16), 392 + (i // 2) * 204, pw, 190, story, 3, 2)
    # Wide bottom story.
    wy = 806
    fill_rect(36, wy, W - 72, 100, CARD)
    for t in range(3):
        fill_rect(36, wy + t, W - 72, 1, INK)
        fill_rect(36, wy + 100 - 1 - t, W - 72, 1, INK)
        fill_rect(36 + t, wy, 1, 100, INK)
        fill_rect(36 + W - 72 - 1 - t, wy, 1, 100, INK)
    ICONS[WIDE["icon"]](50, wy + 5)
    draw_text(154, wy + 10, WIDE["kicker"], 2, RED)
    draw_text(154, wy + 32, WIDE["headline"], 3, INK)
    draw_wrapped(154, wy + 62, WIDE["body"], 2, INK, W - 72 - 118 - 36, 17)
    # Briefs strip.
    fill_rect(36, 918, W - 72, 3, RED)
    draw_wrapped(36, 930, BRIEFS, 2, INK, W - 72, 17)


def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += BUF[yy * W * 3:(yy + 1) * W * 3]

    def chunk(ctype, body):
        return (struct.pack(">I", len(body)) + ctype + body
                + struct.pack(">I", zlib.crc32(ctype + body) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    draw_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png_bytes())


if __name__ == "__main__":
    main()
