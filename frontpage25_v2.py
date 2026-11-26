#!/usr/bin/env python3
"""frontpage25_v2.py — draw the news-image-20261125 v2 entry (fresh build).

Wednesday 25 November 2026, one serif newspaper front page, 1024x1024.
Built from the v2 dossier (research/stories-v2.md + research/fix-list-v2.md):
38 stories / 7 regions / 20 fields, 3 heroes (kept), 10 cards, 25 briefs,
numbers strip, dot-matrix world map with pins 1-13, DATE CHECK strip.

Deterministic: no clock, no randomness, no network. Run:
    python3 frontpage25_v2.py            # writes entry.png next to this file
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
M = 16                      # outer margin
CW = W - 2 * M              # 992 content width

# ---------------------------------------------------------------- palette
PAPER   = (247, 241, 227)   # warmer paper tone (WOW)
INK     = (26, 22, 18)
GREY    = (90, 84, 76)
LGREY   = (150, 142, 130)
RED     = (178, 34, 34)     # masthead red
DRED    = (140, 22, 22)     # darker red dek (W3)
GOLD    = (196, 141, 28)
GOLD_L  = (212, 160, 23)
CREAM   = (250, 246, 236)
NAVY    = (16, 32, 64)
TEAL_D  = (13, 60, 74)

REGION = {  # name -> (tab colour, kicker colour)
    "EUROPE":         ((43, 108, 176), (43, 108, 176)),
    "MIDDLE EAST":    ((14, 124, 123), (14, 124, 123)),
    "AFRICA":         ((201, 110, 8),  (176, 96, 6)),
    "ASIA-PACIFIC":   ((178, 52, 52),  (178, 52, 52)),
    "OCEANIA":        ((110, 84, 160), (110, 84, 160)),
    "AMERICAS":       ((178, 32, 92),  (178, 32, 92)),
    "WORLD & SCIENCE": ((93, 109, 126), (93, 109, 126)),
}

PILL = {  # certainty pill -> (bg, fg)
    "OFFICIAL":  ((14, 124, 123), (255, 255, 255)),
    "CONFIRMED": ((30, 125, 50),  (255, 255, 255)),
    "REPORTED":  ((178, 52, 52),  (255, 255, 255)),
    "CLAIM":     ((176, 124, 20), (255, 255, 255)),
}

# ---------------------------------------------------------------- fonts
FDIR = "/usr/share/fonts/truetype/liberation"
_cache = {}
def F(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(os.path.join(FDIR, name), size)
    return _cache[key]

def serif_b(s):  return F("LiberationSerif-Bold.ttf", s)
def serif_i(s):  return F("LiberationSerif-Italic.ttf", s)
def serif_bi(s): return F("LiberationSerif-BoldItalic.ttf", s)
def serif(s):    return F("LiberationSerif-Regular.ttf", s)
def sans_b(s):   return F("LiberationSans-Bold.ttf", s)
def sans(s):     return F("LiberationSans-Regular.ttf", s)

# ---------------------------------------------------------------- helpers
def tw(draw, text, font):
    return draw.textlength(text, font=font)

def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines (never empty)."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if tw(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines or [""]

def fit_lines(draw, text, font, max_w, max_lines, min_size, fname):
    """Shrink font until text wraps to <= max_lines. Returns (font, lines)."""
    size = font.size
    while size > min_size:
        f = F(fname, size)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines and all(tw(draw, l, f) <= max_w for l in lines):
            return f, lines
        size -= 1
    f = F(fname, min_size)
    return f, wrap(draw, text, f, max_w)

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def pill(d, x, y, text, kind, size=9):
    """Certainty pill; returns width used. Top-left anchored at (x, y)."""
    bg, fg = PILL[kind]
    f = sans_b(size)
    w = int(tw(d, text, f)) + 12
    h = size + 8
    rrect(d, [x, y, x + w, y + h], r=h // 2, fill=bg)
    d.text((x + 6, y + 4), text, font=f, fill=fg)
    return w

def pin_badge(d, x, y, num, r=9):
    """Red numbered pin badge, centred at (x, y)."""
    d.ellipse([x - r, y - r, x + r, y + r], fill=(178, 34, 34),
              outline=(255, 255, 255), width=2)
    f = sans_b(10)
    t = str(num)
    d.text((x - tw(d, t, f) / 2, y - 7), t, font=f, fill=(255, 255, 255))

def scene_bar(d, w, h, text, size=11):
    """Bottom red caption bar inside a scene. Text left-aligned so a pill
    can sit at the bottom-right without covering it."""
    bh = size + 10
    d.rectangle([0, h - bh, w, h], fill=(178, 34, 34))
    f = sans_b(size)
    d.text((10, h - bh + 5), text, font=f, fill=(255, 255, 255))

def new_scene(w, h, bg):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)

# =====================================================================
# CONTENT — every figure/date traced to stories-v2.md (see v2-spec-summary)
# =====================================================================

TOPLINE_L = "ONE DAY OF WORLD NEWS"
TOPLINE_R = "38 STORIES \u00b7 7 REGIONS \u00b7 20 FIELDS \u00b7 EVERY ONE FROM WEDNESDAY 25 NOVEMBER 2026"
MASTHEAD = "Wednesday 25 November 2026"
DEK = ("US proposes tariffs on 14 partners \u00b7 Shenzhou-24 launches with first "
       "foreign astronaut \u00b7 Judges urge Netanyahu bribery case dropped")

TABS = [("EUROPE", 8), ("MIDDLE EAST", 5), ("AFRICA", 5), ("ASIA-PACIFIC", 5),
        ("OCEANIA", 2), ("AMERICAS", 7), ("WORLD & SCIENCE", 6)]

NUMBERS = [
    ("WASHINGTON", "14",     "partners hit by new tariffs"),
    ("CHINA",      "20%",    "top tariff rate proposed"),
    ("GIZA",       "31",     "killed in fuel-tanker fire"),
    ("LONDON",     "$94.61", "Brent close Wed (+3.5%)"),
    ("SEOUL",      "\u22126.2%", "Kospi fall in a day"),
    ("US \u00b7 OCTOBER", "3.8%", "PCE inflation, year on year"),
]

# heroes: (num, kicker, pill, headline, deck, bar)
HEROES = [
    (1, "WASHINGTON \u00b7 TRADE", "OFFICIAL",
     "US proposes new tariffs on 14 trading partners",
     "China 20% top rate; Vietnam 20% if a deal, 35% if talks fail; "
     "Singapore 10%. Hearing 25 Jan. Reuters, USTR",
     "NEW TARIFFS \u00b7 14 PARTNERS"),
    (2, "JIUQUAN \u00b7 SPACE", "CONFIRMED",
     "Shenzhou-24 launches, first foreign astronaut",
     "Pakistan\u2019s Zeeshan Ali, 40, joins the Tiangong crew for 5\u201310 days. "
     "Xinhua, Aviation Week",
     "FIRST FOREIGN ASTRONAUT"),
    (3, "JERUSALEM \u00b7 COURTS", "CONFIRMED",
     "Judges urge Netanyahu bribery case be dropped",
     "Case 4000 drop recommended; Case 2000 reconsidered. Not a ruling. "
     "Reuters, CNN",
     "JUDGES URGE CASE DROPPED"),
]

# cards: (num, place, region, pill, headline, deck)
CARDS = [
    (4, "GIZA", "AFRICA", "CONFIRMED",
     "Fuel tanker blast in Giza kills 31",
     "27 vehicles burned; toll rose from 21 overnight. Reuters, CNN"),
    (5, "CANBERRA", "OCEANIA", "OFFICIAL",
     "Solomon picks Australia, bars foreign bases",
     "A$740m over 10 years; China pact ends Apr 2027. AP, CNN, ASPI"),
    (6, "DHAKA", "ASIA-PACIFIC", "CONFIRMED",
     "Bangladesh lifts garment wage 36%",
     "Minimum 17,000 taka; smallest rise since 1986 \u2014 protests follow. AP, AFP, CCC"),
    (7, "DAMAZIN", "AFRICA", "REPORTED",
     "RSF drone strike kills 19 in Blue Nile",
     "Reported Wed; 19 dead in Damazin, 20 hurt. Reuters"),
    (8, "POLAND", "EUROPE", "OFFICIAL",
     "Poland plans no-fly zone on east border",
     "Tens of km wide; rules due by early January. Reuters"),
    (9, "JEDDAH", "MIDDLE EAST", "REPORTED",
     "Houthis threaten Jeddah port; Hodeidah hit",
     "Coalition bombs Hodeidah; 4 drones downed. Reuters"),
    (10, "RAS TANURA", "MIDDLE EAST", "CLAIM",
     "Houthis claim Ras Tanura refinery strike",
     "Brent closes $94.61, +3.5%; claim unverified. Reuters"),
    (11, "SAVASLEYKA", "EUROPE", "REPORTED",
     "Ukraine hits Savasleyka: 5 jets damaged",
     "3 MiG-31s, 2 Su-34s hit 680 km inside Russia. Reuters"),
    (12, "GAZA CITY", "MIDDLE EAST", "CONFIRMED",
     "Israel kills Hamas security chief in Gaza",
     "Abu al-Aouf dies with family in Al-Shati strike. CNN, IDF"),
    (13, "NEW YORK", "AMERICAS", "CONFIRMED",
     "Dow swings +0.33% after 1,100-point dive",
     "S&P \u22120.25%, Nasdaq \u22120.62%; Nvidia \u22124%. Reuters"),
]

# briefs 14-38: (num, region, BOLD lead, rest incl. source)
# W2: key fact first in bold 12px, body 10.5px after; single line each.
BRIEFS = [
    (14, "EUROPE", "Kyiv hit late Wed; 4 hurt", "(Klitschko)"),
    (15, "EUROPE", "UCL: PSG 2-2 Roma; Bayern 1-2 Lille", "(UEFA)"),
    (16, "EUROPE", "Macron threatens EU budget walkout", "(AP)"),
    (17, "EUROPE", "Kyiv hits 2 Russia refineries", "(ISW)"),
    (18, "EUROPE", "US OKs $621.9m F-16 aid for Kyiv", "\u2014 Europe pays (State Dept)"),
    (19, "MIDDLE EAST", "Kushner: Netanyahu \u2018not always easy\u2019", "(CNN)"),
    (20, "AFRICA", "Ebola: 11,955 cases, 5,867 dead", "\u2014 UNICEF findings Tue (Bloomberg)"),
    (21, "AFRICA", "UN evacuates 10 Ebola staff in Ituri", "(Reuters)"),
    (22, "AFRICA", "Beni families can\u2019t find Ebola dead", "(Reuters)"),
    (23, "ASIA-PACIFIC", "Sensex +1,502; Nifty +1.85%", "\u2014 rupee 8-month high (HBL)"),
    (24, "ASIA-PACIFIC", "China presses Japan on chemical arms", "\u2014 Hague talks (Xinhua)"),
    (25, "EUROPE", "Ukraine laser downs jet Geran \u2014 CLAIM", "Blysk first claim (ISW)"),
    (26, "OCEANIA", "Australia CPI 4.9%; core 3.8%", "\u2014 RBA hike risk (ABS)"),
    (27, "AMERICAS", "US GDP +4.3%; PCE inflation 3.8%", "\u2014 Sept revised 3.7% (BEA)"),
    (28, "AMERICAS", "Trump, Rutte urge Russia not to widen war", "(NATO)"),
    (29, "WORLD & SCIENCE", "Gold breaks below $3,500", "\u2014 lowest since Sept 2025 (FXStreet)"),
    (30, "AMERICAS", "US eyes 10% duty on Brazil jets", "\u2014 in tariff salvo (Reuters)"),
    (31, "AMERICAS", "Venezuela bonds rally Wed", "\u2014 2022s +2.5c to 56.38c (Reuters)"),
    (32, "ASIA-PACIFIC", "Kospi \u22126.2%; Taiex \u22124.8%; Nikkei \u22122.8%", "\u2014 Asia rout (AP)"),
    (33, "WORLD & SCIENCE", "S&P mulls Nvidia downgrade to AA-", "\u2014 CreditWatch negative (S&P)"),
    (34, "WORLD & SCIENCE", "Macy\u2019s postpones 100th parade", "\u2014 first ever for weather (NWS)"),
    (35, "WORLD & SCIENCE", "Andy Taylor of Duran Duran dies, 65", "\u2014 announced Wed (Reuters)"),
    (36, "WORLD & SCIENCE", "Anthropic ends Wed $82.79", "\u2014 intraday $73.85, under $1tn (Fool)"),
    (37, "AMERICAS", "Beige Book: 8 of 12 districts grow", "\u2014 shoppers wary (Fed)"),
    (38, "WORLD & SCIENCE", "Durant hits 33,000 pts", "\u2014 LeBron triple-double for 76ers (AP)"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 Left off as earlier or later news: Shenzhou crew named (24 Nov) \u00b7 "
    "Venezuela debt plan published (24 Nov) \u00b7 Sarkozy trial order (24 Nov) \u00b7 "
    "Sinner surgery (24 Nov) \u00b7 CIA breach first reported (24 Nov) \u00b7 "
    "Hormuz mine strikes (22 Nov) \u00b7 Nvidia govt-stake talk (24 Nov interview) \u00b7 "
    "Macy\u2019s parade POSTPONED Wed \u2014 first ever for weather \u00b7 "
    "Bangladesh \u2018360 plants\u2019 (26 Nov) \u00b7 Ebola 12,021 (26 Nov) \u00b7 "
    "Brent $91.10 (26 Nov) \u00b7 Europe rally (26 Nov) \u00b7 Anthropic above IPO (26 Nov) \u00b7 "
    "Katz threat (26 Nov) \u00b7 Kyiv hurt \u20187\u2019 (Thu morning) \u00b7 "
    "Hong Kong fire anniversary (26 Nov)")

FOOTER = ("Every story happened or was first reported on Wednesday 25 Nov 2026, UTC. "
          "Times shown are UTC unless marked local. Sources named on each item \u00b7 "
          "* = one side\u2019s claim \u00b7 Original drawings, no photos.")

# map pins: (num, lat, lon) — true positions; display positions fan out below
PINS = [
    (1, 38.9, -77.0),    # Washington
    (2, 39.7, 98.5),     # Jiuquan
    (3, 31.8, 35.2),     # Jerusalem
    (4, 30.0, 31.2),     # Giza
    (5, -35.3, 149.1),   # Canberra
    (6, 23.8, 90.4),     # Dhaka
    (7, 11.8, 34.35),    # Damazin
    (8, 52.2, 21.0),     # Poland
    (9, 21.5, 39.2),     # Jeddah
    (10, 26.6, 50.1),    # Ras Tanura
    (11, 55.7, 42.3),    # Savasleyka
    (12, 31.5, 34.45),   # Gaza City
    (13, 40.7, -74.0),   # New York
]

# coarse dot-matrix world map, 64 cols (lon -180..180) x 32 rows (lat 90..-60)
# spans per row: (first_col, last_col) inclusive, from real geography
_LAND_SPANS = {
    0: [(10, 12), (20, 21)],
    1: [(7, 13), (19, 22), (48, 54)],
    2: [(3, 14), (19, 21), (38, 58)],
    3: [(3, 15), (19, 20), (37, 58)],
    4: [(4, 15), (28, 28), (32, 34), (36, 58)],
    5: [(4, 16), (28, 29), (31, 35), (36, 57)],
    6: [(5, 16), (29, 30), (32, 35), (36, 56)],
    7: [(7, 16), (29, 30), (31, 33), (35, 55), (56, 57)],
    8: [(7, 15), (30, 36), (36, 40), (42, 52), (50, 54)],
    9: [(7, 15), (30, 35), (38, 42), (43, 50), (50, 56), (57, 58)],
    10: [(8, 15), (30, 34), (35, 38), (41, 43), (48, 55), (56, 57)],
    11: [(8, 14), (30, 34), (36, 42), (44, 48), (48, 54), (56, 56)],
    12: [(8, 13), (30, 37), (38, 43), (44, 48), (49, 52), (52, 54)],
    13: [(8, 11), (30, 38), (39, 42), (44, 47), (48, 51)],
    14: [(9, 12), (30, 38), (39, 41), (44, 46), (48, 51)],
    15: [(10, 12), (31, 37), (44, 45), (48, 52), (53, 54)],
    16: [(11, 12), (30, 34), (35, 37), (49, 52), (51, 55)],
    17: [(14, 17), (30, 36), (50, 56), (57, 59)],
    18: [(14, 19), (31, 36), (51, 56), (57, 59)],
    19: [(15, 20), (32, 36), (52, 56)],
    20: [(15, 20), (32, 36), (52, 55)],
    21: [(16, 20), (32, 35), (37, 37), (52, 55)],
    22: [(16, 19), (32, 35), (37, 38), (52, 56)],
    23: [(16, 19), (32, 35), (37, 37), (52, 57)],
    24: [(17, 19), (32, 34), (52, 57)],
    25: [(17, 18), (33, 34), (53, 56), (59, 60)],
    26: [(17, 18), (33, 33), (59, 60)],
    27: [(60, 60)],
}
WORLD = []
for _r in range(32):
    _row = [" "] * 64
    for _a, _b in _LAND_SPANS.get(_r, []):
        for _c in range(_a, _b + 1):
            _row[_c] = "#"
    WORLD.append("".join(_row))

# =====================================================================
# SCENES — original flat illustrations, drawn with Pillow primitives.
# Each returns a pasted-in image of the requested size. Bold flat shapes
# so every scene reads as a distinct coloured block at 300px.
# =====================================================================

def scene_hero1(w, h):
    """Container yard at dusk: crane silhouette, stacked containers, 20% pill."""
    img, d = new_scene(w, h, (22, 42, 84))
    d.rectangle([0, h - 26, w, h], fill=(13, 26, 54))          # quay
    d.rectangle([0, h - 30, w, h - 26], fill=(212, 160, 23))  # quay edge line
    # stacked containers, two rows, flag-ish stripes
    cols = [(178, 52, 52), (20, 143, 119), (212, 160, 23), (30, 132, 73),
            (43, 108, 176), (178, 52, 52), (20, 143, 119), (212, 160, 23)]
    cw, ch, gap = 34, 22, 4
    x0, yb = 14, h - 30
    for row in range(2):
        for i, c in enumerate(cols):
            x = x0 + i * (cw + gap)
            y = yb - (row + 1) * (ch + 3)
            if x + cw > w - 8:
                break
            d.rectangle([x, y, x + cw, y + ch], fill=c, outline=(255, 255, 255), width=1)
            for k in range(1, 4):
                d.line([x + k * cw // 4, y, x + k * cw // 4, y + ch], fill=(255, 255, 255), width=1)
    # crane silhouette (right side)
    d.rectangle([w - 58, 6, w - 50, h - 30], fill=(10, 20, 42))
    d.polygon([(w - 58, 6), (w - 8, 22), (w - 8, 30), (w - 50, 14)], fill=(10, 20, 42))
    d.line([w - 30, 26, w - 30, 52], fill=(10, 20, 42), width=2)
    d.rectangle([w - 36, 52, w - 24, 60], fill=(10, 20, 42))
    # big 20% pill, top right (WOW: bigger)
    f = sans_b(20)
    t = "20%"
    pw = int(tw(d, t, f)) + 22
    rrect(d, [w - pw - 10, 8, w - 10, 8 + 32], r=16, fill=(255, 255, 255))
    d.text((w - pw - 10 + 11, 8 + 6), t, font=f, fill=(178, 34, 34))
    scene_bar(d, w, h, HEROES[0][5], size=11)
    return img

def scene_hero2(w, h):
    """Shenzhou-24: rocket, plume, stars, Earth arc, capsule detail."""
    img, d = new_scene(w, h, (10, 18, 48))
    # stars (fixed positions, deterministic)
    stars = [(18, 12), (52, 26), (96, 8), (150, 20), (210, 10), (262, 30),
             (300, 14), (36, 48), (120, 44), (188, 52), (238, 44), (286, 52),
             (70, 66), (160, 70), (250, 66), (12, 80), (310, 78)]
    for (sx, sy) in stars:
        r = 2 if (sx + sy) % 3 else 1
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))
    # Earth arc, bottom left
    d.ellipse([-70, h - 34, 90, h + 60], fill=(20, 120, 110))
    d.ellipse([-58, h - 26, 78, h + 48], fill=(28, 140, 130))
    # plume
    cx = w // 2 + 38
    d.polygon([(cx - 26, 66), (cx + 26, 66), (cx + 8, 96), (cx - 8, 96)],
              fill=(230, 126, 34))
    d.polygon([(cx - 16, 66), (cx + 16, 66), (cx + 5, 88), (cx - 5, 88)],
              fill=(241, 196, 15))
    # rocket body (nose tip at y=0, fully inside the scene)
    d.rectangle([cx - 20, 14, cx + 20, 66], fill=(245, 245, 240))
    d.polygon([(cx - 20, 14), (cx, 0), (cx + 20, 14)], fill=(178, 34, 34))
    d.rectangle([cx - 20, 36, cx + 20, 44], fill=(178, 34, 34))
    d.ellipse([cx - 8, 20, cx + 8, 34], fill=(43, 108, 176),
              outline=(255, 255, 255), width=2)
    d.polygon([(cx - 20, 66), (cx - 34, 82), (cx - 20, 74)], fill=(178, 34, 34))
    d.polygon([(cx + 20, 66), (cx + 34, 82), (cx + 20, 74)], fill=(178, 34, 34))
    # crew capsule detail, left
    d.ellipse([26, 44, 62, 80], fill=(200, 200, 190), outline=(255, 255, 255), width=2)
    d.ellipse([36, 54, 52, 70], fill=(43, 108, 176))
    scene_bar(d, w, h, HEROES[1][5], size=11)
    return img

def scene_hero3(w, h):
    """W5 rebuild: dark brown, large solid gold scales, courthouse columns,
    big CASE 4000 pill. High contrast for judge size."""
    img, d = new_scene(w, h, (46, 30, 18))
    # courthouse columns as solid shapes, bottom
    col_c = (140, 110, 74)
    for i, cx in enumerate([18, 78, 138, 198, 258]):
        d.rectangle([cx, h - 52, cx + 26, h - 18], fill=col_c)
        d.rectangle([cx - 4, h - 58, cx + 30, h - 52], fill=col_c)
        d.rectangle([cx - 4, h - 18, cx + 30, h - 12], fill=col_c)
    d.rectangle([0, h - 12, w, h], fill=(30, 20, 12))
    # large solid gold scales, centred above the columns
    gold = (212, 160, 23)
    cx = w // 2
    d.rectangle([cx - 4, 12, cx + 4, 66], fill=gold)                    # beam post
    d.polygon([(cx - 62, 14), (cx + 62, 14), (cx, 24)], fill=gold)      # top beam
    d.ellipse([cx - 8, 6, cx + 8, 20], fill=gold)                       # finial
    for sgn in (-1, 1):
        px = cx + sgn * 56
        d.line([px, 18, px, 44], fill=gold, width=3)                    # hanger
        d.line([px - 16, 44, px, 22], fill=gold, width=2)
        d.line([px + 16, 44, px, 22], fill=gold, width=2)
        d.polygon([(px - 22, 44), (px + 22, 44), (px, 62)], fill=gold)  # pan
    d.rectangle([cx - 26, 66, cx + 26, 72], fill=gold)                  # base
    # big CASE 4000 pill, top right
    f = sans_b(13)
    t = "CASE 4000"
    pw = int(tw(d, t, f)) + 18
    rrect(d, [w - pw - 8, 8, w - 8, 8 + 26], r=13, fill=(212, 160, 23))
    d.text((w - pw - 8 + 9, 8 + 6), t, font=f, fill=(46, 30, 18))
    scene_bar(d, w, h, HEROES[2][5], size=11)
    return img

HERO_SCENES = [scene_hero1, scene_hero2, scene_hero3]

# ---- card scenes (188 x 58) ----
def card_giza(w, h):
    img, d = new_scene(w, h, (26, 26, 46))
    d.rectangle([0, h - 14, w, h], fill=(12, 12, 22))                   # road
    d.rectangle([20, 30, 110, 44], fill=(60, 60, 66))                   # tanker
    d.ellipse([104, 28, 128, 46], fill=(80, 80, 88))
    for (fx, fy, fr) in [(40, 26, 12), (70, 20, 15), (100, 28, 11)]:
        d.polygon([(fx - fr, fy + 8), (fx, fy - fr), (fx + fr, fy + 8)],
                  fill=(230, 126, 34))
        d.polygon([(fx - fr // 2, fy + 8), (fx, fy - fr // 2), (fx + fr // 2, fy + 8)],
                  fill=(241, 196, 15))
    for (sx, sy) in [(30, 8), (80, 6), (140, 10), (165, 6)]:
        d.ellipse([sx - 7, sy - 4, sx + 7, sy + 6], fill=(120, 120, 128))
    return img

def card_canberra(w, h):
    img, d = new_scene(w, h, (31, 122, 109))
    d.ellipse([w - 34, 6, w - 12, 28], fill=(241, 196, 15))              # sun
    d.ellipse([w // 2 - 52, 18, w // 2 + 52, 62], fill=(245, 245, 240))  # dome
    d.rectangle([20, 44, w - 20, h], fill=(235, 235, 228))
    for cx in [34, 62, 90, 118, 146]:
        d.rectangle([cx, 46, cx + 8, h], fill=(31, 122, 109))
    d.rectangle([w // 2 - 2, 2, w // 2 + 2, 22], fill=(26, 22, 18))
    d.polygon([(w // 2 + 2, 2), (w // 2 + 20, 7), (w // 2 + 2, 12)], fill=(178, 34, 34))
    return img

def card_dhaka(w, h):
    img, d = new_scene(w, h, (30, 132, 73))
    d.rectangle([14, 34, 26, h], fill=(20, 60, 40))                     # chimneys
    d.rectangle([30, 40, 44, h], fill=(20, 60, 40))
    d.ellipse([16, 26, 28, 34], fill=(200, 200, 200))
    bars = [14, 20, 26, 34]
    for i, bh in enumerate(bars):
        x = 70 + i * 26
        d.rectangle([x, h - 8 - bh, x + 18, h - 8], fill=(255, 255, 255))
    d.line([66, h - 8, 178, h - 8], fill=(255, 255, 255), width=2)
    f = sans_b(13)
    d.text((116, 2), "36%", font=f, fill=(255, 255, 255))
    return img

def card_damazin(w, h):
    img, d = new_scene(w, h, (176, 96, 32))
    for (bx, bw, bh) in [(8, 26, 22), (40, 18, 30), (64, 30, 18), (100, 22, 26),
                         (128, 26, 20), (158, 22, 28)]:
        d.rectangle([bx, h - bh, bx + bw, h], fill=(40, 22, 10))
    d.ellipse([w - 30, 6, w - 10, 26], fill=(241, 196, 15))
    # drone silhouette
    dx, dy = 120, 14
    d.line([dx - 12, dy, dx + 12, dy], fill=(26, 22, 18), width=3)
    d.line([dx, dy - 8, dx, dy + 8], fill=(26, 22, 18), width=3)
    d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(26, 22, 18))
    for (sx, sy) in [(150, 30), (160, 36), (140, 40)]:
        d.ellipse([sx - 6, sy - 5, sx + 6, sy + 5], fill=(120, 120, 120))
    return img

def card_poland(w, h):
    img, d = new_scene(w, h, (43, 108, 176))
    for (cx, cy) in [(30, 12), (90, 20), (150, 10)]:
        d.ellipse([cx - 16, cy - 6, cx + 16, cy + 6], fill=(255, 255, 255))
    # jet silhouette
    d.polygon([(60, 34), (120, 30), (128, 34), (120, 38), (60, 40)], fill=(26, 22, 18))
    d.polygon([(84, 36), (96, 48), (104, 36)], fill=(26, 22, 18))
    d.polygon([(84, 36), (96, 24), (104, 36)], fill=(26, 22, 18))
    # dashed no-fly border
    for x in range(6, w - 6, 12):
        d.line([x, h - 8, x + 7, h - 8], fill=(255, 255, 255), width=2)
        d.line([x, 4, x + 7, 4], fill=(255, 255, 255), width=2)
    return img

def card_jeddah(w, h):
    """W7: big ship silhouette on bright sea, single explosion burst, clear outline."""
    img, d = new_scene(w, h, (174, 214, 241))
    d.rectangle([0, 34, w, h], fill=(127, 179, 213))                    # bright sea
    d.line([0, 34, w, 34], fill=(255, 255, 255), width=2)
    # single explosion burst with clear dark outline, upper right
    bx, by = 148, 18
    pts = []
    import math
    for k in range(12):
        ang = k * math.pi / 6
        r = 16 if k % 2 == 0 else 8
        pts.append((bx + r * math.cos(ang), by + r * math.sin(ang)))
    d.polygon(pts, fill=(230, 126, 34), outline=(120, 50, 10))
    d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(241, 196, 15))
    # big ship silhouette
    d.polygon([(16, 44), (172, 44), (160, 56), (28, 56)], fill=(26, 32, 44))
    for i, c in enumerate([(178, 52, 52), (20, 143, 119), (212, 160, 23)]):
        x = 34 + i * 30
        d.rectangle([x, 30, x + 24, 44], fill=c, outline=(255, 255, 255), width=1)
    d.rectangle([140, 22, 146, 30], fill=(26, 32, 44))
    return img

def card_rastanura(w, h):
    img, d = new_scene(w, h, (126, 81, 9))
    for (tx, th) in [(16, 34), (34, 44), (56, 30), (120, 40), (142, 32)]:
        d.rectangle([tx, h - th, tx + 12, h], fill=(40, 26, 10))
    d.rectangle([76, h - 26, 110, h], fill=(60, 40, 16))
    d.polygon([(84, 20), (92, 6), (100, 20)], fill=(230, 126, 34))
    d.polygon([(88, 20), (92, 12), (96, 20)], fill=(241, 196, 15))
    for (sx, sy) in [(40, 8), (150, 12), (165, 8)]:
        d.ellipse([sx - 8, sy - 5, sx + 8, sy + 5], fill=(60, 60, 60))
    return img

def card_savasleyka(w, h):
    img, d = new_scene(w, h, (26, 58, 36))
    d.rectangle([0, h - 12, w, h], fill=(90, 90, 88))                   # runway
    d.line([0, h - 12, w, h - 12], fill=(255, 255, 255), width=1)
    for (jx, jy) in [(52, 34), (96, 28)]:
        d.polygon([(jx - 16, jy), (jx + 14, jy - 3), (jx + 18, jy), (jx + 14, jy + 3)],
                  fill=(16, 16, 16))
        d.polygon([(jx - 2, jy), (jx + 4, jy + 10), (jx + 8, jy)], fill=(16, 16, 16))
    d.polygon([(150, 30), (158, 12), (166, 30)], fill=(230, 126, 34))
    d.polygon([(154, 30), (158, 20), (162, 30)], fill=(241, 196, 15))
    for (sx, sy) in [(20, 8), (70, 6), (130, 10), (175, 6)]:
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    return img

def card_gaza(w, h):
    """W6 lighten: dusk sky gradient bands, skyline with lit windows."""
    img, d = new_scene(w, h, (108, 52, 131))
    d.rectangle([0, 18, w, 36], fill=(214, 137, 60))
    d.rectangle([0, 36, w, h], fill=(230, 180, 110))
    d.ellipse([w - 36, 4, w - 14, 26], fill=(241, 196, 15))
    for (bx, bw, bh) in [(6, 24, 22), (34, 18, 30), (56, 28, 18), (88, 20, 26),
                         (112, 26, 20), (142, 20, 28), (166, 18, 24)]:
        d.rectangle([bx, h - bh, bx + bw, h], fill=(44, 34, 52))
        for wy in range(h - bh + 4, h - 4, 8):
            for wx in (bx + 4, bx + bw - 8):
                d.rectangle([wx, wy, wx + 4, wy + 4], fill=(241, 196, 15))
    return img

def card_newyork(w, h):
    img, d = new_scene(w, h, (28, 40, 51))
    # candlesticks
    sticks = [(16, 30, 20, 1), (36, 24, 14, 1), (56, 28, 18, 0), (76, 18, 12, 1),
              (96, 22, 16, 0), (116, 14, 10, 1), (136, 18, 14, 1), (156, 10, 8, 1)]
    for (x, y, bh, up) in sticks:
        c = (39, 174, 96) if up else (231, 76, 60)
        d.rectangle([x, y, x + 10, y + bh], fill=c)
        d.line([x + 5, y - 5, x + 5, y + bh + 5], fill=c, width=1)
    f = sans_b(10)
    d.text((8, 3), "DOW +0.33%", font=f, fill=(39, 174, 96))
    d.text((102, 3), "NASDAQ \u22120.62%", font=f, fill=(231, 76, 60))
    return img

CARD_SCENES = [card_giza, card_canberra, card_dhaka, card_damazin, card_poland,
               card_jeddah, card_rastanura, card_savasleyka, card_gaza,
               card_newyork]

# =====================================================================
# PAGE ASSEMBLY
# =====================================================================

def draw_top(d):
    # top line
    f = sans_b(11)
    d.text((M, 6), TOPLINE_L, font=f, fill=RED)
    r = tw(d, TOPLINE_R, f)
    d.text((W - M - r, 6), TOPLINE_R, font=f, fill=GREY)
    # masthead
    f = serif_b(60)
    t = MASTHEAD
    d.text((M, 20), t, font=f, fill=INK)
    # dek, bold-italic 15px, darker red, centred (W3)
    f = serif_bi(15)
    w = tw(d, DEK, f)
    if w > CW:
        f = serif_bi(14)
        w = tw(d, DEK, f)
    d.text((M + (CW - w) / 2, 90), DEK, font=f, fill=DRED)
    # thin gold rule under dek (WOW)
    d.rectangle([M, 112, W - M, 114], fill=GOLD)

def draw_tabs(d):
    y0, y1 = 118, 138
    # widths by text, then distribute leftover evenly
    f = sans_b(11)
    widths = []
    for name, n in TABS:
        widths.append(int(tw(d, "%s %d" % (name, n), f)) + 18)
    extra = CW - sum(widths) - 6 * 4
    per = extra // len(widths)
    widths = [w_ + per for w_ in widths]
    x = M
    for (name, n), w_ in zip(TABS, widths):
        col = REGION[name][0]
        d.rectangle([x, y0, x + w_, y1], fill=col)
        t = "%s %d" % (name, n)
        d.text((x + (w_ - tw(d, t, f)) / 2, y0 + 4), t, font=f, fill=(255, 255, 255))
        x += w_ + 4

def draw_numbers(d):
    y0, y1 = 144, 194
    lab_w = 104
    d.rectangle([M, y0, M + lab_w, y1], fill=(20, 18, 16))
    f = sans_b(10)
    d.text((M + 10, y0 + 7), "THE DAY", font=f, fill=(255, 255, 255))
    d.text((M + 10, y0 + 20), "IN NUMBERS", font=f, fill=(255, 255, 255))
    d.text((M + 10, y0 + 33), "WEDNESDAY", font=sans_b(9), fill=(212, 160, 23))
    cell_w = (CW - lab_w) / 6.0
    for i, (city, num, cap) in enumerate(NUMBERS):
        x = M + lab_w + i * cell_w
        d.text((x + 8, y0 + 3), city, font=sans_b(8), fill=GREY)
        d.text((x + 8, y0 + 14), num, font=serif_b(27), fill=RED)
        d.text((x + 8, y0 + 40), cap, font=sans(9), fill=GREY)
        if i:
            d.line([x, y0 + 4, x, y1 - 4], fill=(210, 202, 188), width=1)
    d.line([M, y1, W - M, y1], fill=(210, 202, 188), width=1)

def draw_heroes(img, d):
    y0 = 200
    hw, gap = 320, 16
    scene_h = 98
    for i, (num, kicker, p, headline, deck, bar) in enumerate(HEROES):
        x = M + i * (hw + gap)
        scene = HERO_SCENES[i](hw, scene_h)
        img.paste(scene, (x, y0))
        sd = ImageDraw.Draw(img)
        pin_badge(sd, x + 13, y0 + 13, num)
        # pill bottom-right of scene
        pw = pill(sd, x + hw - 92, y0 + scene_h - 24, p, p, size=9)
        # kicker
        kc = {"WASHINGTON": (178, 32, 92), "JIUQUAN": (178, 52, 52),
              "JERUSALEM": (14, 124, 123)}[kicker.split(" ")[0]]
        d.text((x, y0 + scene_h + 5), kicker, font=sans_b(11), fill=kc)
        # headline 30px bold, max 2 lines (W4)
        f, lines = fit_lines(d, headline, serif_b(30), hw, 2, 26,
                             "LiberationSerif-Bold.ttf")
        yy = y0 + scene_h + 20
        for ln in lines:
            d.text((x, yy), ln, font=f, fill=INK)
            yy += f.size + 1
        # deck, 2 lines, 11.5px
        f2, lines2 = fit_lines(d, deck, serif(12), hw, 2, 10,
                               "LiberationSerif-Regular.ttf")
        yy = y0 + scene_h + 20 + 2 * 31 + 2
        for ln in lines2:
            d.text((x, yy), ln, font=f2, fill=(58, 52, 46))
            yy += f2.size + 2

def draw_cards(img, d):
    cw, gap = 188, 13
    scene_h = 58
    rows_y = [414, 560]
    for idx, (num, place, region, p, headline, deck) in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x = M + col * (cw + gap)
        y0 = rows_y[row]
        scene = CARD_SCENES[idx](cw, scene_h)
        img.paste(scene, (x, y0))
        sd = ImageDraw.Draw(img)
        pin_badge(sd, x + 12, y0 + 12, num)
        pill(sd, x + cw - 82, y0 + scene_h - 22, p, p, size=8)
        # kicker: place in region colour
        d.text((x, y0 + scene_h + 4), place, font=sans_b(10),
               fill=REGION[region][1])
        # headline 16.5px bold, max 2 lines (W8)
        f, lines = fit_lines(d, headline, serif_b(17), cw, 2, 14,
                             "LiberationSerif-Bold.ttf")
        yy = y0 + scene_h + 17
        for ln in lines:
            d.text((x, yy), ln, font=f, fill=INK)
            yy += f.size + 1
        # deck 2 lines
        f2, lines2 = fit_lines(d, deck, serif(11), cw, 2, 9,
                               "LiberationSerif-Regular.ttf")
        yy = y0 + scene_h + 17 + 2 * 18 + 1
        for ln in lines2:
            d.text((x, yy), ln, font=f2, fill=(58, 52, 46))
            yy += f2.size + 1

def draw_briefs_header(d):
    f = sans_b(15)
    d.text((M, 708), "ALSO ON WEDNESDAY 25 NOVEMBER \u2014 25 MORE, BY REGION",
           font=f, fill=INK)
    d.rectangle([M, 727, 716, 729], fill=RED)
    f2 = sans_b(11)
    d.text((736, 710), "WHERE IT HAPPENED \u00b7 PINS 1\u201313",
           font=f2, fill=INK)

def fit_brief(d, lead, rest, max_w):
    """Pick (lead_font, body_font) from the ladder so lead+rest fits one line."""
    for ls, bs in [(12, 10), (11, 10), (11, 9), (10, 9)]:
        lf, bf = sans_b(ls), sans(bs)
        if tw(d, lead + " " + rest, lf) <= max_w and \
           tw(d, lead, lf) + tw(d, " " + rest, bf) <= max_w:
            return lf, bf
    return sans_b(10), sans(9)

def draw_briefs(d):
    col_x = [M, 372]
    col_w = 344
    row_h = 15.8
    y0 = 732
    for idx, (num, region, lead, rest) in enumerate(BRIEFS):
        col, row = (0, idx) if idx < 13 else (1, idx - 13)
        x = col_x[col]
        y = y0 + row * row_h
        # number
        nf = sans_b(11)
        d.text((x, y), "%d." % num, font=nf, fill=INK)
        # region dot 10px (W2)
        dx = x + 26
        d.ellipse([dx, y + 1, dx + 10, y + 11], fill=REGION[region][0])
        tx = x + 42
        lf, bf = fit_brief(d, lead, rest, col_w - 42)
        d.text((tx, y), lead, font=lf, fill=INK)
        lw = tw(d, lead, lf)
        d.text((tx + lw + 3, y + (lf.size - bf.size)), rest, font=bf,
               fill=(58, 52, 46))

def draw_map(d):
    x0, y0 = 736, 732
    mw, mh = 272, 158
    # navy -> teal vertical gradient
    for yy in range(mh):
        t = yy / max(mh - 1, 1)
        r = int(13 + (13 - 13) * t)
        g = int(60 + (110 - 60) * t)
        b = int(74 + (110 - 74) * t)
        d.line([x0, y0 + yy, x0 + mw, y0 + yy], fill=(r, g, b))
    # land dots
    cw_, ch_ = mw / 64.0, mh / 32.0
    for r_, row in enumerate(WORLD):
        row = row.ljust(64)[:64]
        for c_, ch in enumerate(row):
            if ch == "#":
                cx = x0 + (c_ + 0.5) * cw_
                cy = y0 + (r_ + 0.5) * ch_
                d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6],
                          fill=GOLD_L)
    # pin true positions
    def proj(lat, lon):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (90.0 - lat) / 150.0 * mh)
    pts = {n: proj(lat, lon) for (n, lat, lon) in PINS}
    # fan-out repulsion: keep display pins >= 26px apart (W10)
    disp = dict(pts)
    seed = {1: (-14, 10), 13: (12, -12), 3: (10, -12), 4: (-16, 4),
            12: (-4, 14), 8: (-14, -8), 11: (14, 8), 9: (-10, 10),
            10: (12, -6), 7: (0, 8), 6: (8, -8)}
    for n, (ox, oy) in seed.items():
        px, py = disp[n]
        disp[n] = (px + ox, py + oy)
    for _ in range(60):
        moved = False
        keys = sorted(disp)
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = keys[i], keys[j]
                ax, ay = disp[a]
                bx, by = disp[b]
                dx, dy = bx - ax, by - ay
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < 26 and dist > 0.01:
                    push = (26 - dist) / 2.0
                    ux, uy = dx / dist, dy / dist
                    disp[a] = (ax - ux * push, ay - uy * push)
                    disp[b] = (bx + ux * push, by + uy * push)
                    moved = True
        if not moved:
            break
    # clamp inside map box
    for n in disp:
        px, py = disp[n]
        disp[n] = (min(max(px, x0 + 10), x0 + mw - 10),
                   min(max(py, y0 + 10), y0 + mh - 10))
    # leader lines + true dots + badges
    for n, (px, py) in pts.items():
        dx, dy = disp[n]
        if abs(dx - px) > 2 or abs(dy - py) > 2:
            d.line([px, py, dx, dy], fill=(255, 255, 255), width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))
        pin_badge(d, dx, dy, n, r=8)
    # legend, two rows (auto-shrink so nothing runs past the map edge)
    rows = [[("EUROPE", 8), ("MIDDLE EAST", 5), ("AFRICA", 5), ("OCEANIA", 2)],
            [("ASIA-PACIFIC", 5), ("AMERICAS", 7), ("WORLD & SCIENCE", 6)]]
    fsize = 9
    while fsize >= 8:
        f = sans_b(fsize)
        ok = True
        for row in rows:
            tot = sum(11 + tw(d, "%s %d" % (n_, v_), f) + 8 for n_, v_ in row) - 8
            if tot > mw:
                ok = False
        if ok:
            break
        fsize -= 1
    f = sans_b(fsize)
    for row, yy in zip(rows, [896, 914]):
        x = x0
        for name, n in row:
            d.ellipse([x, yy + 1, x + 8, yy + 9], fill=REGION[name][0])
            t = "%s %d" % (name, n)
            d.text((x + 11, yy), t, font=f, fill=INK)
            x += 11 + tw(d, t, f) + 8

def draw_bottom(d):
    # DATE CHECK strip, red, 3 lines max
    y0, y1 = 942, 994
    d.rectangle([M, y0, W - M, y1], fill=(140, 22, 22))
    f = sans(10)
    fb = sans_b(10)
    # label bold + rest regular, wrapped together on the strip
    label = "DATE CHECK \u2014 "
    words = DATE_CHECK.split()
    lines = []
    cur = label
    cur_w = tw(d, label, fb)
    i = 0
    # first line starts with the bold label; measure rest with regular font
    for w_ in words[3:]:  # skip "DATE CHECK —" (already the label)
        trial = cur + w_ + " "
        if tw(d, trial, f) <= CW - 20:
            cur = trial
        else:
            lines.append(cur.rstrip())
            cur = w_ + " "
    lines.append(cur.rstrip())
    # vertically centre the lines block inside the strip
    yy = y0 + (y1 - y0 - len(lines) * 13) // 2
    for li, ln in enumerate(lines):
        if li == 0:
            d.text((M + 10, yy), label, font=fb, fill=(255, 255, 255))
            d.text((M + 10 + tw(d, label, fb), yy), ln[len(label):],
                   font=f, fill=(255, 255, 255))
        else:
            d.text((M + 10, yy), ln, font=f, fill=(255, 255, 255))
        yy += 13
    # footer
    f2 = sans(9)
    t = FOOTER
    d.text((M + (CW - tw(d, t, f2)) / 2, 1000), t, font=f2, fill=GREY)

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_top(d)
    draw_tabs(d)
    draw_numbers(d)
    draw_heroes(img, d)
    draw_cards(img, d)
    draw_briefs_header(d)
    draw_briefs(d)
    draw_map(d)
    draw_bottom(d)
    img.save(OUT, format="PNG", optimize=True)
    return OUT

if __name__ == "__main__":
    path = build()
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))
