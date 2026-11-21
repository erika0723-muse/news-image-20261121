#!/usr/bin/env python3
"""Render the entry image: one day's world news as a newspaper front page.

Production script (runs on the build machine, needs Pillow).
It draws assets/entry.png, which main.py then ships verbatim.

Design goals, following the competition's judging criteria:
  * the date is named, large: FRIDAY 20 NOVEMBER 2026
  * the day's most consequential stories, across regions and fields
  * readable from the image alone: short headline + one-line explainer each
  * clean, flat rendering, no generated imagery, no garbled text
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_REG = os.path.join(HERE, "fonts", "DejaVuSans.ttf")
FONT_BOLD = os.path.join(HERE, "fonts", "DejaVuSans-Bold.ttf")
OUT = os.path.join(HERE, "assets", "entry.png")

W = H = 1024
MARGIN = 36
CW = W - 2 * MARGIN  # content width = 952

PAPER = (247, 243, 234)
INK = (24, 24, 24)
GRAY = (92, 88, 80)
RULE = (176, 168, 152)
RED = (168, 35, 26)
NAVY = (31, 78, 121)
TEAL = (16, 96, 96)
BROWN = (133, 77, 20)
PURPLE = (94, 53, 130)
LEAD_BG = (246, 231, 222)
BODY = (52, 48, 44)


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, text, fnt, fill, max_w, leading):
    """Draw wrapped text, return y after the block."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centered(draw, y, text, fnt, fill):
    w_ = draw.textlength(text, font=fnt)
    draw.text(((W - w_) / 2, y), text, font=fnt, fill=fill)


def fit_font(draw, text, start_size, max_w, bold=True):
    size = start_size
    while size > 10 and draw.textlength(text, font=font(size, bold)) > max_w:
        size -= 2
    return font(size, bold)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- masthead
y = 20
centered(d, y, "T H E   W O R L D   I N   O N E   I M A G E", font(27, True), INK)
y += 40
d.rectangle([MARGIN, y, W - MARGIN, y + 5], fill=INK)
y += 9
d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=2)
y += 13
date_text = "FRIDAY 20 NOVEMBER 2026"
date_fnt = fit_font(d, date_text, 62, CW)
centered(d, y, date_text, date_fnt, INK)
y += 74
centered(
    d,
    y,
    "The day's biggest stories — war, markets, courts, diplomacy and disaster",
    font(21),
    GRAY,
)
y += 32
d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=2)
y += 5
d.rectangle([MARGIN, y, W - MARGIN, y + 4], fill=INK)
y += 16

# ---------------------------------------------------------------- lead story
lead_top = y
lead_h = 246
d.rectangle([MARGIN, lead_top, W - MARGIN, lead_top + lead_h], fill=LEAD_BG)
d.rectangle([MARGIN, lead_top, MARGIN + 10, lead_top + lead_h], fill=RED)
lx = MARGIN + 30
lw = CW - 30 - 22
ly = lead_top + 16
d.text((lx, ly), "EUROPE — WAR", font=font(23, True), fill=RED)
ly += 35
ly = block(
    d,
    lx,
    ly,
    "Russian Missiles Land in Poland as Kyiv Bridges Are Hit",
    font(45, True),
    INK,
    lw,
    52,
)
ly += 7
block(
    d,
    lx,
    ly,
    "Missiles and drones fell inside NATO member Poland; Warsaw called it a "
    "deliberate provocation and NATO a grave violation of airspace. The same "
    "night, Russia struck three Dnipro bridges and the embassy district in Kyiv.",
    font(21),
    BODY,
    lw,
    27,
)
y = lead_top + lead_h + 14

# ---------------------------------------------------------------- grid
stories = [
    (
        "GLOBAL MARKETS",
        NAVY,
        "AI Sell-Off Pounds World Stocks",
        "S&P 500 falls 3.7% into correction; Tokyo's Nikkei dives 5.1% "
        "on AI spending fears.",
    ),
    (
        "THE HAGUE — WORLD COURT",
        PURPLE,
        "ICJ: Myanmar Committed Genocide",
        "World court finds the Rohingya crackdown was genocide; "
        "reparations ordered.",
    ),
    (
        "DIPLOMACY — SHENZHEN",
        TEAL,
        "US, China & Russia Issue Peace Pledge",
        "Trump, Xi and Putin vow no nuclear war; Germany's Merz "
        "rejects a 'new Yalta'.",
    ),
    (
        "MIDDLE EAST",
        RED,
        "Houthi Missile Hits Riyadh Skyscraper",
        "Second strike this month on the financial district blows out "
        "eight floors of windows.",
    ),
    (
        "PERU — DISASTER",
        BROWN,
        "Magnitude 6.7 Quake Hits Central Peru",
        "Buildings and roads damaged near Cerro de Pasco; injuries reported.",
    ),
    (
        "INDIA — WEATHER",
        TEAL,
        "Cyclone Akban Makes Landfall",
        "Mass evacuations and cancelled trains as the storm hits "
        "India's east coast.",
    ),
    (
        "NIGERIA — DISASTER",
        BROWN,
        "Funeral Boat Capsizes in Bayelsa",
        "A vessel carrying mourners overturns in southern Nigeria.",
    ),
    (
        "UNITED STATES",
        NAVY,
        "Trump Fires National Cyber Director",
        "Ousted amid outages and a breach exposing data of "
        "16,000 bank customers.",
    ),
]

gap = 20
col_w = (CW - gap) // 2
rows = 4
grid_top = y
grid_bottom = H - 24
row_h = (grid_bottom - grid_top) // rows

# candidate (headline size, headline leading, sub size, sub leading), largest first
CELL_FITS = [(27, 32, 19, 23), (26, 30, 18, 22), (24, 28, 17, 20), (22, 26, 16, 19)]
KICKER_SIZE, KICKER_LEAD, CELL_PAD = 18, 25, 10


def cell_height(head, sub, hs, hl, ss, sl):
    h_lines = len(wrap(d, head, font(hs, True), col_w))
    s_lines = len(wrap(d, sub, font(ss), col_w))
    return CELL_PAD + KICKER_LEAD + h_lines * hl + 3 + s_lines * sl


for i, (kicker, color, head, sub) in enumerate(stories):
    cx = MARGIN + (i % 2) * (col_w + gap)
    cy = grid_top + (i // 2) * row_h
    hs, hl, ss, sl = CELL_FITS[-1]
    for cand in CELL_FITS:
        if cell_height(head, sub, *cand) <= row_h:
            hs, hl, ss, sl = cand
            break
    d.line([cx, cy, cx + col_w, cy], fill=RULE, width=2)
    ty = cy + CELL_PAD
    d.text((cx, ty), kicker, font=font(KICKER_SIZE, True), fill=color)
    ty += KICKER_LEAD
    ty = block(d, cx, ty, head, font(hs, True), INK, col_w, hl)
    ty += 3
    block(d, cx, ty, sub, font(ss), BODY, col_w, sl)

# ---------------------------------------------------------------- footer
foot_y = grid_bottom - 14
d.line([MARGIN, foot_y - 12, W - MARGIN, foot_y - 12], fill=INK, width=2)
centered(
    d,
    foot_y,
    "All stories as reported on Friday, 20 November 2026",
    font(17),
    GRAY,
)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT, format="PNG", optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
