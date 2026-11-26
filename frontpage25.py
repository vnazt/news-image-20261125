#!/usr/bin/env python3
"""frontpage25.py — 'THE WORLD IN ONE DAY', Wednesday 25 November 2026.

Fresh authoring for news-image-20261125, built on the ni24 v2-fixed anatomy:
header counts line, giant serif masthead + red dek naming the 3 heroes,
region tabs, THE DAY IN NUMBERS strip, 3 numbered heroes, pictured cards,
numbered briefs 14-38 with region dots, dot-matrix world map with pins 1-13,
red DATE CHECK box.

Numbering: the 13 pictured items are the 3 heroes (pins 1-3) + 10 mid cards
(pins 4-13); briefs run 14-38 (25 briefs). 13 + 25 = 38 stories exactly.
The header count is honest.

All 38 stories verified >=2 named sources (dossier research/stories.md).
Heroes: US tariffs on 14 partners · Shenzhou-24 launch, first foreign
astronaut · judges urge Netanyahu bribery case dropped.
Local render only: python3 + Pillow, no network, deterministic.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---------------------------------------------------------------- fonts
def _font(name, size, bold=False):
    cands = []
    if name == "serif":
        cands = [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf" % ("Bold" if bold else "Regular"),
            "/usr/share/fonts/truetype/liberation/LiberationSerif-%sItalic.ttf" % ("Bold" if bold else ""),
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif%s.ttf" % ("-Bold" if bold else ""),
        ]
    else:
        cands = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % ("Bold" if bold else "Regular"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
        ]
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def Fserif(s, bold=False):
    return _font("serif", s, bold)

def Fsans(s, bold=False):
    return _font("sans", s, bold)

def Fserif_it(s):
    p = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
    if os.path.exists(p):
        return ImageFont.truetype(p, s)
    return Fserif(s)

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 236)
INK = (18, 18, 18)
RED = (178, 34, 34)
DARKRED = (140, 20, 20)
GREY = (90, 88, 84)
LINE = (200, 192, 178)
TEAL = (13, 110, 110)      # OFFICIAL
GREEN = (34, 128, 60)      # CONFIRMED
AMBER = (176, 110, 0)      # REPORTED
CLAIMRED = (178, 34, 34)   # CLAIM
NAVY = (10, 42, 80)
TEALDEEP = (12, 92, 112)
GOLD = (240, 183, 92)
GOLDDARK = (214, 148, 52)
PINRED = (204, 32, 24)

REGIONS = [
    # name, colour, count (computed below, asserted)
    ("EUROPE", (52, 110, 180)),
    ("MIDDLE EAST", (18, 130, 110)),
    ("AFRICA", (205, 120, 30)),
    ("ASIA-PACIFIC", (178, 40, 40)),
    ("OCEANIA", (120, 80, 170)),
    ("AMERICAS", (190, 40, 110)),
    ("WORLD & SCIENCE", (90, 90, 95)),
]
RHEX = {name: col for name, col in REGIONS}

PILL_FILL = {"OFFICIAL": TEAL, "CONFIRMED": GREEN, "REPORTED": AMBER, "CLAIM": CLAIMRED}

# ---------------------------------------------------------------- data
# fields are used to compute the "20 FIELDS" header count honestly.
HEROES = [
    dict(num=1, region="AMERICAS", field="trade", place="WASHINGTON · TRADE",
         pill="OFFICIAL", tag="14 PARTNERS",
         head="US proposes new tariffs on 14 trading partners",
         summ=("China faces a 20% top rate; public hearing on 25 January. "
               "Reuters, USTR"),
         scene="tariff", pin=(-77.0, 38.9)),
    dict(num=2, region="ASIA-PACIFIC", field="space", place="JIUQUAN · SPACE",
         pill="CONFIRMED", tag="08:18 BEIJING",
         head="Shenzhou-24 launches with first foreign astronaut",
         summ=("Pakistan's Zeeshan Ali, 40, joins the Tiangong crew for "
               "5-10 days. Xinhua, Aviation Week"),
         scene="launch", pin=(100.3, 40.9)),
    dict(num=3, region="MIDDLE EAST", field="courts", place="JERUSALEM · COURTS",
         pill="CONFIRMED", tag="CASE 4000",
         head="Judges urge Netanyahu bribery case be dropped",
         summ=("Case 4000 drop recommended; Case 2000 reconsidered. "
               "Not a ruling yet. Reuters, CNN"),
         scene="court", pin=(35.2, 31.8)),
]

CARDS = [
    dict(num=4, region="AFRICA", field="disaster", place="GIZA",
         pill="CONFIRMED", tag="31 DEAD",
         head="Fuel tanker blast in Giza kills 31",
         summ="27 vehicles burned; toll rose from 21 overnight. Reuters, CNN",
         scene="smoke", pin=(31.2, 30.0), bg=(110, 74, 50)),
    dict(num=5, region="OCEANIA", field="diplomacy", place="CANBERRA",
         pill="OFFICIAL", tag="$740M",
         head="Solomon picks Australia, bars foreign bases",
         summ="Wale-Albanese sign pact; $740m over 10 years. AP, CNN",
         scene="capitol", pin=(149.1, -35.3), bg=(40, 70, 110)),
    dict(num=6, region="ASIA-PACIFIC", field="labour", place="DHAKA",
         pill="CONFIRMED", tag="+36%",
         head="Bangladesh lifts garment wage 36%",
         summ="Minimum now 17,000 taka; smallest rise since 1986. AP, AFP",
         scene="chart", pin=(90.4, 23.8), bg=(30, 96, 66)),
    dict(num=7, region="AFRICA", field="war", place="DAMAZIN",
         pill="REPORTED", tag="19 DEAD",
         head="RSF drone strike kills 19 in Blue Nile",
         summ="Reported Wed; 19 dead in Damazin, 20 hurt. Reuters",
         scene="dawn", pin=(34.5, 11.8), bg=(70, 60, 92)),
    dict(num=8, region="EUROPE", field="defence", place="POLAND · EAST BORDER",
         pill="OFFICIAL", tag="NO-FLY ZONE",
         head="Poland plans no-fly zone on east border",
         summ="Strip tens of km wide; rules due by early January. Reuters",
         scene="jets", pin=(23.5, 52.0), bg=(30, 50, 90)),
    dict(num=9, region="MIDDLE EAST", field="security", place="JEDDAH",
         pill="REPORTED", tag="PORT THREAT",
         head="Houthis threaten Jeddah port; Hodeidah hit",
         summ="Coalition bombs Hodeidah; 4 drones downed. Reuters",
         scene="tanker", pin=(39.2, 21.5), bg=(96, 58, 44)),
    dict(num=10, region="MIDDLE EAST", field="energy", place="RAS TANURA",
         pill="CLAIM", tag="BRENT +3.5%",
         head="Houthis claim Ras Tanura refinery strike",
         summ="Brent closes $94.61, +3.5%; claim unverified. Reuters",
         scene="derrick", pin=(50.1, 26.6), bg=(92, 70, 30)),
    dict(num=11, region="EUROPE", field="war", place="SAVASLEYKA",
         pill="REPORTED", tag="5 JETS HIT",
         head="Ukraine hits Savasleyka: 5 jets damaged",
         summ="3 MiG-31s, 2 Su-34s hit 680 km inside Russia. Reuters",
         scene="blast", pin=(43.3, 55.6), bg=(60, 50, 70)),
    dict(num=12, region="MIDDLE EAST", field="war", place="GAZA CITY",
         pill="CONFIRMED", tag="02:46",
         head="Israel kills Hamas security chief in Gaza",
         summ="Abu al-Aouf dies with family in Al-Shati strike. CNN, IDF",
         scene="tower", pin=(34.5, 31.5), bg=(58, 74, 96)),
    dict(num=13, region="AMERICAS", field="markets", place="NEW YORK",
         pill="CONFIRMED", tag="DOW +0.33%",
         head="Dow swings +0.33% after 1,100-point dive",
         summ="S&P -0.25%, Nasdaq -0.62%; Nvidia -4%. Reuters",
         scene="ticker", pin=(-74.0, 40.7), bg=(20, 60, 40)),
]

# Briefs: one line each (<= ~66 chars incl. source), numbered 14-38.
# (region, field, text, source)
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
    # (place, figure, label)
    ("WASHINGTON", "14", "partners hit by new tariffs"),
    ("CHINA", "20%", "top tariff rate proposed"),
    ("GIZA", "31", "killed in fuel-tanker fire"),
    ("LONDON", "$94.61", "Brent close Wed (+3.5%)"),
    ("MUMBAI", "+1,502", "Sensex points in a day"),
    ("US · OCTOBER", "3.8%", "PCE inflation, year on year"),
]

DATECHECK = ("DATE CHECK — Left off as earlier news: ICJ Myanmar ruling (19 Nov) · "
             "Sarkozy trial order (24 Nov) · Venezuela debt plan published (24 Nov) · "
             "Hormuz mine strikes (22 Nov) · Sinner surgery (24 Nov) · CIA breach "
             "first reported (24 Nov) · Malaysia refugee return (24 Nov) · Hong Kong "
             "fire anniversary (26 Nov) · Shenzhou crew named (24 Nov)")

FOOTER = ("Every story happened or was first reported on Wednesday 25 Nov 2026, UTC. "
          "Times shown are UTC unless marked local. Sources named on each item · "
          "Original drawings, no photos.")

# ---------------------------------------------------------------- helpers
OVERFLOWS = []

def text_w(d, x, y, s, font, fill=INK, anchor="la"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)

def wrap(s, font, width):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(d, x, y, s, font, width, leading, fill=INK, max_lines=None):
    """Draw wrapped text; record an overflow if it needs more lines than max."""
    lines = wrap(s, font, width)
    if max_lines is not None and len(lines) > max_lines:
        OVERFLOWS.append("'%s' needs %d lines, max %d" % (s[:40], len(lines), max_lines))
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=font, fill=fill)
    return len(lines)

def fit_size(s, font_fn, width, start, minimum=8):
    """Largest font size (<=start) at which s fits width; records overflow if < minimum."""
    sz = start
    while sz > minimum and font_fn(sz).getlength(s) > width:
        sz -= 1
    if font_fn(sz).getlength(s) > width:
        OVERFLOWS.append("cannot fit '%s' in %d px even at %d" % (s[:40], width, minimum))
    return sz

def pill(d, x, y, label, h=13):
    f = Fsans(8, bold=True)
    w = int(f.getlength(label)) + 10
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=PILL_FILL[label])
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w

def num_badge(d, cx, cy, n, r=11, fill=RED):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=(255, 255, 255), width=2)
    f = Fsans(11, bold=True)
    t = str(n)
    d.text((cx - f.getlength(t) / 2, cy - 6), t, font=f, fill=(255, 255, 255))

def vgrad(d, box, top, bot):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1):
        t = (yy - y0) / max(1, (y1 - y0 - 1))
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(x0, yy), (x1, yy)], fill=c)

# ---------------------------------------------------------------- scenes
def scene_shanghai(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (24, 34, 66), (214, 110, 60))
    # sun
    d.ellipse([x + w - 78, y + 14, x + w - 38, y + 54], fill=(240, 190, 90))
    # skyline silhouettes
    import random
    rnd = random.Random(7)
    bx = x + 6
    while bx < x + w - 14:
        bw = rnd.randint(12, 26)
        bh = rnd.randint(int(h * 0.30), int(h * 0.62))
        d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(22, 26, 44))
        for wy in range(y + h - bh + 6, y + h - 6, 10):
            for wx in range(bx + 3, bx + bw - 3, 7):
                if rnd.random() < 0.5:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(250, 200, 90))
        bx += bw + 4
    # Oriental Pearl Tower
    tx = x + w // 2
    d.line([(tx, y + 8), (tx, y + h)], fill=(30, 32, 52), width=4)
    d.ellipse([tx - 13, y + 26, tx + 13, y + 52], fill=(30, 32, 52))
    d.ellipse([tx - 9, y + 62, tx + 9, y + 80], fill=(30, 32, 52))
    # red investigation banner
    d.rectangle([x, y + h - 20, x + w, y + h], fill=RED)
    f = Fsans(10, bold=True)
    t = "UNDER INVESTIGATION"
    d.text((x + w / 2 - f.getlength(t) / 2, y + h - 16), t, font=f, fill=(255, 255, 255))

def scene_court(d, x, y, w, h, badge="10 OF 12"):
    vgrad(d, (x, y, x + w, y + h), (96, 66, 44), (52, 34, 22))
    # bench
    d.rectangle([x + 18, y + h - 46, x + w - 18, y + h - 8], fill=(40, 26, 16))
    d.rectangle([x + 18, y + h - 52, x + w - 18, y + h - 46], fill=(120, 84, 48))
    # scales of justice
    cx, cy = x + w // 2, y + 22
    d.line([(cx, cy), (cx, cy + 44)], fill=(232, 200, 120), width=3)
    d.line([(cx - 34, cy + 8), (cx + 34, cy + 8)], fill=(232, 200, 120), width=3)
    for sgn in (-1, 1):
        px = cx + sgn * 34
        d.line([(px, cy + 8), (px, cy + 26)], fill=(232, 200, 120), width=2)
        d.pieslice([px - 13, cy + 22, px + 13, cy + 40], 0, 180, fill=(232, 200, 120))
    # gavel
    d.rectangle([x + w - 62, y + h - 62, x + w - 30, y + h - 54], fill=(150, 104, 58))
    d.line([(x + w - 46, y + h - 54), (x + w - 46, y + h - 46)], fill=(150, 104, 58), width=4)
    # verdict badge (top-right, clear of the number badge)
    f = Fserif(20, bold=True)
    t = badge
    tw = f.getlength(t)
    d.rectangle([x + w - 18 - tw, y + 8, x + w - 10, y + 32], fill=(255, 255, 255))
    d.text((x + w - 14 - tw, y + 10), t, font=f, fill=DARKRED)

def scene_ship(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (16, 30, 58), (8, 18, 38))
    # stars / radar arcs
    cx, cy = x + w - 52, y + 40
    for r in (34, 24, 14):
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(90, 200, 160), width=2)
    # drones with trails
    for (dx, dy, ln) in ((x + 40, y + 26, 26), (x + 88, y + 16, 20), (x + 130, y + 34, 30)):
        d.line([(dx - ln, dy + 8), (dx, dy)], fill=(255, 190, 80), width=2)
        d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(255, 210, 110))
    # sea
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(10, 40, 66))
    for wx in range(x + 8, x + w - 8, 26):
        d.line([(wx, y + h - 26), (wx + 14, y + h - 26)], fill=(70, 140, 180), width=2)
    # cargo ship
    sx, sy = x + 30, y + h - 52
    d.rectangle([sx, sy, sx + 190, sy + 20], fill=(28, 30, 40))
    for i, col in enumerate(((200, 60, 50), (40, 110, 160), (220, 170, 60))):
        d.rectangle([sx + 14 + i * 52, sy - 22, sx + 52 + i * 52, sy], fill=col)
    # bridge tower with a human figure in the lit window
    d.rectangle([sx + 196, sy - 44, sx + 224, sy], fill=(38, 42, 56))
    d.rectangle([sx + 200, sy - 40, sx + 220, sy - 22], fill=(250, 205, 110))
    fx = sx + 210
    d.ellipse([fx - 4, sy - 38, fx + 4, sy - 30], fill=(20, 20, 26))   # head
    d.rectangle([fx - 4, sy - 30, fx + 4, sy - 22], fill=(20, 20, 26))  # body
    d.line([(fx - 6, sy - 27), (fx + 6, sy - 27)], fill=(20, 20, 26), width=2)  # shoulders
    # mast + flag
    d.line([(sx + 210, sy - 44), (sx + 210, sy - 62)], fill=(200, 200, 200), width=2)
    d.polygon([(sx + 210, sy - 62), (sx + 226, sy - 58), (sx + 210, sy - 54)], fill=(220, 60, 50))

def scene_tariff(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (28, 52, 96), (14, 26, 54))
    # crane silhouette
    d.line([(x + 20, y + 10), (x + 20, y + h - 6)], fill=(16, 20, 36), width=5)
    d.line([(x + 20, y + 12), (x + w - 16, y + 12)], fill=(16, 20, 36), width=4)
    d.line([(x + w - 60, y + 12), (x + w - 34, y + h - 40)], fill=(16, 20, 36), width=2)
    # container stacks
    cols = [(200, 60, 50), (40, 110, 160), (220, 170, 60), (60, 140, 90)]
    for row in range(2):
        for i, col in enumerate(cols):
            bx = x + 34 + i * 62
            by = y + h - 34 - row * 26
            d.rectangle([bx, by, bx + 56, by + 22], fill=col)
            for lx in range(bx + 6, bx + 56, 12):
                d.line([(lx, by + 3), (lx, by + 19)], fill=(255, 255, 255, 90), width=1)
    # big rate badge, top-right
    f = Fserif(30, bold=True)
    t = "20%"
    tw = f.getlength(t)
    d.rectangle([x + w - 16 - tw, y + 8, x + w - 8, y + 44], fill=(255, 255, 255))
    d.text((x + w - 12 - tw, y + 10), t, font=f, fill=DARKRED)
    # red banner
    d.rectangle([x, y + h - 20, x + w, y + h], fill=RED)
    f = Fsans(10, bold=True)
    t = "NEW TARIFFS · 14 PARTNERS"
    d.text((x + w / 2 - f.getlength(t) / 2, y + h - 16), t, font=f, fill=(255, 255, 255))

def scene_launch(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (16, 24, 54), (8, 12, 30))
    # stars
    for (sx, sy) in ((x + 14, y + 40), (x + 46, y + 10), (x + 60, y + 18),
                     (x + w - 18, y + 10), (x + w - 36, y + 20), (x + w - 54, y + 34),
                     (x + 30, y + 70), (x + w - 70, y + 60)):
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(230, 235, 250))
    # launch gantry left of the rocket
    d.rectangle([x + 30, y + 6, x + 38, y + h - 6], fill=(120, 125, 135))
    d.line([(x + 38, y + 14), (x + w // 2 - 14, y + 14)], fill=(120, 125, 135), width=3)
    d.line([(x + 38, y + 30), (x + w // 2 - 14, y + 30)], fill=(120, 125, 135), width=3)
    # rocket body (wide, with red nose cone)
    cx = x + w // 2
    d.polygon([(cx, y + 2), (cx + 8, y + 16), (cx - 8, y + 16)], fill=(200, 60, 50))
    d.polygon([(cx + 8, y + 16), (cx + 16, y + 30), (cx + 16, y + h - 20),
               (cx - 16, y + h - 20), (cx - 16, y + 30), (cx - 8, y + 16)],
              fill=(235, 235, 230))
    d.ellipse([cx - 7, y + 22, cx + 7, y + 38], fill=(60, 140, 200))
    d.rectangle([cx - 16, y + 44, cx + 16, y + 48], fill=(200, 60, 50))
    d.polygon([(cx - 16, y + h - 20), (cx - 28, y + h - 6), (cx - 16, y + h - 10)],
              fill=(200, 60, 50))
    d.polygon([(cx + 16, y + h - 20), (cx + 28, y + h - 6), (cx + 16, y + h - 10)],
              fill=(200, 60, 50))
    # exhaust plume + pad
    for (px, py, r) in ((cx - 10, y + h - 12, 8), (cx + 8, y + h - 10, 9), (cx, y + h - 18, 7)):
        d.ellipse([px - r, py - r, px + r, py + r], fill=(250, 180, 60))
    for (px, py, r) in ((cx - 6, y + h - 12, 4), (cx + 5, y + h - 10, 5)):
        d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 240, 180))
    d.rectangle([cx - 34, y + h - 4, cx + 34, y + h], fill=(90, 95, 105))
    # red banner
    d.rectangle([x, y + h - 20, x + w, y + h], fill=RED)
    f = Fsans(10, bold=True)
    t = "FIRST FOREIGN ASTRONAUT"
    d.text((x + w / 2 - f.getlength(t) / 2, y + h - 16), t, font=f, fill=(255, 255, 255))

def scene_court_netanyahu(d, x, y, w, h):
    scene_court(d, x, y, w, h, badge="CASE 4000")

def card_scene(d, x, y, w, h, kind, tag, bg):
    d.rectangle([x, y, x + w, y + h], fill=bg)
    if kind == "tower":
        vgrad(d, (x, y, x + w, y + h), (70, 88, 120), (30, 38, 60))
        # flanking skyline
        d.rectangle([x + 6, y + h - 26, x + 44, y + h], fill=(20, 22, 34))
        d.rectangle([x + w - 46, y + h - 32, x + w - 6, y + h], fill=(20, 22, 34))
        for (wx, wy) in ((x + 12, y + h - 20), (x + 26, y + h - 14),
                         (x + w - 38, y + h - 26), (x + w - 22, y + h - 18)):
            d.rectangle([wx, wy, wx + 4, wy + 4], fill=(250, 200, 90))
        d.rectangle([x, y + h - 5, x + w, y + h], fill=(14, 16, 26))
        for (sx, sy) in ((x + 48, y + 6), (x + 66, y + 12), (x + w - 58, y + 8), (x + w - 70, y + 16)):
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(220, 225, 240))
        d.rectangle([x + w // 2 - 14, y + 8, x + w // 2 + 14, y + h], fill=(24, 26, 40))
        for wy in range(y + 12, y + h - 4, 8):
            d.rectangle([x + w // 2 - 10, wy, x + w // 2 - 4, wy + 4], fill=(250, 200, 90))
            d.rectangle([x + w // 2 + 4, wy, x + w // 2 + 10, wy + 4], fill=(250, 200, 90))
        d.ellipse([x + w // 2 - 2, y + 4, x + w // 2 + 2, y + 8], fill=(240, 60, 50))
        d.ellipse([x + w - 34, y + 6, x + w - 8, y + 32], fill=(240, 150, 60))
    elif kind == "tanker":
        vgrad(d, (x, y, x + w, y + h), (150, 80, 40), (60, 30, 24))
        d.ellipse([x + w - 46, y + 4, x + w - 22, y + 28], fill=(250, 190, 90))
        # distant tanker silhouette on the horizon
        d.rectangle([x + 8, y + h - 24, x + 44, y + h - 16], fill=(40, 22, 18))
        d.rectangle([x + 18, y + h - 32, x + 26, y + h - 24], fill=(40, 22, 18))
        d.rectangle([x, y + h - 16, x + w, y + h], fill=(16, 44, 66))
        for wy in (y + h - 12, y + h - 6):
            for wx in range(x + 6, x + w - 6, 18):
                d.line([(wx, wy), (wx + 8, wy)], fill=(120, 170, 200), width=2)
        d.rectangle([x + 30, y + h - 30, x + w - 30, y + h - 16], fill=(40, 40, 48))
        d.rectangle([x + 46, y + h - 44, x + w - 46, y + h - 30], fill=(60, 60, 70))
        for fx in (x + 52, x + 96, x + 140):
            d.polygon([(fx, y + h - 44), (fx + 8, y + 8), (fx + 16, y + h - 44)], fill=(240, 130, 40))
            d.ellipse([fx + 2, y + 2, fx + 14, y + 16], fill=(250, 200, 80))
        for (gx, gy) in ((x + 60, y + 4), (x + 78, y + 10)):
            d.line([(gx, gy), (gx + 4, gy + 3), (gx + 8, gy)], fill=(230, 230, 220), width=1)
    elif kind == "chart":
        # faint volume bars behind the line
        for (bx, bh) in ((x + 64, 12), (x + 88, 20), (x + 112, 16), (x + 136, 26),
                         (x + 160, 20), (x + 178, 12)):
            d.rectangle([bx, y + h - 8 - bh, bx + 12, y + h - 8], fill=(70, 160, 110))
        d.line([(x + 8, y + h - 12), (x + w // 3, y + h - 26), (x + 2 * w // 3, y + h - 18),
                (x + w - 14, y + 8)], fill=(255, 255, 255), width=4)
        d.polygon([(x + w - 22, y + 4), (x + w - 8, y + 8), (x + w - 16, y + 18)], fill=(255, 255, 255))
        for gy in range(y + 8, y + h - 8, 12):
            d.line([(x + 6, gy), (x + w - 6, gy)], fill=(255, 255, 255, 60), width=1)
        # second, flatter trend line (dashed)
        for sx in range(x + 10, x + w - 20, 12):
            d.line([(sx, y + h - 20), (sx + 6, y + h - 22)], fill=(200, 255, 220), width=2)
    elif kind == "trophy":
        # stadium: floodlight beams + crowd + pitch
        d.line([(x + 6, y + 4), (x + w // 2 - 30, y + 30)], fill=(240, 235, 170), width=2)
        d.line([(x + w - 6, y + 4), (x + w // 2 + 30, y + 30)], fill=(240, 235, 170), width=2)
        for (cx, cy, cc) in ((x + 30, y + 10, (220, 80, 80)), (x + 42, y + 16, (240, 240, 240)),
                             (x + 52, y + 8, (90, 140, 220)), (x + w - 30, y + 10, (240, 240, 240)),
                             (x + w - 42, y + 16, (220, 80, 80)), (x + w - 52, y + 8, (240, 200, 80)),
                             (x + 32, y + 24, (240, 200, 80)), (x + w - 32, y + 24, (90, 140, 220))):
            d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=cc)
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(30, 120, 60))
        d.line([(x, y + h - 8), (x + w, y + h - 8)], fill=(255, 255, 255), width=1)
        d.ellipse([x + w // 2 - 26, y + 8, x + w // 2 + 26, y + 44], fill=(250, 205, 90))
        d.rectangle([x + w // 2 - 26, y + 8, x + w // 2 + 26, y + 26], fill=(250, 205, 90))
        d.rectangle([x + w // 2 - 4, y + 40, x + w // 2 + 4, y + h - 8], fill=(250, 205, 90))
        d.rectangle([x + w // 2 - 16, y + h - 10, x + w // 2 + 16, y + h - 6], fill=(250, 205, 90))
        d.arc([x + w // 2 - 36, y + 10, x + w // 2 - 12, y + 34], 90, 270, fill=(250, 205, 90), width=4)
        d.arc([x + w // 2 + 12, y + 10, x + w // 2 + 36, y + 34], 270, 90, fill=(250, 205, 90), width=4)
    elif kind == "dawn":
        vgrad(d, (x, y, x + w, y + h), (40, 40, 70), (220, 120, 50))
        for (sx, sy) in ((x + 20, y + 6), (x + 44, y + 12), (x + w - 20, y + 8), (x + w - 44, y + 14)):
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(230, 230, 240))
        for (gx, gy) in ((x + 30, y + 10), (x + 52, y + 16), (x + w - 40, y + 12)):
            d.line([(gx, gy), (gx + 4, gy + 3), (gx + 8, gy)], fill=(30, 28, 40), width=1)
        d.ellipse([x + w // 2 - 14, y + h - 30, x + w // 2 + 14, y + h - 2], fill=(250, 200, 90))
        for (bx, bh) in ((x + 8, 14), (x + 34, 22), (x + 62, 16), (x + 104, 26), (x + 142, 18), (x + 168, 24)):
            d.rectangle([bx, y + h - bh, bx + 24, y + h], fill=(24, 22, 34))
        # smoke column from the hit building (kept inside the scene box)
        for (sx, sy, r) in ((x + 112, y + h - 32, 5), (x + 116, y + h - 40, 6), (x + 110, y + h - 46, 5)):
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(70, 66, 70))
    elif kind == "smoke":
        vgrad(d, (x, y, x + w, y + h), (120, 110, 100), (60, 56, 52))
        # ruined skyline behind the smoke
        for (bx, bh) in ((x + 6, 20), (x + 30, 28), (x + 150, 24), (x + 172, 16)):
            d.rectangle([bx, y + h - bh, bx + 20, y + h], fill=(52, 48, 46))
        for (sx, sy, r) in ((x + 40, y + 14, 12), (x + 70, y + 8, 15), (x + 105, y + 16, 11),
                            (x + 140, y + 10, 13)):
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(90, 86, 84))
        d.polygon([(x + 90, y + h), (x + 110, y + 18), (x + 130, y + h)], fill=(240, 140, 50))
        d.polygon([(x + 150, y + h), (x + 160, y + 30), (x + 170, y + h)], fill=(230, 110, 40))
        d.rectangle([x + 12, y + h - 12, x + w - 12, y + h], fill=(30, 28, 26))
        for (rx, ry) in ((x + 30, y + h - 4), (x + 60, y + h - 3), (x + 140, y + h - 4)):
            d.ellipse([rx, ry, rx + 3, ry + 3], fill=(120, 116, 110))
    elif kind == "derrick":
        d.ellipse([x + w - 30, y + 6, x + w - 10, y + 26], fill=(250, 200, 90))
        # second, smaller derrick at left
        d.line([(x + 18, y + h - 6), (x + 34, y + 16), (x + 50, y + h - 6)], fill=(30, 26, 22), width=3)
        d.line([(x + 26, y + h - 6), (x + 34, y + 24), (x + 42, y + h - 6)], fill=(30, 26, 22), width=2)
        d.line([(x + 40, y + h - 6), (x + 70, y + 6), (x + 100, y + h - 6)], fill=(30, 26, 22), width=4)
        d.line([(x + 52, y + h - 6), (x + 70, y + 20), (x + 88, y + h - 6)], fill=(30, 26, 22), width=3)
        d.rectangle([x + w - 48, y + h - 26, x + w - 22, y + h - 6], fill=(24, 22, 20))
        d.line([(x + w - 48, y + h - 19), (x + w - 22, y + h - 19)], fill=(120, 110, 100), width=2)
        d.line([(x + w - 48, y + h - 12), (x + w - 22, y + h - 12)], fill=(120, 110, 100), width=2)
        d.polygon([(x + w - 35, y + h - 26), (x + w - 30, y + h - 38), (x + w - 25, y + h - 26)], fill=(240, 140, 50))
        # pipeline + barrels along the ground
        d.line([(x + 6, y + h - 4), (x + w - 6, y + h - 4)], fill=(24, 22, 20), width=3)
        for bx in (x + 108, x + 122, x + 136):
            d.rectangle([bx, y + h - 16, bx + 10, y + h - 6], fill=(60, 52, 44))
            d.line([(bx, y + h - 11), (bx + 10, y + h - 11)], fill=(140, 130, 120), width=1)
    elif kind == "capitol":
        vgrad(d, (x, y, x + w, y + h), (140, 180, 220), (225, 225, 220))
        # side wings + trees
        d.rectangle([x + 6, y + 30, x + w // 2 - 36, y + h - 10], fill=(225, 225, 215))
        d.rectangle([x + w // 2 + 36, y + 30, x + w - 6, y + h - 10], fill=(225, 225, 215))
        for (tx, ty) in ((x + 14, y + h - 26), (x + w - 14, y + h - 26)):
            d.line([(tx, ty + 10), (tx, ty)], fill=(60, 90, 50), width=2)
            d.ellipse([tx - 6, ty - 8, tx + 6, ty + 4], fill=(50, 120, 60))
        d.ellipse([x + w // 2 - 30, y + 6, x + w // 2 + 30, y + 30], fill=(235, 235, 225))
        d.rectangle([x + w // 2 - 34, y + 26, x + w // 2 + 34, y + h - 10], fill=(235, 235, 225))
        for cx in range(x + w // 2 - 28, x + w // 2 + 29, 12):
            d.line([(cx, y + 30), (cx, y + h - 12)], fill=(160, 160, 150), width=2)
        d.rectangle([x + w // 2 - 2, y + 0, x + w // 2 + 2, y + 8], fill=(235, 235, 225))
        # small flag on the finial + steps
        d.polygon([(x + w // 2 + 2, y + 1), (x + w // 2 + 14, y + 4),
                   (x + w // 2 + 2, y + 7)], fill=(200, 50, 50))
        for sy in (y + h - 8, y + h - 5):
            d.line([(x + w // 2 - 40, sy), (x + w // 2 + 40, sy)], fill=(170, 170, 160), width=2)
    elif kind == "flask":
        # shelf with bottles at the back
        d.line([(x + 8, y + 12), (x + w - 8, y + 12)], fill=(200, 230, 235), width=2)
        for (bx, bw2, bh2, bc) in ((x + 16, 8, 10, (255, 200, 90)), (x + 34, 7, 12, (240, 120, 120)),
                                   (x + w - 44, 8, 11, (150, 220, 150)), (x + w - 26, 7, 12, (255, 200, 90))):
            d.rectangle([bx, y + 12 - bh2, bx + bw2, y + 12], fill=bc)
        d.polygon([(x + w // 2 - 8, y + 8), (x + w // 2 + 8, y + 8),
                   (x + w // 2 + 26, y + h - 10), (x + w // 2 - 26, y + h - 10)],
                  fill=(220, 240, 245))
        d.rectangle([x + w // 2 - 30, y + h - 22, x + w // 2 + 30, y + h - 10], fill=(40, 160, 120))
        for (px, py, r) in ((x + w // 2 - 8, y + 22, 4), (x + w // 2 + 6, y + 16, 3),
                            (x + w // 2, y + 30, 5)):
            d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255))
        # bench line + small second flask
        d.line([(x + 6, y + h - 8), (x + w - 6, y + h - 8)], fill=(200, 230, 235), width=2)
        d.polygon([(x + w - 46, y + 26), (x + w - 38, y + 26),
                   (x + w - 30, y + h - 10), (x + w - 54, y + h - 10)], fill=(200, 225, 230))
        d.rectangle([x + w - 50, y + h - 18, x + w - 34, y + h - 10], fill=(90, 190, 150))
    elif kind == "rocket":
        for (sx, sy) in ((x + 12, y + 40), (x + 44, y + 8), (x + 58, y + 16),
                         (x + w - 16, y + 8), (x + w - 34, y + 18), (x + w - 52, y + 32)):
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(230, 235, 250))
        # launch gantry left of the rocket
        d.rectangle([x + 26, y + 6, x + 34, y + h - 6], fill=(120, 125, 135))
        d.line([(x + 34, y + 14), (x + w // 2 - 12, y + 14)], fill=(120, 125, 135), width=3)
        d.line([(x + 34, y + 30), (x + w // 2 - 12, y + 30)], fill=(120, 125, 135), width=3)
        d.polygon([(x + w // 2, y + 4), (x + w // 2 + 12, y + 26),
                   (x + w // 2 + 12, y + h - 18), (x + w // 2 - 12, y + h - 18),
                   (x + w // 2 - 12, y + 26)], fill=(235, 235, 230))
        d.ellipse([x + w // 2 - 5, y + 12, x + w // 2 + 5, y + 24], fill=(60, 140, 200))
        d.polygon([(x + w // 2 - 12, y + h - 18), (x + w // 2 - 22, y + h - 6),
                   (x + w // 2 - 12, y + h - 8)], fill=(200, 60, 50))
        d.polygon([(x + w // 2 + 12, y + h - 18), (x + w // 2 + 22, y + h - 6),
                   (x + w // 2 + 12, y + h - 8)], fill=(200, 60, 50))
        d.polygon([(x + w // 2 - 5, y + h - 18), (x + w // 2 + 5, y + h - 18),
                   (x + w // 2, y + h - 2)], fill=(250, 180, 60))
        # exhaust plume + pad
        for (px, py, r) in ((x + w // 2 - 8, y + h - 10, 6), (x + w // 2 + 6, y + h - 8, 7),
                            (x + w // 2, y + h - 14, 5)):
            d.ellipse([px - r, py - r, px + r, py + r], fill=(220, 220, 215))
        d.rectangle([x + w // 2 - 34, y + h - 4, x + w // 2 + 34, y + h], fill=(90, 95, 105))
    elif kind == "jets":
        vgrad(d, (x, y, x + w, y + h), (60, 100, 160), (20, 40, 80))
        # radar arcs, bottom-right
        cx, cy = x + w - 34, y + h - 6
        for r in (26, 18, 10):
            d.arc([cx - r, cy - r, cx + r, cy + r], 180, 270, fill=(90, 200, 160), width=2)
        # two jets with contrails
        for (jx, jy, s) in ((x + 40, y + 18, 1.0), (x + 110, y + 34, 0.8)):
            d.line([(jx - 46 * s, jy + 10 * s), (jx - 6 * s, jy)], fill=(255, 255, 255), width=2)
            d.polygon([(jx, jy - 6 * s), (jx + 22 * s, jy), (jx, jy + 6 * s),
                       (jx - 12 * s, jy)], fill=(225, 225, 220))
            d.polygon([(jx - 4 * s, jy - 6 * s), (jx - 14 * s, jy - 14 * s),
                       (jx - 10 * s, jy - 2 * s)], fill=(200, 200, 195))
            d.polygon([(jx - 4 * s, jy + 6 * s), (jx - 14 * s, jy + 14 * s),
                       (jx - 10 * s, jy + 2 * s)], fill=(200, 200, 195))
        # cloud puffs
        for (px, py, r) in ((x + 20, y + h - 14, 6), (x + 150, y + h - 10, 5),
                            (x + 90, y + h - 18, 4)):
            d.ellipse([px - r, py - r, px + r, py + r], fill=(220, 225, 240))
    elif kind == "blast":
        vgrad(d, (x, y, x + w, y + h), (46, 32, 40), (18, 12, 18))
        # fireball + core
        cx, cy = x + w // 2, y + h // 2 - 4
        d.ellipse([cx - 34, cy - 26, cx + 34, cy + 26], fill=(240, 120, 40))
        d.ellipse([cx - 20, cy - 15, cx + 20, cy + 15], fill=(250, 200, 80))
        d.ellipse([cx - 9, cy - 7, cx + 9, cy + 7], fill=(255, 240, 180))
        # smoke + debris
        for (sx, sy, r) in ((cx - 30, cy - 28, 7), (cx + 28, cy - 30, 6),
                            (cx - 38, cy + 8, 5), (cx + 36, cy + 12, 5)):
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(70, 66, 70))
        for (dx, dy) in ((x + 18, y + 12), (x + w - 20, y + 16), (x + 30, y + h - 16)):
            d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(250, 190, 90))
        # ground line
        d.rectangle([x, y + h - 6, x + w, y + h], fill=(24, 20, 20))
    elif kind == "ticker":
        d.rectangle([x, y, x + w, y + h], fill=(14, 30, 22))
        # ticker rows, indented clear of the number badge (top-left)
        f = Fsans(11, bold=True)
        d.text((x + 30, y + 5), "DOW", font=f, fill=(255, 255, 255))
        d.text((x + w - 66, y + 5), "+0.33%", font=f, fill=(80, 220, 120))
        d.polygon([(x + w - 76, y + 15), (x + w - 70, y + 5), (x + w - 64, y + 15)],
                  fill=(80, 220, 120))
        f2 = Fsans(11, bold=True)
        d.text((x + 30, y + 22), "NASDAQ", font=f2, fill=(255, 255, 255))
        d.text((x + w - 66, y + 22), "-0.62%", font=f2, fill=(240, 90, 80))
        d.polygon([(x + w - 76, y + 25), (x + w - 64, y + 25), (x + w - 70, y + 35)],
                  fill=(240, 90, 80))
    # tag chip, bottom-left
    f = Fsans(10, bold=True)
    tw = f.getlength(tag) + 12
    d.rectangle([x + 4, y + h - 20, x + 4 + tw, y + h - 4], fill=(255, 255, 255))
    d.text((x + 10, y + h - 18), tag, font=f, fill=INK)


# ---------------------------------------------------------------- map
# Equirectangular land grid: (lon, lat) of rough land cells, 5-degree step.
LAND = set()
for _lon in range(-170, 181, 5):
    for _lat in range(-55, 86, 5):
        _lon2, _lat2 = _lon, _lat
        on = False
        # North America
        if -168 <= _lon2 <= -52 and 15 <= _lat2 <= 72 and not (5 <= _lat2 <= 15 and _lon2 > -85):
            on = True
        if -60 <= _lon2 <= -52 and 5 <= _lat2 <= 15:
            on = True
        # South America
        if -80 <= _lon2 <= -35 and -55 <= _lat2 <= 10:
            on = True
        # Europe
        if -10 <= _lon2 <= 40 and 36 <= _lat2 <= 70:
            on = True
        # Africa
        if -18 <= _lon2 <= 50 and -35 <= _lat2 <= 35:
            on = True
        # Asia
        if 40 <= _lon2 <= 180 and 5 <= _lat2 <= 75:
            on = True
        if 95 <= _lon2 <= 145 and -10 <= _lat2 <= 5:
            on = True
        # Oceania
        if 112 <= _lon2 <= 154 and -40 <= _lat2 <= -10:
            on = True
        if 166 <= _lon2 <= 179 and -47 <= _lat2 <= -34:
            on = True
        if on:
            LAND.add((_lon2, _lat2))

def map_xy(mx, my, mw, mh, lon, lat):
    fx = (lon + 180.0) / 360.0
    fy = (84.0 - lat) / 144.0
    return mx + fx * mw, my + fy * mh

def draw_map(d, mx, my, mw, mh):
    vgrad(d, (mx, my, mx + mw, my + mh), NAVY, TEALDEEP)
    # graticule
    for glon in range(-150, 181, 30):
        gx, _ = map_xy(mx, my, mw, mh, glon, 0)
        d.line([(gx, my), (gx, my + mh)], fill=(255, 255, 255, 40), width=1)
    for glat in (-30, 0, 30, 60):
        _, gy = map_xy(mx, my, mw, mh, 0, glat)
        d.line([(mx, gy), (mx + mw, gy)], fill=(255, 255, 255, 40), width=1)
    # land dots
    for (lon, lat) in LAND:
        px, py = map_xy(mx, my, mw, mh, lon, lat)
        d.ellipse([px - 2.4, py - 2.4, px + 2.4, py + 2.4], fill=GOLD)
    # pins: heroes 1-3 + cards 4-13
    pins = [(h["num"], h["pin"]) for h in HEROES] + [(c["num"], c["pin"]) for c in CARDS]
    # fan-out offsets for the crowded Europe / Near-East cluster (dx, dy px)
    fan = {1: (18, 22), 3: (26, -26), 4: (-30, 18), 8: (22, -18), 9: (-30, 18),
           10: (30, -14), 12: (34, 20), 13: (-24, -18)}
    for n, (lon, lat) in pins:
        px, py = map_xy(mx, my, mw, mh, lon, lat)
        dx, dy = fan.get(n, (0, 0))
        bx, by = px + dx, py + dy
        if (dx, dy) != (0, 0):
            d.line([(px, py), (bx, by)], fill=(20, 20, 20), width=4)
            d.line([(px, py), (bx, by)], fill=(255, 255, 255), width=2)
            d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=(255, 255, 255))
        r = 8
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=PINRED, outline=(255, 255, 255), width=2)
        f = Fsans(8, bold=True)
        t = str(n)
        d.text((bx - f.getlength(t) / 2, by - 5), t, font=f, fill=(255, 255, 255))

# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # top rule
    d.rectangle([0, 0, W, 5], fill=INK)

    # --- header line
    y = 12
    text_w(d, 8, y, "ONE DAY OF WORLD NEWS", Fsans(12, bold=True), fill=RED)
    hdr = "38 STORIES \u00b7 7 REGIONS \u00b7 20 FIELDS \u00b7 EVERY ONE FROM WEDNESDAY 25 NOVEMBER 2026"
    text_w(d, W - 8, y, hdr, Fsans(11, bold=True), anchor="ra")

    # --- masthead
    y = 30
    sz = fit_size("Wednesday 25 November 2026", lambda s: Fserif(s, bold=True), W - 16, 62, 40)
    f = Fserif(sz, bold=True)
    text_w(d, W // 2, y, "Wednesday 25 November 2026", f, anchor="ma")
    # --- dek
    y = 30 + sz + 8
    dek = ("US proposes tariffs on 14 partners \u00b7 "
           "Shenzhou-24 launches with first foreign astronaut \u00b7 "
           "Judges urge Netanyahu bribery case dropped")
    dsz = fit_size(dek, lambda s: Fserif_it(s), W - 40, 17, 12)
    text_w(d, W // 2, y, dek, Fserif_it(dsz), fill=RED, anchor="ma")

    # --- region tabs
    y = 128
    counts = {}
    for h in HEROES:
        counts[h["region"]] = counts.get(h["region"], 0) + 1
    for c in CARDS:
        counts[c["region"]] = counts.get(c["region"], 0) + 1
    for i, (region, _, _, _) in enumerate(BRIEFS):
        counts[region] = counts.get(region, 0) + 1
    total = sum(counts.values())
    fields = set()
    for h in HEROES:
        fields.add(h["field"])
    for c in CARDS:
        fields.add(c["field"])
    for (_, f2, _, _) in BRIEFS:
        fields.add(f2)
    assert total == 38, "story total %d != 38" % total
    assert len(REGIONS) == 7
    assert len(fields) == 20, "fields %d != 20: %s" % (len(fields), sorted(fields))
    tab_w = W // 7
    for i, (name, col) in enumerate(REGIONS):
        x0 = i * tab_w
        d.rectangle([x0 + 2, y, x0 + tab_w - 2, y + 22], fill=col)
        f = Fsans(10, bold=True)
        t = "%s %d" % (name, counts.get(name, 0))
        text_w(d, x0 + tab_w // 2, y + 5, t, f, fill=(255, 255, 255), anchor="ma")

    # --- numbers strip
    y = 156
    d.rectangle([8, y, 8 + 92, y + 62], fill=INK)
    f = Fsans(10, bold=True)
    text_w(d, 54, y + 12, "THE DAY", f, fill=(255, 255, 255), anchor="ma")
    text_w(d, 54, y + 26, "IN NUMBERS", f, fill=(255, 255, 255), anchor="ma")
    text_w(d, 54, y + 42, "WEDNESDAY", Fsans(8), fill=(200, 200, 200), anchor="ma")
    cw = (W - 16 - 100) // 6
    for i, (place, fig, label) in enumerate(NUMBERS):
        x0 = 108 + i * cw
        if i:
            d.line([(x0 - 4, y + 4), (x0 - 4, y + 58)], fill=LINE, width=1)
        text_w(d, x0, y + 2, place, Fsans(8, bold=True), fill=GREY)
        fsz = fit_size(fig, lambda s: Fserif(s, bold=True), cw - 8, 28, 16)
        text_w(d, x0, y + 14, fig, Fserif(fsz, bold=True), fill=RED)
        draw_wrapped(d, x0, y + 44, label, Fsans(9), cw - 8, 11, max_lines=2)

    # --- heroes
    y = 226
    hw = (W - 16 - 16) // 3
    for i, h in enumerate(HEROES):
        x0 = 8 + i * (hw + 8)
        sc = {"tariff": scene_tariff, "launch": scene_launch,
              "court": scene_court_netanyahu}[h["scene"]]
        sc(d, x0, y, hw, 118)
        num_badge(d, x0 + 14, y + 14, h["num"], r=12)
        # place tag + pill
        yy = y + 124
        text_w(d, x0, yy, h["place"], Fsans(10, bold=True), fill=RED)
        pill(d, x0 + hw - 62, yy - 1, h["pill"])
        # headline
        yy += 16
        draw_wrapped(d, x0, yy, h["head"], Fserif(19, bold=True), hw, 21, max_lines=2)
        yy += 44
        draw_wrapped(d, x0, yy, h["summ"], Fsans(11), hw, 14, max_lines=3)
    y = 226 + 124 + 16 + 44 + 42

    # --- cards, 2 rows x 5
    cw2 = (W - 16 - 4 * 8) // 5
    ch = 114
    for row in range(2):
        for col in range(5):
            c = CARDS[row * 5 + col]
            x0 = 8 + col * (cw2 + 8)
            y0 = y + row * (ch + 8)
            card_scene(d, x0, y0, cw2, 52, c["scene"], c["tag"], c["bg"])
            num_badge(d, x0 + 13, y0 + 13, c["num"], r=10)
            yy = y0 + 56
            text_w(d, x0, yy, c["place"], Fsans(9, bold=True), fill=RED)
            pill(d, x0 + cw2 - 62, yy - 1, c["pill"])
            yy += 13
            draw_wrapped(d, x0, yy, c["head"], Fserif(13, bold=True), cw2, 15, max_lines=2)
            yy += 30
            draw_wrapped(d, x0, yy, c["summ"], Fsans(10), cw2, 12, max_lines=2)
    y = y + 2 * (ch + 8)

    # --- briefs header
    d.line([(8, y + 4), (W - 8, y + 4)], fill=INK, width=2)
    text_w(d, 8, y + 10, "ALSO ON WEDNESDAY 25 NOVEMBER \u2014 25 MORE, BY REGION",
           Fsans(11, bold=True))
    text_w(d, W - 8, y + 10, "Sources in brackets \u00b7 * = one side's claim",
           Fsans(9), fill=GREY, anchor="ra")
    y = y + 30

    # --- briefs (2 cols) + map
    by = y
    bw = 322
    for col in range(2):
        items = BRIEFS[col * 13:(col + 1) * 13] if col == 0 else BRIEFS[13:25]
        x0 = 8 + col * (bw + 8)
        for j, (region, _, txt, src) in enumerate(items):
            n = 14 + col * 13 + j
            yy = by + j * 19
            f = Fsans(10, bold=True)
            d.text((x0, yy), str(n), font=f, fill=INK)
            d.ellipse([x0 + 19, yy + 2, x0 + 29, yy + 12], fill=RHEX[region])
            line = "%s (%s)" % (txt, src)
            words = line.split(" ")
            lead = " ".join(words[:3])
            rest = " " + " ".join(words[3:])
            # fit: bold lead + regular rest, base 11px (was 10), floor 9px
            sz = 11
            while sz > 9 and (Fsans(sz, bold=True).getlength(lead)
                              + Fsans(sz).getlength(rest)) > bw - 34:
                sz -= 1
            fb = Fsans(sz, bold=True)
            f2 = Fsans(sz)
            if fb.getlength(lead) + f2.getlength(rest) > bw - 34:
                OVERFLOWS.append("brief %d too long even at 9px" % n)
            d.text((x0 + 32, yy), lead, font=fb, fill=INK)
            d.text((x0 + 32 + fb.getlength(lead), yy), rest, font=f2, fill=INK)
    # map
    mx, my, mw, mh = 668, by - 4, W - 8 - 668, 244
    text_w(d, mx, my, "WHERE IT HAPPENED \u00b7 PINS 1\u201313", Fsans(11, bold=True))
    draw_map(d, mx, my + 20, mw, mh - 62)
    # map legend
    ly = my + mh - 38
    lx = mx
    for name, col in REGIONS:
        d.ellipse([lx, ly, lx + 8, ly + 8], fill=col)
        t = "%s %d" % (name, counts.get(name, 0))
        f = Fsans(8)
        d.text((lx + 11, ly - 1), t, font=f, fill=INK)
        lx += int(f.getlength(t)) + 26
        if lx > mx + mw - 90:
            lx = mx
            ly += 13
    y = by + 248

    # --- DATE CHECK
    d.rectangle([8, y, W - 8, y + 26], fill=RED)
    f = Fsans(10, bold=True)
    t = DATECHECK
    if len(wrap(t, f, W - 28)) > 2:
        OVERFLOWS.append("DATE CHECK needs >2 lines")
    draw_wrapped(d, 14, y + 3, t, f, W - 28, 12, fill=(255, 255, 255), max_lines=2)

    # --- footer
    y = y + 28
    text_w(d, W // 2, y, FOOTER, Fsans(8), fill=GREY, anchor="ma")

    if OVERFLOWS:
        print("OVERFLOWS (%d):" % len(OVERFLOWS))
        for o in OVERFLOWS:
            print("  -", o)
    else:
        print("no overflows")
    print("counts:", {k: counts[k] for k, _ in REGIONS}, "total", total, "fields", len(fields))
    img.save(OUT, optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")

if __name__ == "__main__":
    build()
