#!/usr/bin/env python3
"""One Day of World News — Wednesday 25 November 2026.

A single-page newspaper front page drawn entirely with Pillow
primitives. No network, no photos, deterministic output.
Run:  python3 frontpage25.py   -> writes entry.png next to this file.
"""
import math
import os
import random
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (250, 246, 236)
INK = (18, 18, 18)
RED = (178, 34, 34)
GREY = (110, 108, 100)
LIGHT_GREY = (150, 147, 138)

LIB = "/usr/share/fonts/truetype/liberation/"
DEJ = "/usr/share/fonts/truetype/dejavu/"

PILLS = {
    "OFFICIAL": (13, 110, 110),
    "CONFIRMED": (34, 128, 60),
    "REPORTED": (176, 110, 0),
    "CLAIM": (178, 34, 34),
}
REGIONS = [
    ("EUROPE", (52, 110, 180), 7),
    ("MIDDLE EAST", (18, 130, 110), 5),
    ("AFRICA", (205, 120, 30), 5),
    ("ASIA-PACIFIC", (178, 40, 40), 5),
    ("OCEANIA", (120, 80, 170), 2),
    ("AMERICAS", (190, 40, 110), 9),
    ("WORLD & SCIENCE", (90, 90, 95), 5),
]
REGION_COLOUR = {name: col for name, col, _ in REGIONS}

OVERFLOWS = []


def note(msg):
    OVERFLOWS.append(msg)


# ---------------------------------------------------------------- fonts
_cache = {}


def font(kind, size):
    """kind: serif_b, serif, serif_i, sans_b, sans."""
    key = (kind, size)
    if key in _cache:
        return _cache[key]
    table = {
        "serif_b": ("LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"),
        "serif": ("LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"),
        "serif_i": ("LiberationSerif-Italic.ttf", "DejaVuSerif.ttf"),
        "sans_b": ("LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
        "sans": ("LiberationSans-Regular.ttf", "DejaVuSans.ttf"),
    }
    lib_name, dej_name = table[kind]
    path = os.path.join(LIB, lib_name)
    if not os.path.exists(path):
        path = os.path.join(DEJ, dej_name)
    f = ImageFont.truetype(path, size)
    _cache[key] = f
    return f


def tw(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if tw(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_block(draw, text, kind, start, floor, max_w, max_lines, lh_factor=1.18):
    """Largest font (start..floor) whose wrap fits max_lines. Returns (font, lines)."""
    size = start
    while size > floor:
        fnt = font(kind, size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = font(kind, floor)
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        note("block overflow (%s): %r -> %d lines at floor %d"
             % (kind, text[:40], len(lines), floor))
    return fnt, lines


def fit_single(draw, text, kind, start, floor, max_w):
    size = start
    while size > floor:
        fnt = font(kind, size)
        if tw(draw, text, fnt) <= max_w:
            return fnt
        size -= 1
    fnt = font(kind, floor)
    if tw(draw, text, fnt) > max_w:
        note("single-line overflow: %r" % text[:50])
    return fnt


def draw_lines(draw, lines, x, y, fnt, fill, lh):
    for i, line in enumerate(lines):
        draw.text((x, y + i * lh), line, font=fnt, fill=fill)
    return y + len(lines) * lh


def pill(draw, x_right, y, label, size=8):
    """Certainty pill, right-aligned at x_right, top y. Returns left edge."""
    fnt = font("sans_b", size)
    w = int(tw(draw, label, fnt)) + 12
    h = 14 if size <= 8 else 16
    x0 = x_right - w
    draw.rounded_rectangle([x0, y, x_right, y + h], radius=h // 2,
                           fill=PILLS[label])
    draw.text((x0 + 6, y + (h - size) // 2 - 1), label, font=fnt,
              fill=(255, 255, 255))
    return x0


def badge(draw, cx, cy, num, r=10, size=11):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                 outline=(255, 255, 255), width=2)
    fnt = font("sans_b", size)
    t = str(num)
    draw.text((cx - tw(draw, t, fnt) / 2, cy - size / 2 - 1), t,
              font=fnt, fill=(255, 255, 255))


def tag_chip(draw, x, y_bottom, text):
    fnt = font("sans_b", 7)
    w = int(tw(draw, text, fnt)) + 10
    y0 = y_bottom - 13
    draw.rectangle([x + 2, y0, x + 2 + w, y_bottom - 1], fill=(15, 15, 15))
    draw.text((x + 7, y0 + 2), text, font=fnt, fill=(255, 255, 255))


# ---------------------------------------------------------------- data
HEROES = [
    dict(num=1, region="AMERICAS", field="trade",
         place="WASHINGTON · TRADE", pill="OFFICIAL", tag="14 PARTNERS",
         head="US proposes new tariffs on 14 trading partners",
         summ="China faces a 20% top rate; public hearing on 25 January. "
              "Reuters, USTR",
         pin=(-77.0, 38.9), scene="tariff"),
    dict(num=2, region="ASIA-PACIFIC", field="space",
         place="JIUQUAN · SPACE", pill="CONFIRMED", tag="08:18 BEIJING",
         head="Shenzhou-24 launches with first foreign astronaut",
         summ="Pakistan's Zeeshan Ali, 40, joins the Tiangong crew for "
              "5-10 days. Xinhua, Aviation Week",
         pin=(100.3, 40.9), scene="launch"),
    dict(num=3, region="MIDDLE EAST", field="courts",
         place="JERUSALEM · COURTS", pill="CONFIRMED", tag="CASE 4000",
         head="Judges urge Netanyahu bribery case be dropped",
         summ="Case 4000 drop recommended; Case 2000 reconsidered. "
              "Not a ruling yet. Reuters, CNN",
         pin=(35.2, 31.8), scene="court"),
]

CARDS = [
    dict(num=4, region="AFRICA", field="disaster", place="GIZA",
         pill="CONFIRMED", tag="31 DEAD",
         head="Fuel tanker blast in Giza kills 31",
         summ="27 vehicles burned; toll rose from 21 overnight. Reuters, CNN",
         pin=(31.2, 30.0), scene="smoke"),
    dict(num=5, region="OCEANIA", field="diplomacy", place="CANBERRA",
         pill="OFFICIAL", tag="$740M",
         head="Solomon picks Australia, bars foreign bases",
         summ="Wale-Albanese sign pact; $740m over 10 years. AP, CNN",
         pin=(149.1, -35.3), scene="capitol"),
    dict(num=6, region="ASIA-PACIFIC", field="labour", place="DHAKA",
         pill="CONFIRMED", tag="+36%",
         head="Bangladesh lifts garment wage 36%",
         summ="Minimum now 17,000 taka; smallest rise since 1986. AP, AFP",
         pin=(90.4, 23.8), scene="chart"),
    dict(num=7, region="AFRICA", field="war", place="DAMAZIN",
         pill="REPORTED", tag="19 DEAD",
         head="RSF drone strike kills 19 in Blue Nile",
         summ="Reported Wed; 19 dead in Damazin, 20 hurt. Reuters",
         pin=(34.5, 11.8), scene="dawn"),
    dict(num=8, region="EUROPE", field="defence",
         place="POLAND · EAST BORDER", pill="OFFICIAL", tag="NO-FLY ZONE",
         head="Poland plans no-fly zone on east border",
         summ="Strip tens of km wide; rules due by early January. Reuters",
         pin=(23.5, 52.0), scene="jets"),
    dict(num=9, region="MIDDLE EAST", field="security", place="JEDDAH",
         pill="REPORTED", tag="PORT THREAT",
         head="Houthis threaten Jeddah port; Hodeidah hit",
         summ="Coalition bombs Hodeidah; 4 drones downed. Reuters",
         pin=(39.2, 21.5), scene="tanker"),
    dict(num=10, region="MIDDLE EAST", field="energy", place="RAS TANURA",
         pill="CLAIM", tag="BRENT +3.5%",
         head="Houthis claim Ras Tanura refinery strike",
         summ="Brent closes $94.61, +3.5%; claim unverified. Reuters",
         pin=(50.1, 26.6), scene="derrick"),
    dict(num=11, region="EUROPE", field="war", place="SAVASLEYKA",
         pill="REPORTED", tag="5 JETS HIT",
         head="Ukraine hits Savasleyka: 5 jets damaged",
         summ="3 MiG-31s, 2 Su-34s hit 680 km inside Russia. Reuters",
         pin=(43.3, 55.6), scene="blast"),
    dict(num=12, region="MIDDLE EAST", field="war", place="GAZA CITY",
         pill="CONFIRMED", tag="02:46",
         head="Israel kills Hamas security chief in Gaza",
         summ="Abu al-Aouf dies with family in Al-Shati strike. CNN, IDF",
         pin=(34.5, 31.5), scene="tower"),
    dict(num=13, region="AMERICAS", field="markets", place="NEW YORK",
         pill="CONFIRMED", tag="DOW +0.33%",
         head="Dow swings +0.33% after 1,100-point dive",
         summ="S&P -0.25%, Nasdaq -0.62%; Nvidia -4%. Reuters",
         pin=(-74.0, 40.7), scene="ticker"),
]

BRIEFS = [
    ("EUROPE", "war", "Kyiv hit late Wed; ≥4 hurt", "Klitschko"),
    ("EUROPE", "sport", "UCL: PSG 2-2 Roma; Bayern 1-2 Lille", "UEFA"),
    ("EUROPE", "diplomacy", "Macron threatens EU budget walkout", "AP"),
    ("EUROPE", "war", "Kyiv hits 2 Russia refineries", "ISW"),
    ("EUROPE", "defence", "US OKs $621.9m F-16 aid for Kyiv", "State Dept"),
    ("MIDDLE EAST", "diplomacy", "Kushner: Netanyahu 'not always easy'", "CNN"),
    ("AFRICA", "health", "Ebola fuels abuse of girls in Ituri", "UNICEF"),
    ("AFRICA", "health", "UN evacuates 10 Ebola staff in Ituri", "Reuters"),
    ("AFRICA", "health", "Beni families can't find Ebola dead", "Reuters"),
    ("ASIA-PACIFIC", "markets", "Sensex +1,502; Nifty +1.85%", "HBL"),
    ("ASIA-PACIFIC", "diplomacy", "China presses Japan on chemical arms", "Xinhua"),
    ("ASIA-PACIFIC", "labour", "Dhaka wage deal sparks new protests", "CCC"),
    ("OCEANIA", "disaster", "Flinders Island bushfire evacuates", "ABC"),
    ("AMERICAS", "economy", "US GDP +4.3%; PCE inflation 3.8%", "BEA"),
    ("AMERICAS", "diplomacy", "Trump hosts NATO chief Rutte at 7pm", "PBP"),
    ("AMERICAS", "travel", "81.5m Americans travel for Thanksgiving", "AAA"),
    ("AMERICAS", "trade", "US eyes 10% duty on Brazil jets", "Reuters"),
    ("AMERICAS", "markets", "Venezuela bonds rally Wed on debt data", "Reuters"),
    ("AMERICAS", "markets", "LatAm FX worst since Nov 10", "ING"),
    ("AMERICAS", "economy", "Beige Book: 8 of 12 districts grow", "Fed"),
    ("WORLD & SCIENCE", "technology", "S&P mulls Nvidia downgrade to AA-", "TechCrunch"),
    ("WORLD & SCIENCE", "weather", "Nor'easter bears down on East Coast", "NWS"),
    ("WORLD & SCIENCE", "culture", "Andy Taylor of Duran Duran dies, 65", "Reuters"),
    ("WORLD & SCIENCE", "stocks", "Anthropic ends Wed at $82.79", "Fool"),
    ("WORLD & SCIENCE", "finance", "Burry closes last Nasdaq 100 puts", "CNBC"),
]

NUMBERS = [
    ("WASHINGTON", "14", "partners hit by new tariffs"),
    ("CHINA", "20%", "top tariff rate proposed"),
    ("GIZA", "31", "killed in fuel-tanker fire"),
    ("LONDON", "$94.61", "Brent close Wed (+3.5%)"),
    ("MUMBAI", "+1,502", "Sensex points in a day"),
    ("US · OCTOBER", "3.8%", "PCE inflation, year on year"),
]

DATE_CHECK = ("DATE CHECK — Left off as earlier news: ICJ Myanmar ruling "
              "(19 Nov) · Sarkozy trial order (24 Nov) · Venezuela debt plan "
              "published (24 Nov) · Hormuz mine strikes (22 Nov) · Sinner "
              "surgery (24 Nov) · CIA breach first reported (24 Nov) · "
              "Malaysia refugee return (24 Nov) · Hong Kong fire anniversary "
              "(26 Nov) · Shenzhou crew named (24 Nov)")
FOOTER = ("Every story happened or was first reported on Wednesday 25 Nov "
          "2026, UTC. Times shown are UTC unless marked local. Sources "
          "named on each item · Original drawings, no photos.")

# Pin display offsets (dx, dy in px) to fan out crowded clusters.
PIN_OFFSETS = {
    1: (-34, -18), 13: (22, -26),
    3: (-48, -34), 12: (52, -20),
    4: (-58, 6), 9: (-6, 44), 10: (52, 18),
    8: (0, -22), 11: (30, -18),
    2: (18, -30), 5: (0, 0), 6: (-2, 30), 7: (-44, 34),
}

# ---------------------------------------------------------------- scenes
def scene_tariff(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(22, 48, 96))
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(14, 30, 62))
    cols = [(178, 60, 50), (20, 120, 110), (210, 160, 40), (60, 140, 70)]
    for row in range(2):
        for i in range(4):
            cx = x + 14 + i * 52
            cy = y + h - 34 - (row + 1) * 20
            d.rectangle([cx, cy, cx + 48, cy + 18], fill=cols[(i + row) % 4],
                        outline=(255, 255, 255))
            d.line([cx + 16, cy, cx + 16, cy + 18], fill=(255, 255, 255))
            d.line([cx + 32, cy, cx + 32, cy + 18], fill=(255, 255, 255))
    d.rectangle([x + w - 52, y + 18, x + w - 46, y + h - 34], fill=(12, 20, 44))
    d.line([x + w - 100, y + 22, x + w - 30, y + 22], fill=(12, 20, 44), width=6)
    d.line([x + w - 96, y + 22, x + w - 70, y + 52], fill=(12, 20, 44), width=3)
    d.rectangle([x + w - 76, y + 52, x + w - 62, y + 64], fill=(12, 20, 44))
    fnt = font("sans_b", 15)
    bw = int(tw(d, "20%", fnt)) + 16
    d.rounded_rectangle([x + w - bw - 8, y + 8, x + w - 8, y + 30],
                        radius=4, fill=(255, 255, 255))
    d.text((x + w - bw, y + 10), "20%", font=fnt, fill=RED)
    d.rectangle([x, y + h - 20, x + w, y + h], fill=RED)
    bf = font("sans_b", 10)
    t = "NEW TARIFFS · 14 PARTNERS"
    d.text((x + (w - tw(d, t, bf)) / 2, y + h - 17), t, font=bf,
           fill=(255, 255, 255))


def scene_launch(d, x, y, w, h, rng):
    d.rectangle([x, y, x + w, y + h], fill=(8, 12, 42))
    for _ in range(46):
        sx = x + rng.randint(4, w - 4)
        sy = y + rng.randint(4, h - 30)
        r = rng.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))
    d.rectangle([x + 26, y + 22, x + 52, y + h - 20], fill=(70, 76, 92))
    for gy in range(y + 30, y + h - 28, 14):
        d.line([x + 26, gy, x + 52, gy + 10], fill=(40, 44, 60), width=3)
    cx = x + w // 2
    d.polygon([(cx - 26, y + h - 44), (cx + 26, y + h - 44), (cx, y + h - 8)],
              fill=(255, 140, 0))
    d.polygon([(cx - 14, y + h - 44), (cx + 14, y + h - 44), (cx, y + h - 14)],
              fill=(255, 220, 80))
    d.rectangle([cx - 16, y + 26, cx + 16, y + h - 42], fill=(245, 245, 240))
    d.polygon([(cx - 16, y + 26), (cx + 16, y + 26), (cx, y + 6)],
              fill=RED)
    d.rectangle([cx - 16, y + 58, cx + 16, y + 66], fill=RED)
    d.ellipse([cx - 7, y + 36, cx + 7, y + 50], fill=(40, 90, 170))
    d.ellipse([cx - 4, y + 39, cx + 4, y + 47], fill=(180, 220, 255))
    d.polygon([(cx - 16, y + h - 58), (cx - 30, y + h - 38),
               (cx - 16, y + h - 42)], fill=(200, 40, 40))
    d.polygon([(cx + 16, y + h - 58), (cx + 30, y + h - 38),
               (cx + 16, y + h - 42)], fill=(200, 40, 40))
    for sx, sy, r in [(cx - 44, y + h - 26, 12), (cx + 46, y + h - 22, 10),
                      (cx - 58, y + h - 14, 8)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(150, 150, 155))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=RED)
    bf = font("sans_b", 10)
    t = "FIRST FOREIGN ASTRONAUT"
    d.text((x + (w - tw(d, t, bf)) / 2, y + h - 17), t, font=bf,
           fill=(255, 255, 255))


def scene_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(122, 86, 56))
    d.rectangle([x, y + h - 30, x + w, y + h], fill=(88, 58, 34))
    d.rectangle([x + 18, y + h - 52, x + w - 18, y + h - 30], fill=(96, 62, 34))
    d.rectangle([x + 18, y + h - 58, x + w - 18, y + h - 52], fill=(140, 96, 52))
    cx = x + w // 2
    top = y + 34
    d.line([cx, top, cx, y + 78], fill=(230, 190, 90), width=4)
    d.line([cx - 42, top + 8, cx + 42, top + 8], fill=(230, 190, 90), width=4)
    d.ellipse([cx - 5, top - 6, cx + 5, top + 4], fill=(230, 190, 90))
    for s in (-1, 1):
        ex = cx + s * 42
        d.line([ex, top + 8, ex, y + 62], fill=(230, 190, 90), width=2)
        d.line([ex - 16, y + 62, ex + 16, y + 62], fill=(230, 190, 90), width=3)
        d.polygon([(ex - 16, y + 62), (ex + 16, y + 62), (ex, y + 76)],
                  fill=(210, 170, 70))
    gx, gy = x + w - 62, y + h - 62
    d.line([gx, gy + 8, gx + 26, gy - 6], fill=(70, 44, 22), width=5)
    d.rectangle([gx - 12, gy - 8, gx + 8, gy + 4], fill=(120, 80, 40))
    fnt = font("sans_b", 9)
    bw = int(tw(d, "CASE 4000", fnt)) + 14
    d.rounded_rectangle([x + w - bw - 8, y + 8, x + w - 8, y + 28],
                        radius=4, fill=(255, 255, 255))
    d.text((x + w - bw - 1, y + 11), "CASE 4000", font=fnt, fill=RED)


def scene_card(d, kind, x, y, w, h, rng):
    if kind == "smoke":
        d.rectangle([x, y, x + w, y + h], fill=(90, 96, 110))
        for bx, bw in [(14, 34), (56, 26), (96, 40), (146, 30)]:
            d.rectangle([x + bx, y + 26, x + bx + bw, y + h - 8],
                        fill=(40, 42, 52))
        for sx, sy, r in [(80, 12, 10), (104, 8, 13), (128, 14, 9)]:
            d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                      fill=(190, 190, 195))
        for fx in (30, 70, 120, 160):
            d.polygon([(x + fx, y + h - 8), (x + fx + 12, y + h - 8),
                       (x + fx + 6, y + h - 24)], fill=(255, 120, 20))
    elif kind == "capitol":
        d.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
        d.rectangle([x + 58, y + 22, x + w - 58, y + h - 8], fill=(245, 242, 230))
        d.pieslice([x + 72, y + 2, x + w - 72, y + 34], 180, 360,
                   fill=(245, 242, 230))
        d.rectangle([x + 58, y + 30, x + w - 58, y + 34], fill=(180, 170, 140))
        for cx in range(x + 70, x + w - 66, 16):
            d.line([cx, y + 34, cx, y + h - 10], fill=(150, 140, 110), width=2)
        for tx in (x + 22, x + w - 30):
            d.ellipse([tx - 9, y + 26, tx + 9, y + 44], fill=(40, 130, 70))
            d.rectangle([tx - 2, y + 42, tx + 2, y + h - 8], fill=(90, 60, 30))
    elif kind == "chart":
        d.rectangle([x, y, x + w, y + h], fill=(18, 110, 62))
        for gy in range(y + 10, y + h, 12):
            d.line([x + 8, gy, x + w - 8, gy], fill=(60, 160, 100))
        for i, bh in enumerate([8, 12, 7, 15, 11, 18]):
            bx = x + 96 + i * 14
            d.rectangle([bx, y + h - 6 - bh, bx + 8, y + h - 6],
                        fill=(180, 230, 190))
        pts = [(x + 12, y + 38), (x + 48, y + 30), (x + 84, y + 34),
               (x + 118, y + 20), (x + 152, y + 22), (x + w - 10, y + 8)]
        d.line(pts, fill=(255, 255, 255), width=3)
        d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4,
                   pts[-1][1] + 4], fill=(255, 220, 60))
    elif kind == "dawn":
        for i in range(6):
            col = [(70, 40, 110), (120, 60, 120), (190, 90, 90),
                   (230, 130, 70), (240, 170, 90), (250, 200, 120)][i]
            d.rectangle([x, y + i * h // 6, x + w, y + (i + 1) * h // 6],
                        fill=col)
        d.ellipse([x + w - 52, y + 6, x + w - 28, y + 30], fill=(255, 230, 140))
        for bx, bw in [(20, 40), (70, 30), (150, 44)]:
            d.rectangle([x + bx, y + h - 22, x + bx + bw, y + h],
                        fill=(20, 16, 24))
        for sx, sy, r in [(120, 10, 8), (128, 18, 10), (136, 8, 7)]:
            d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                      fill=(120, 110, 115))
    elif kind == "jets":
        d.rectangle([x, y, x + w, y + h], fill=(70, 140, 210))
        for cy in (14, 40):
            d.ellipse([x + 120, y + cy - 8, x + 136, y + cy + 8],
                      fill=(255, 255, 255))
        for jx, jy in [(52, 18), (96, 34)]:
            d.line([x + jx - 34, y + jy + 6, x + jx, y + jy],
                   fill=(255, 255, 255), width=2)
            d.polygon([(x + jx, y + jy - 4), (x + jx + 26, y + jy),
                       (x + jx, y + jy + 4)], fill=(30, 34, 44))
            d.polygon([(x + jx + 4, y + jy - 12), (x + jx + 12, y + jy),
                       (x + jx + 4, y + jy + 2)], fill=(30, 34, 44))
        for r in (10, 18, 26):
            d.arc([x + w - 40 - r, y + h - 14 - r, x + w - 40 + r,
                   y + h - 14 + r], 200, 340, fill=(40, 200, 120), width=2)
    elif kind == "tanker":
        d.rectangle([x, y, x + w, y + h], fill=(230, 120, 50))
        d.ellipse([x + w - 46, y + 4, x + w - 22, y + 28], fill=(255, 220, 120))
        d.rectangle([x, y + 30, x + w, y + h], fill=(20, 50, 90))
        d.rectangle([x + 44, y + 24, x + w - 14, y + 38], fill=(18, 18, 22))
        for fx in (66, 96, 126):
            d.rectangle([x + fx, y + 12, x + fx + 10, y + 26],
                        fill=(30, 30, 34))
            d.polygon([(x + fx - 2, y + 14), (x + fx + 12, y + 14),
                       (x + fx + 5, y + 2)], fill=(255, 160, 30))
        d.rectangle([x + w - 34, y + 18, x + w - 14, y + 26],
                    fill=(240, 240, 235))
    elif kind == "derrick":
        d.rectangle([x, y, x + w, y + h], fill=(150, 100, 55))
        d.ellipse([x + 14, y + 4, x + 36, y + 26], fill=(255, 210, 100))
        cx = x + w - 62
        d.line([cx, y + 6, cx - 22, y + h - 10], fill=(40, 26, 14), width=3)
        d.line([cx, y + 6, cx + 22, y + h - 10], fill=(40, 26, 14), width=3)
        d.line([cx - 16, y + 22, cx + 16, y + 22], fill=(40, 26, 14), width=2)
        d.line([cx - 10, y + 36, cx + 10, y + 36], fill=(40, 26, 14), width=2)
        for bx in (x + 18, x + 40):
            d.ellipse([bx, y + h - 16, bx + 16, y + h - 4], fill=(60, 40, 20))
        d.rectangle([x + 70, y + h - 12, x + w - 20, y + h - 6],
                    fill=(40, 26, 14))
    elif kind == "blast":
        d.rectangle([x, y, x + w, y + h], fill=(24, 18, 16))
        cx, cy = x + w // 2 + 12, y + h // 2 + 2
        for r, col in [(24, (255, 200, 60)), (17, (255, 140, 30)),
                       (10, (255, 220, 140))]:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        for sx, sy, r in [(cx - 34, cy - 16, 8), (cx + 36, cy - 12, 7),
                          (cx - 30, cy + 14, 6)]:
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(90, 85, 85))
        for _ in range(10):
            dx, dy = rng.randint(-70, 70), rng.randint(-20, 18)
            d.ellipse([cx + dx - 1, cy + dy - 1, cx + dx + 1, cy + dy + 1],
                      fill=(255, 180, 60))
    elif kind == "tower":
        d.rectangle([x, y, x + w, y + h], fill=(16, 22, 52))
        d.ellipse([x + w - 40, y + 4, x + w - 22, y + 22], fill=(235, 235, 210))
        d.rectangle([x + 78, y + 8, x + 128, y + h - 4], fill=(52, 58, 88))
        for wy in range(y + 14, y + h - 8, 11):
            for wx in range(x + 84, x + 124, 13):
                if rng.random() < 0.55:
                    d.rectangle([wx, wy, wx + 7, wy + 6], fill=(255, 210, 90))
        d.rectangle([x + 30, y + 30, x + 62, y + h - 4], fill=(38, 44, 70))
    elif kind == "ticker":
        d.rectangle([x, y, x + w, y + h], fill=(5, 35, 20))
        f1 = font("sans_b", 10)
        f2 = font("sans_b", 10)
        tx = x + 30
        d.text((tx, y + 7), "DOW", font=f1, fill=(255, 255, 255))
        t = "+0.33%"
        d.text((x + w - 8 - tw(d, t, f2), y + 7), t, font=f2,
               fill=(60, 220, 120))
        d.polygon([(x + w - 8 - tw(d, t, f2) - 12, y + 16),
                   (x + w - 8 - tw(d, t, f2) - 4, y + 16),
                   (x + w - 8 - tw(d, t, f2) - 8, y + 8)],
                  fill=(60, 220, 120))
        d.text((tx, y + 25), "NASDAQ", font=f1, fill=(255, 255, 255))
        t2 = "-0.62%"
        d.text((x + w - 8 - tw(d, t2, f2), y + 25), t2, font=f2,
               fill=(255, 90, 80))
        d.polygon([(x + w - 8 - tw(d, t2, f2) - 12, y + 28),
                   (x + w - 8 - tw(d, t2, f2) - 4, y + 28),
                   (x + w - 8 - tw(d, t2, f2) - 8, y + 36)],
                  fill=(255, 90, 80))


HERO_SCENES = {"tariff": scene_tariff, "launch": scene_launch,
               "court": scene_court}

# ---------------------------------------------------------------- map
LAND = [
    (-170, -55, 15, 71), (-80, -35, -56, 11), (-58, -18, 60, 84),
    (-11, 41, 36, 71), (-18, 51, -35, 36), (40, 181, 5, 76),
    (113, 154, -40, -10), (95, 105, 5, 20), (129, 142, 30, 46),
]


def on_land(lon, lat):
    for lo0, lo1, la0, la1 in LAND:
        if lo0 <= lon <= lo1 and la0 <= lat <= la1:
            return True
    return False


def build_map(d, x, y, w, h):
    top_c, bot_c = (12, 34, 78), (10, 92, 96)
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = tuple(int(top_c[i] + (bot_c[i] - top_c[i]) * t) for i in range(3))
        d.line([x, y + yy, x + w, y + yy], fill=col)
    d.rectangle([x, y, x + w, y + h], outline=(255, 255, 255), width=1)
    for lon in range(-180, 181, 30):
        gx = x + (lon + 180) / 360 * w
        d.line([gx, y, gx, y + h], fill=(150, 180, 185))
    for lat in range(-60, 91, 30):
        gy = y + (85 - lat) / 145 * h
        d.line([x, gy, x + w, gy], fill=(150, 180, 185))
    lon = -180
    while lon <= 180:
        lat = -55
        while lat <= 85:
            if on_land(lon, lat):
                px = x + (lon + 180) / 360 * w
                py = y + (85 - lat) / 145 * h
                d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6],
                          fill=(230, 190, 80))
            lat += 5
        lon += 5
    all_items = HEROES + CARDS
    for item in all_items:
        lon, lat = item["pin"]
        px = x + (lon + 180) / 360 * w
        py = y + (85 - lat) / 145 * h
        dx, dy = PIN_OFFSETS.get(item["num"], (0, 0))
        bx, by = px + dx, py + dy
        bx = max(x + 11, min(x + w - 11, bx))
        by = max(y + 11, min(y + h - 11, by))
        d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5],
                  fill=(255, 210, 90), outline=(255, 255, 255))
        if abs(dx) + abs(dy) > 0:
            d.line([px, py, bx, by], fill=(255, 255, 255), width=1)
        badge(d, bx, by, item["num"], r=9, size=9)


# ---------------------------------------------------------------- build
def main():
    rng = random.Random(20261125)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 16
    right = W - mx

    d.rectangle([0, 0, W, 5], fill=INK)

    hf = font("sans_b", 12)
    d.text((mx, 12), "ONE DAY OF WORLD NEWS", font=hf, fill=RED)
    hr = font("sans_b", 11)
    rt = "38 STORIES · 7 REGIONS · 20 FIELDS · EVERY ONE FROM WEDNESDAY 25 NOVEMBER 2026"
    if tw(d, rt, hr) > W - 2 * mx - tw(d, "ONE DAY OF WORLD NEWS", hf) - 20:
        note("header right too wide")
    d.text((right - tw(d, rt, hr), 13), rt, font=hr, fill=INK)

    mast = "Wednesday 25 November 2026"
    mf = fit_single(d, mast, "serif_b", 62, 40, W - 2 * mx)
    mw = tw(d, mast, mf)
    d.text(((W - mw) / 2, 30), mast, font=mf, fill=INK)
    mast_bottom = 30 + mf.size + 6

    dek = ("US proposes tariffs on 14 partners · Shenzhou-24 launches with "
           "first foreign astronaut · Judges urge Netanyahu bribery case dropped")
    df = fit_single(d, dek, "serif_i", 17, 12, W - 2 * mx)
    dw = tw(d, dek, df)
    d.text(((W - dw) / 2, mast_bottom + 2), dek, font=df, fill=RED)

    tab_y, tab_h = 128, 22
    tab_w = (W - 2 * mx) / 7
    tf = font("sans_b", 10)
    for i, (name, col, cnt) in enumerate(REGIONS):
        tx0 = mx + i * tab_w
        d.rectangle([tx0, tab_y, tx0 + tab_w - 2, tab_y + tab_h], fill=col)
        label = "%s %d" % (name, cnt)
        lf = tf
        if tw(d, label, lf) > tab_w - 8:
            lf = font("sans_b", 9)
        d.text((tx0 + (tab_w - 2 - tw(d, label, lf)) / 2, tab_y + 5),
               label, font=lf, fill=(255, 255, 255))

    ns_y, ns_h = 156, 62
    d.rectangle([mx, ns_y, mx + 92, ns_y + ns_h], fill=INK)
    nf = font("sans_b", 9)
    for i, line in enumerate(["THE DAY", "IN NUMBERS", "WEDNESDAY"]):
        lw = tw(d, line, nf)
        d.text((mx + (92 - lw) / 2, ns_y + 8 + i * 16), line, font=nf,
               fill=(255, 255, 255))
    cell_w = (W - 2 * mx - 92) / 6
    for i, (place, figure, label) in enumerate(NUMBERS):
        cx0 = mx + 92 + i * cell_w
        pf = font("sans_b", 8)
        d.text((cx0 + 10, ns_y + 5), place, font=pf, fill=GREY)
        ff = fit_single(d, figure, "serif_b", 28, 16, cell_w - 20)
        d.text((cx0 + 10, ns_y + 17), figure, font=ff, fill=RED)
        lf = font("sans", 9)
        lines = wrap(d, label, lf, cell_w - 20)
        if len(lines) > 2:
            note("numbers label overflow: %r" % label)
            lines = lines[:2]
        draw_lines(d, lines, cx0 + 10, ns_y + 44, lf, INK, 11)

    hero_y = 226
    hero_w = int((W - 2 * mx - 16) / 3)
    heroes_bottom = hero_y
    for i, item in enumerate(HEROES):
        hx = mx + i * (hero_w + 8)
        sx, sy, sw, sh = hx, hero_y, hero_w, 118
        if item["scene"] == "launch":
            HERO_SCENES[item["scene"]](d, sx, sy, sw, sh, rng)
        else:
            HERO_SCENES[item["scene"]](d, sx, sy, sw, sh)
        badge(d, sx + 14, sy + 14, item["num"], r=11, size=11)
        py = sy + sh + 6
        pf = font("sans_b", 10)
        d.text((hx, py), item["place"], font=pf, fill=RED)
        pill(d, hx + hero_w, py - 1, item["pill"], size=8)
        hf2, hlines = fit_block(d, item["head"], "serif_b", 19, 15,
                                hero_w, 2, 1.2)
        hy = py + 16
        draw_lines(d, hlines, hx, hy, hf2, INK, int(hf2.size * 1.2))
        sf, slines = fit_block(d, item["summ"], "sans", 11, 9,
                               hero_w, 3, 1.25)
        summ_y = hy + len(hlines) * int(hf2.size * 1.2) + 3
        draw_lines(d, slines, hx, summ_y,
                   sf, INK, int(sf.size * 1.25))
        heroes_bottom = max(heroes_bottom,
                            summ_y + len(slines) * int(sf.size * 1.25))

    card_w = int((W - 2 * mx - 32) / 5)
    card_y0 = heroes_bottom + 6
    row_h, row_gap = 114, 8
    for idx, item in enumerate(CARDS):
        row, col = divmod(idx, 5)
        cx0 = mx + col * (card_w + 8)
        cy0 = card_y0 + row * (row_h + row_gap)
        scene_card(d, item["scene"], cx0, cy0, card_w, 52, rng)
        tag_chip(d, cx0, cy0 + 52, item["tag"])
        badge(d, cx0 + 11, cy0 + 11, item["num"], r=8, size=8)
        py = cy0 + 55
        pf = font("sans_b", 9)
        d.text((cx0, py), item["place"], font=pf, fill=RED)
        pill(d, cx0 + card_w, py - 1, item["pill"], size=7)
        hf2, hlines = fit_block(d, item["head"], "serif_b", 13, 11,
                                card_w, 2, 1.15)
        hy = py + 13
        draw_lines(d, hlines, cx0, hy, hf2, INK, int(hf2.size * 1.15))
        sf, slines = fit_block(d, item["summ"], "sans", 10, 8,
                               card_w, 2, 1.2)
        draw_lines(d, slines, cx0,
                   hy + len(hlines) * int(hf2.size * 1.15) + 2,
                   sf, INK, int(sf.size * 1.2))
    cards_bottom = card_y0 + 2 * row_h + row_gap

    bh_y = cards_bottom + 6
    d.line([mx, bh_y, right, bh_y], fill=INK, width=2)
    bf = font("sans_b", 11)
    btitle = "ALSO ON WEDNESDAY 25 NOVEMBER — 25 MORE, BY REGION"
    d.text((mx, bh_y + 5), btitle, font=bf, fill=INK)
    nf2 = font("sans", 8)
    note_t = "Sources in brackets · * = one side's claim"
    d.text((right - tw(d, note_t, nf2), bh_y + 7), note_t, font=nf2,
           fill=GREY)

    brief_y0 = bh_y + 22
    col_w = (668 - mx - 8) / 2
    for ci in range(2):
        items = BRIEFS[:13] if ci == 0 else BRIEFS[13:]
        bx0 = mx + ci * (col_w + 8)
        for ri, (region, field, text, src) in enumerate(items):
            ry = brief_y0 + ri * 19
            num = 14 + ci * 13 + ri
            nf3 = font("sans_b", 10)
            d.text((bx0, ry), "%d." % num, font=nf3, fill=INK)
            num_w = tw(d, "%d." % num, nf3)
            dot_cx = bx0 + num_w + 8
            d.ellipse([dot_cx - 3, ry + 4, dot_cx + 3, ry + 10],
                      fill=REGION_COLOUR[region])
            tx = dot_cx + 7
            words = text.split()
            bold_part = " ".join(words[:3])
            rest_part = " " + " ".join(words[3:]) if len(words) > 3 else ""
            size = 11
            while size >= 9:
                bfont = font("sans_b", size)
                rfont = font("sans", size)
                total = (tw(d, bold_part, bfont) + tw(d, rest_part, rfont)
                         + tw(d, " (%s)" % src, rfont))
                if total <= col_w - (tx - bx0) - 2:
                    break
                size -= 1
            bfont = font("sans_b", size)
            rfont = font("sans", size)
            if size < 9:
                note("brief overflow: %r" % text)
            cur_x = tx
            d.text((cur_x, ry), bold_part, font=bfont, fill=INK)
            cur_x += tw(d, bold_part, bfont)
            if rest_part:
                d.text((cur_x, ry), rest_part, font=rfont, fill=INK)
                cur_x += tw(d, rest_part, rfont)
            d.text((cur_x, ry), " (%s)" % src, font=rfont, fill=GREY)
    briefs_bottom = brief_y0 + 13 * 19

    map_x, map_w = 668, right - 668
    map_title_y = bh_y + 5
    mt = font("sans_b", 10)
    d.text((map_x, map_title_y), "WHERE IT HAPPENED · PINS 1–13",
           font=mt, fill=INK)
    map_y = brief_y0
    map_h = 178
    build_map(d, map_x, map_y, map_w, map_h)
    leg_y = map_y + map_h + 8
    lf = font("sans_b", 8)
    lx, ly = map_x, leg_y
    for name, col, cnt in REGIONS:
        label = "%s %d" % (name, cnt)
        lw = tw(d, label, lf)
        if lx + 10 + lw > right:
            lx = map_x
            ly += 13
        d.ellipse([lx, ly + 2, lx + 7, ly + 9], fill=col)
        d.text((lx + 10, ly), label, font=lf, fill=INK)
        lx += 10 + lw + 12

    dc_y = briefs_bottom + 6
    dc_f, dc_lines = fit_block(d, DATE_CHECK, "sans_b", 10, 9,
                               W - 2 * mx - 20, 2, 1.2)
    dc_h = 8 + len(dc_lines) * int(dc_f.size * 1.2)
    d.rectangle([mx, dc_y, right, dc_y + dc_h], fill=RED)
    draw_lines(d, dc_lines, mx + 10, dc_y + 4, dc_f, (255, 255, 255),
               int(dc_f.size * 1.2))

    ff = font("sans", 8)
    fw = tw(d, FOOTER, ff)
    if fw > W - 2 * mx:
        note("footer overflow")
    d.text(((W - fw) / 2, dc_y + dc_h + 4), FOOTER, font=ff, fill=GREY)
    if dc_y + dc_h + 4 + 10 > H:
        note("footer runs past bottom edge")

    total = len(HEROES) + len(CARDS) + len(BRIEFS)
    fields = set()
    for item in HEROES + CARDS:
        fields.add(item["field"])
    for _, field, _, _ in BRIEFS:
        fields.add(field)
    region_counts = {name: cnt for name, _, cnt in REGIONS}
    print("region counts:", region_counts)
    print("stories total:", total)
    print("fields:", len(fields), sorted(fields))
    print("overflows:", len(OVERFLOWS))
    for o in OVERFLOWS:
        print("  OVERFLOW:", o)
    assert total == 38, total
    assert len(fields) == 20, len(fields)
    assert sum(region_counts.values()) == 38, region_counts
    assert not OVERFLOWS, OVERFLOWS

    img.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
