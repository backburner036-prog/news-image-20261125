#!/usr/bin/env python3
"""THE WORLD TODAY — 25 November 2026, rendered to entry.png.

A one-page newspaper front page built with Pillow: one hero story, three
leads with small drawn pictures, a strip of five big numbers, a UTC
timeline, thirty-one one-line briefs, a regions line and a sources footer.
Every story in it happened or was first reported on Wednesday 25 November
2026 (see news-image-20261125-research.md for the date-checked list).

Layout is a fixed 1024x1024 grid. Nothing here touches the network, the
clock or any random source, so repeated runs write identical bytes.
Only Pillow plus the standard library.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 28
RIGHT = 996
COL_W = 312
GAP = 16

# palette, as a table so each swatch is named once
C = {
    "ink": (0x11, 0x11, 0x11),
    "grey": (0x55, 0x55, 0x55),
    "red": (0xC0, 0x39, 0x2B),
    "panel": (0xF5, 0xF5, 0xF5),
    "paper": (0xFF, 0xFF, 0xFF),
    "gold": (0xFF, 0xD6, 0x17),
    "dark": (0x1A, 0x1A, 0x22),
    "grid": (0x5C, 0x1E, 0x1E),
    "red_top": (0x2A, 0x0F, 0x0F),
    "red_mid": (0x53, 0x14, 0x14),
    "red_bot": (0x7A, 0x1F, 0x1F),
    "red_line": (0xFF, 0x6B, 0x5E),
    "shadow": (0x1A, 0x07, 0x07),
    "dim": (0xBB, 0xBB, 0xBB),
    "rubble": (0x3A, 0x3A, 0x44),
}

BASE = "/usr/share/fonts/truetype/liberation/"
SERIF = BASE + "LiberationSerif-Bold.ttf"
SANS = BASE + "LiberationSans-Regular.ttf"
SANSB = BASE + "LiberationSans-Bold.ttf"

_cache = {}


def fnt(path, size):
    """Load (and memoise) a TrueType font at a size."""
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def mix(a, b, t):
    """Blend two RGB triples."""
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def wrap(f, text, width):
    """Greedy word wrap into lines no wider than width."""
    out, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip() if line else word
        if f.getlength(trial) <= width:
            line = trial
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


# ------------------------------------------------------------------ content
HERO_KICKER = "TOP STORY  —  ASIA MARKETS"
HERO_HEAD = "Asia tumbles as AI rally reverses"
HERO_SUB = "Kospi down 5.3% as Nikkei falls 2.9%  —  Reuters"
HEADER_DATE = "Wednesday, 25 November 2026"
FOOTER_DATE = "WEDNESDAY, 25 NOVEMBER 2026"
HEADER_INFO = "35 STORIES  ·  7 REGIONS  ·  UTC TIMELINE"

STRIP = [
    ("-5.3%", "KOSPI TUMBLES (#1)"),
    ("-14%", "SOFTBANK SLUMPS (#5)"),
    ("4.9%", "AUSTRALIA CPI (#14)"),
    ("$4.71B", "BITCOIN ETF OUTFLOWS (#10)"),
    ("500,000", "RUSSIAN WAR DEAD (#16)"),
]

# each lead: number, headline, one-liner, source, thumbnail kind
LEADS = [
    (2, "US set to unveil new tariffs on China, EU",
     "New duties loom for China, EU.", "AP", "ship"),
    (3, "CIA, ODNI suffer cyber breach, CNN reports",
     "Breach hits US spy agencies.", "CNN", "breach"),
    (4, "China rocket carries Pakistani astronaut",
     "Pakistan astronaut lifts off.", "BBC", "rocket"),
]

TIMELINE = [
    ("00:30 UTC", "AUSTRALIA CPI HITS 4.9%"),
    ("01:03 UTC", "TRUMP: NVIDIA STAKE POSSIBLE"),
    ("01:48 UTC", "SOFTBANK DROPS 14%"),
    ("01:52 UTC", "US READY TO SLAP TARIFFS"),
    ("02:09 UTC", "AG DODGES NVIDIA QUESTIONS"),
]

BRIEFS = [
    (5, "SoftBank slumps 14% in Tokyo"),
    (6, "Nvidia falls 5.9% after Huang return"),
    (7, "Anthropic sinks below IPO price"),
    (8, "Trump floats US stake in Nvidia"),
    (9, "Attorney general dodges Nvidia probe"),
    (10, "Bitcoin slips below $60,000"),
    (11, "CleanSpark posts $987m yearly loss"),
    (12, "Brent crude slides below $90"),
    (13, "Japan services prices jump 4.2%"),
    (14, "Australia CPI hits 4.9% in October"),
    (15, "China AI fakes smear Taiwan hopefuls"),
    (16, "Russia counts 500,000 war dead"),
    (17, "Ukraine shares Libya strike video"),
    (18, "NATO chief vows space defence"),
    (19, "Russian governor detained in rare case"),
    (20, "UK braces for energy price cap rise"),
    (21, "Sinner has minor surgery on knee"),
    (22, "India food prices squeeze households"),
    (23, "North Koreans jailed as Christians"),
    (24, "India women thrash China 6-2"),
    (25, "Czechia reach Davis Cup semifinals"),
    (26, "Paris Basketball beat Besiktas 88-76"),
    (27, "Spix's macaw chick born in Brazil zoo"),
    (28, "WHO evacuates Congo Ebola staff"),
    (29, "DR Congo military plane missing"),
    (30, "Nigerian monarch suspended at 92"),
    (31, "Zimbabwean jailed over Ukraine war"),
    (32, "Landmine casualties soar in Syria"),
    (33, "Houthis threaten Saudi ports"),
    (34, "Sydney policeman guilty of murder"),
    (35, "Pope diary claims he saw devil"),
]

REGIONS = ("REGIONS: NORTH AMERICA · LATIN AMERICA · EUROPE "
           "· MIDDLE EAST · ASIA · AFRICA · OCEANIA")
SOURCES = ("Sources: Reuters / AP / BBC / CNN / Guardian / Business Insider / "
           "Korea Times / Stockbiz / Apex Sports / Inquirer")


def columns():
    """Split the briefs into the three printed columns."""
    return ([b for b in BRIEFS if 5 <= b[0] <= 15],
            [b for b in BRIEFS if 16 <= b[0] <= 25],
            [b for b in BRIEFS if 26 <= b[0] <= 35])


# ------------------------------------------------------------------ drawing
def masthead(d, log):
    """A: nameplate, date, info line, double rule."""
    d.rectangle((0, 0, W, 6), fill=C["red"])
    d.text((MARGIN, 12), "THE WORLD TODAY",
           font=fnt(SERIF, 64), fill=C["ink"])
    d.text((MARGIN, 78), HEADER_DATE, font=fnt(SANSB, 22), fill=C["red"])
    info = fnt(SANS, 13)
    d.text((RIGHT - info.getlength(HEADER_INFO), 82), HEADER_INFO,
           font=info, fill=C["grey"])
    d.rectangle((MARGIN, 102, RIGHT, 105), fill=C["ink"])
    d.rectangle((MARGIN, 107, RIGHT, 108), fill=C["ink"])
    log.append("masthead date %.0fpx wide"
               % fnt(SANSB, 22).getlength(HEADER_DATE))


def hero_panel(d, log):
    """B: red market panel, 104..248, with a falling chart line."""
    y0, y1 = 104, 248
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / (y1 - y0)
        if t < 0.5:
            shade = mix(C["red_top"], C["red_mid"], t * 2)
        else:
            shade = mix(C["red_mid"], C["red_bot"], (t - 0.5) * 2)
        d.line([(MARGIN, yy), (RIGHT, yy)], fill=shade)
    for gx in range(MARGIN + 60, RIGHT, 80):
        d.line([(gx, y0), (gx, y1)], fill=C["grid"])
    for gy in (y0 + 36, y0 + 72, y0 + 108):
        d.line([(MARGIN, gy), (RIGHT, gy)], fill=C["grid"])
    # falling line: high start, small bounce, steep drop to the right.
    # Stays above y=196 left of x=410, so it never meets the TUMBLE label.
    pts = [(60, 112), (170, 124), (290, 118), (410, 130), (520, 148),
           (640, 162), (760, 178), (870, 188), (960, 196)]
    d.line(pts, fill=C["red_line"], width=5, joint="curve")
    d.ellipse((54, 106, 66, 118), fill=C["paper"])
    d.ellipse((954, 190, 966, 202), fill=C["red_line"])
    d.polygon([(968, 196), (940, 192), (956, 210)], fill=C["red_line"])
    big = fnt(SANSB, 30)
    d.text((48, 196), "TUMBLE", font=big, fill=C["paper"],
           stroke_width=1, stroke_fill=C["shadow"])
    d.text((48, 228), "— ASIA MARKETS", font=fnt(SANSB, 14),
           fill=C["paper"], stroke_width=1, stroke_fill=C["shadow"])
    log.append("hero headline %.0f/968px"
               % fnt(SERIF, 36).getlength(HERO_HEAD))


def hero_text(d, log):
    """C: kicker, headline, sub-line, 252..340."""
    d.text((MARGIN, 252), HERO_KICKER, font=fnt(SANSB, 13), fill=C["red"])
    d.text((MARGIN, 270), HERO_HEAD, font=fnt(SERIF, 36), fill=C["ink"])
    d.text((MARGIN, 312), HERO_SUB, font=fnt(SANS, 17), fill=C["ink"])
    log.append("hero sub %.0f/968px" % fnt(SANS, 17).getlength(HERO_SUB))


def strip(d, log):
    """D: five number boxes, 344..392."""
    num_f, lab_f = fnt(SANSB, 20), fnt(SANS, 9)
    for i, (num, lab) in enumerate(STRIP):
        bx = MARGIN + i * (184 + 12)
        d.rectangle((bx, 344, bx + 184, 392), fill=C["panel"])
        d.text((bx + 10, 350), num, font=num_f, fill=C["red"])
        d.text((bx + 10, 376), lab, font=lab_f, fill=C["grey"])
        log.append("strip %d: %s label %.1f/164px"
                   % (i + 1, num, lab_f.getlength(lab)))


def thumb_ship(d, x, y0, y1):
    """Container ship thumbnail for the tariffs lead."""
    d.rectangle((x, y0, x + COL_W, y1), fill=C["dark"])
    d.rectangle((x + 12, y0 + 10, x + 44, y1 - 18), fill=C["red"])
    d.rectangle((x + 48, y0 + 10, x + 80, y1 - 18), fill=C["gold"])
    d.rectangle((x + 84, y0 + 10, x + 116, y1 - 18), fill=(0x2E, 0x7A, 0x4A))
    d.rectangle((x + 28, y0 + 30, x + 60, y1 - 18), fill=(0x2E, 0x5A, 0x8A))
    # hull: slanted bow, flat stern, white wake line below
    d.polygon([(x + 8, y1 - 18), (x + 296, y1 - 18),
               (x + 308, y1 - 6), (x + 22, y1 - 6)], fill=C["rubble"])
    d.line([(x + 8, y1 - 2), (x + 304, y1 - 2)], fill=C["paper"], width=1)
    d.text((x + 150, y0 + 6), "%", font=fnt(SANSB, 34), fill=C["paper"])
    d.text((x + 196, y0 + 30), "TARIFFS", font=fnt(SANSB, 13), fill=C["dim"])


def thumb_breach(d, x, y0, y1):
    """CIA breach thumbnail: big letters plus a warning triangle."""
    d.rectangle((x, y0, x + COL_W, y1), fill=C["dark"])
    d.text((x + 12, y0 + 8), "CIA", font=fnt(SANSB, 36), fill=C["paper"])
    d.polygon([(x + 210, y0 + 44), (x + 232, y0 + 8), (x + 254, y0 + 44)],
              outline=C["red"], width=3)
    d.text((x + 226, y0 + 16), "!", font=fnt(SANSB, 20), fill=C["red"])
    d.text((x + 96, y0 + 34), "BREACH", font=fnt(SANSB, 13), fill=C["dim"])


def thumb_rocket(d, x, y0, y1):
    """Rocket thumbnail for the astronaut lead."""
    d.rectangle((x, y0, x + COL_W, y1), fill=C["dark"])
    for sx, sy in [(20, 10), (280, 12), (250, 40), (60, 44), (150, 8)]:
        d.ellipse((x + sx, y0 + sy, x + sx + 3, y0 + sy + 3), fill=C["paper"])
    d.rectangle((x + 130, y0 + 14, x + 146, y0 + 40), fill=C["paper"])
    d.polygon([(x + 130, y0 + 14), (x + 146, y0 + 14), (x + 138, y0 + 2)],
              fill=C["red"])
    d.polygon([(x + 130, y0 + 40), (x + 146, y0 + 40), (x + 138, y0 + 52)],
              fill=C["gold"])
    d.text((x + 168, y0 + 10), "LIFT-OFF", font=fnt(SANSB, 16), fill=C["paper"])
    d.text((x + 168, y0 + 34), "PAKISTAN ASTRONAUT",
           font=fnt(SANSB, 10), fill=C["dim"])


THUMBS = {"ship": thumb_ship, "breach": thumb_breach, "rocket": thumb_rocket}


def leads(d, log):
    """E: three lead stories, 396..520."""
    head_f, sent_f, num_f = fnt(SERIF, 18), fnt(SANS, 13), fnt(SANSB, 15)
    for lx, (num, title, sentence, source, kind) in zip(
            [MARGIN, 356, 684], LEADS):
        THUMBS[kind](d, lx, 396, 452)
        tag = "%d." % num
        tag_w = num_f.getlength(tag)
        d.text((lx, 458), tag, font=num_f, fill=C["red"])
        lines = wrap(head_f, title, COL_W - tag_w - 6)
        y = 458
        for line in lines[:2]:
            d.text((lx + tag_w + 6, y), line, font=head_f, fill=C["ink"])
            y += 22
        one = "%s — %s" % (sentence, source)
        wide = sent_f.getlength(one)
        log.append("lead %d: sentence %.1f/312px, %d headline lines"
                   % (num, wide, len(lines)))
        if wide > COL_W:
            log.append("OVERFLOW lead %d sentence" % num)
        d.text((lx, 500), one, font=sent_f, fill=C["ink"])


def timeline(d, log):
    """F: UTC timeline, 524..576."""
    d.line([(MARGIN, 548), (RIGHT, 548)], fill=C["ink"], width=2)
    time_f, lab_f = fnt(SANSB, 11), fnt(SANS, 10)
    for (stamp, label), cx in zip(TIMELINE, [124, 318, 512, 705, 899]):
        d.ellipse((cx - 5, 543, cx + 5, 553), fill=C["red"])
        tw = time_f.getlength(stamp)
        d.text((cx - tw / 2, 526), stamp, font=time_f, fill=C["red"])
        lw = lab_f.getlength(label)
        d.text((cx - lw / 2, 556), label, font=lab_f, fill=C["ink"])
        log.append("timeline %s: label %.1fpx at cx %d" % (stamp, lw, cx))


def briefs(d, log):
    """G: thirty-one briefs in three columns, 580..960."""
    brief_f = fnt(SANSB, 14)
    ends = []
    for cx, col in zip([MARGIN, 356, 684], columns()):
        y = 580
        for num, title in col:
            item = "%d. %s" % (num, title)
            wide = brief_f.getlength(item)
            if wide > COL_W:
                log.append("OVERFLOW brief %d: %.1f/312 :: %s"
                           % (num, wide, item))
            d.text((cx, y), item, font=brief_f, fill=C["ink"])
            y += 24
        ends.append(y - 7)
    log.append("brief column ends %s (limit <=940)" % (ends,))


def footer(d, log):
    """Regions line + sources footer, 946..1000."""
    reg_f = fnt(SANS, 10)
    d.text((MARGIN, 946), REGIONS, font=reg_f, fill=C["grey"])
    log.append("regions line %.1f/968px" % reg_f.getlength(REGIONS))
    d.rectangle((MARGIN, 964, RIGHT, 966), fill=C["ink"])
    src_f = fnt(SANS, 10)
    d.text((MARGIN, 972), SOURCES, font=src_f, fill=C["grey"])
    date_f = fnt(SANSB, 11)
    dx = RIGHT - date_f.getlength(FOOTER_DATE)
    d.text((dx, 972), FOOTER_DATE, font=date_f, fill=C["ink"])
    log.append("sources %.1fpx, footer date starts at %.0f"
               % (src_f.getlength(SOURCES), dx))


def build():
    """Draw the whole page and save entry.png; print the diagnostics."""
    img = Image.new("RGB", (W, H), C["paper"])
    d = ImageDraw.Draw(img)
    log = []
    masthead(d, log)
    hero_panel(d, log)
    hero_text(d, log)
    strip(d, log)
    leads(d, log)
    timeline(d, log)
    briefs(d, log)
    footer(d, log)
    img.save("entry.png", optimize=True)
    print("\n".join(log))


if __name__ == "__main__":
    build()
