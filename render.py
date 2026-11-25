#!/usr/bin/env python3
"""Render entry.png for news-image-20261125 — 'THE WORLD TODAY'.

Clean-room build, written fresh in this session (25 Nov 2026) from the frozen
v5 template geometry (1024x1024, fixed vertical budget, Liberation fonts,
GATE-D) with fresh 25 November 2026 content (see
news-image-20261125-research.md): hero is Wednesday's Asia markets tumble as
the AI rally reverses (Kospi -5.3%, Nikkei -2.9% intraday, Reuters), 35
stories (1 hero + 3 leads + 31 briefs), 7 regions, UTC timeline, no map.
Standard library + Pillow only. No network. Deterministic: no timestamps,
no randomness, fixed fonts, fixed layout.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
INK = (0x11, 0x11, 0x11)
GREY = (0x55, 0x55, 0x55)
LIGHT = (0xCC, 0xCC, 0xCC)
RED = (0xC0, 0x39, 0x2B)
PANEL = (0xF5, 0xF5, 0xF5)
WHITE = (0xFF, 0xFF, 0xFF)
GOLD = (0xFF, 0xD6, 0x17)
DARK = (0x1A, 0x1A, 0x22)
RED_BG_TOP = (0x2A, 0x0F, 0x0F)
RED_BG_MID = (0x53, 0x14, 0x14)
RED_BG_BOT = (0x7A, 0x1F, 0x1F)
RED_LINE = (0xFF, 0x6B, 0x5E)
STEEL = (0x8A, 0x95, 0xA5)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(fnt, text, max_width):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], []
    for w in words:
        trial = cur + [w]
        if fnt.getlength(" ".join(trial)) <= max_width or not cur:
            cur = trial
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ------------------------------------------------------------------ data
HERO = {
    "kicker": "TOP STORY  —  ASIA MARKETS",
    "headline": "Asia tumbles as AI rally reverses",
    "sub": "Kospi down 5.3% as Nikkei falls 2.9%",
    "source": "Reuters",
}

STRIP = [
    ("-5.3%", "KOSPI TUMBLES (#1)"),
    ("-14%", "SOFTBANK SLUMPS (#5)"),
    ("4.9%", "AUSTRALIA CPI (#14)"),
    ("$4.71B", "BITCOIN ETF OUTFLOWS (#10)"),
    ("500,000", "RUSSIAN WAR DEAD (#16)"),
]

LEADS = [
    {
        "num": 2,
        "title": "US set to unveil new tariffs on China, EU",
        "sentence": "New duties loom for China, EU.",
        "source": "AP",
        "art": "ship",
    },
    {
        "num": 3,
        "title": "CIA, ODNI suffer cyber breach, CNN reports",
        "sentence": "Breach hits US spy agencies.",
        "source": "CNN",
        "art": "breach",
    },
    {
        "num": 4,
        "title": "China rocket carries Pakistani astronaut",
        "sentence": "Pakistan astronaut lifts off.",
        "source": "BBC",
        "art": "rocket",
    },
]

TIMELINE = [
    ("00:30 UTC", "AUSTRALIA CPI HITS 4.9%"),
    ("01:03 UTC", "TRUMP: NVIDIA STAKE POSSIBLE"),
    ("01:48 UTC", "SOFTBANK DROPS 14%"),
    ("01:52 UTC", "US READY TO SLAP TARIFFS"),
    ("02:09 UTC", "AG DODGES NVIDIA QUESTIONS"),
]

# briefs: (number, title) — titles must fit 1 line at 14px bold in 312px
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

COLS = [
    [b for b in BRIEFS if 5 <= b[0] <= 15],
    [b for b in BRIEFS if 16 <= b[0] <= 25],
    [b for b in BRIEFS if 26 <= b[0] <= 35],
]

REGIONS_LINE = ("REGIONS: NORTH AMERICA \u00b7 LATIN AMERICA \u00b7 EUROPE "
                "\u00b7 MIDDLE EAST \u00b7 ASIA \u00b7 AFRICA \u00b7 OCEANIA")
SOURCES_LINE = ("Sources: Reuters / AP / BBC / CNN / Guardian / Business Insider / "
                "Korea Times / Stockbiz / Apex Sports / Inquirer")


# ------------------------------------------------------------------ draw
def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    diag = []

    f_mast = font(SERIF_BOLD, 64)
    f_date = font(SANS_BOLD, 22)
    f_info = font(SANS, 13)
    f_kick = font(SANS_BOLD, 13)
    f_hero = font(SERIF_BOLD, 36)
    f_sub = font(SANS, 17)
    f_num = font(SANS_BOLD, 20)
    f_lab = font(SANS, 9)
    f_lead = font(SERIF_BOLD, 18)
    f_sent = font(SANS, 13)
    f_num2 = font(SANS_BOLD, 15)
    f_time = font(SANS_BOLD, 11)
    f_tlab = font(SANS, 10)
    f_brief = font(SANS_BOLD, 14)
    f_reg = font(SANS, 10)
    f_src = font(SANS, 10)
    f_fdate = font(SANS_BOLD, 11)

    # ---- A. Header (0..100)
    d.rectangle([0, 0, 1024, 6], fill=RED)
    d.text((28, 12), "THE WORLD TODAY", font=f_mast, fill=INK)
    d.text((28, 78), "Wednesday, 25 November 2026", font=f_date, fill=RED)
    info = "35 STORIES  \u00b7  7 REGIONS  \u00b7  UTC TIMELINE"
    d.text((996 - f_info.getlength(info), 82), info, font=f_info, fill=GREY)
    d.rectangle([28, 102, 996, 105], fill=INK)
    d.rectangle([28, 107, 996, 108], fill=INK)
    diag.append(f"header date width {f_date.getlength('Wednesday, 25 November 2026'):.0f}")

    # ---- B. Hero panel (104..248): red market gradient + falling chart
    x0, y0, x1, y1 = 28, 104, 996, 248
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / (y1 - y0)
        if t < 0.5:
            col = lerp(RED_BG_TOP, RED_BG_MID, t * 2)
        else:
            col = lerp(RED_BG_MID, RED_BG_BOT, (t - 0.5) * 2)
        d.line([(x0, yy), (x1, yy)], fill=col)
    # faint grid
    for gx in range(x0 + 60, x1, 80):
        d.line([(gx, y0), (gx, y1)], fill=(0x5C, 0x1E, 0x1E), width=1)
    for gy in (y0 + 36, y0 + 72, y0 + 108):
        d.line([(x0, gy), (x1, gy)], fill=(0x5C, 0x1E, 0x1E), width=1)
    # falling chart line: high start, shallow bounce mid-panel, steep drop.
    # Kept above y=196 on the left so it never crosses the TUMBLE text.
    pts = [(60, 112), (170, 124), (290, 118), (410, 130), (520, 148),
           (640, 162), (760, 178), (870, 188), (960, 196)]
    d.line(pts, fill=RED_LINE, width=5, joint="curve")
    # start + end dots
    d.ellipse([54, 106, 66, 118], fill=WHITE)
    d.ellipse([954, 190, 966, 202], fill=RED_LINE)
    # arrow head at the drop end (pointing down-right)
    d.polygon([(968, 196), (940, 192), (956, 210)], fill=RED_LINE)
    # panel text
    d.text((48, 196), "TUMBLE", font=font(SANS_BOLD, 30), fill=WHITE,
           stroke_width=1, stroke_fill=(0x1A, 0x07, 0x07))
    d.text((48, 228), "\u2014 ASIA MARKETS", font=font(SANS_BOLD, 14), fill=WHITE,
           stroke_width=1, stroke_fill=(0x1A, 0x07, 0x07))
    diag.append(f"hero headline width {f_hero.getlength(HERO['headline']):.0f}/968")

    # ---- C. Headline hero (252..340)
    d.text((28, 252), HERO["kicker"], font=f_kick, fill=RED)
    d.text((28, 270), HERO["headline"], font=f_hero, fill=INK)
    sub = HERO["sub"] + " \u2014 " + HERO["source"]
    d.text((28, 312), sub, font=f_sub, fill=INK)
    diag.append(f"hero sub width {f_sub.getlength(sub):.0f}/968")

    # ---- D. Number strip (344..392): 5 boxes 184x48, gap 12
    for i, (num, lab) in enumerate(STRIP):
        bx = 28 + i * (184 + 12)
        d.rectangle([bx, 344, bx + 184, 392], fill=PANEL)
        d.text((bx + 10, 350), num, font=f_num, fill=RED)
        lw = f_lab.getlength(lab)
        d.text((bx + 10, 376), lab, font=f_lab, fill=GREY)
        diag.append(f"strip {i+1} label {lw:.1f}/164 num {num}")

    # ---- E. Leads (396..520): 3 cols @312, gap 16
    lead_xs = [28, 356, 684]
    for lx, lead in zip(lead_xs, LEADS):
        # thumb 312x56
        ty0, ty1 = 396, 452
        if lead["art"] == "ship":
            d.rectangle([lx, ty0, lx + 312, ty1], fill=DARK)
            # container ship: stacked containers + hull
            d.rectangle([lx + 12, ty0 + 10, lx + 44, ty1 - 18], fill=(0xC0, 0x39, 0x2B))
            d.rectangle([lx + 48, ty0 + 10, lx + 80, ty1 - 18], fill=GOLD)
            d.rectangle([lx + 84, ty0 + 10, lx + 116, ty1 - 18], fill=(0x2E, 0x7A, 0x4A))
            d.rectangle([lx + 28, ty0 + 30, lx + 60, ty1 - 18], fill=(0x2E, 0x5A, 0x8A))
            # hull: slanted bow, flat stern, white wake line below
            d.polygon([(lx + 8, ty1 - 18), (lx + 296, ty1 - 18),
                       (lx + 308, ty1 - 6), (lx + 22, ty1 - 6)], fill=(0x3A, 0x3A, 0x44))
            d.line([(lx + 8, ty1 - 2), (lx + 304, ty1 - 2)], fill=WHITE, width=1)
            d.text((lx + 150, ty0 + 6), "%", font=font(SANS_BOLD, 34), fill=WHITE)
            d.text((lx + 196, ty0 + 30), "TARIFFS", font=font(SANS_BOLD, 13),
                   fill=(0xBB, 0xBB, 0xBB))
        elif lead["art"] == "breach":
            d.rectangle([lx, ty0, lx + 312, ty1], fill=DARK)
            d.text((lx + 12, ty0 + 8), "CIA", font=font(SANS_BOLD, 36), fill=WHITE)
            # warning triangle with !
            d.polygon([(lx + 210, ty0 + 44), (lx + 232, ty0 + 8), (lx + 254, ty0 + 44)],
                      outline=RED, width=3)
            d.text((lx + 226, ty0 + 16), "!", font=font(SANS_BOLD, 20), fill=RED)
            d.text((lx + 96, ty0 + 34), "BREACH", font=font(SANS_BOLD, 13),
                   fill=(0xBB, 0xBB, 0xBB))
        else:  # rocket
            d.rectangle([lx, ty0, lx + 312, ty1], fill=DARK)
            # stars
            for sx, sy in [(20, 10), (280, 12), (250, 40), (60, 44), (150, 8)]:
                d.ellipse([lx + sx, ty0 + sy, lx + sx + 3, ty0 + sy + 3], fill=WHITE)
            # rocket body + nose + flame
            d.rectangle([lx + 130, ty0 + 14, lx + 146, ty0 + 40], fill=WHITE)
            d.polygon([(lx + 130, ty0 + 14), (lx + 146, ty0 + 14), (lx + 138, ty0 + 2)],
                      fill=RED)
            d.polygon([(lx + 130, ty0 + 40), (lx + 146, ty0 + 40), (lx + 138, ty0 + 52)],
                      fill=GOLD)
            d.text((lx + 168, ty0 + 10), "LIFT-OFF", font=font(SANS_BOLD, 16),
                   fill=WHITE)
            d.text((lx + 168, ty0 + 34), "PAKISTAN ASTRONAUT", font=font(SANS_BOLD, 10),
                   fill=(0xBB, 0xBB, 0xBB))
        # number (red) + headline (serif bold 18, max 2 lines)
        ntxt = f"{lead['num']}."
        nw = f_num2.getlength(ntxt)
        d.text((lx, 458), ntxt, font=f_num2, fill=RED)
        lines = wrap_text(f_lead, lead["title"], 312 - nw - 6)
        y = 458
        for ln in lines[:2]:
            d.text((lx + nw + 6, y), ln, font=f_lead, fill=INK)
            y += 22
        # one sentence (13px, 1 line)
        sent = lead["sentence"] + " \u2014 " + lead["source"]
        sw = f_sent.getlength(sent)
        diag.append(f"lead {lead['num']} sentence {sw:.1f}/312 lines {len(lines)}")
        if sw > 312:
            diag.append(f"OVERFLOW lead {lead['num']} sentence")
        d.text((lx, 500), sent, font=f_sent, fill=INK)

    # ---- F. Timeline UTC (524..576)
    d.line([(28, 548), (996, 548)], fill=INK, width=2)
    centers = [124, 318, 512, 705, 899]
    for (t, lab), cx in zip(TIMELINE, centers):
        d.ellipse([cx - 5, 543, cx + 5, 553], fill=RED)
        tw = f_time.getlength(t)
        d.text((cx - tw / 2, 526), t, font=f_time, fill=RED)
        lw = f_tlab.getlength(lab)
        d.text((cx - lw / 2, 556), lab, font=f_tlab, fill=INK)
        diag.append(f"timeline {t} label {lw:.1f}px at cx {cx}")

    # ---- G. Briefs (580..960): 3 cols @312, gap 16
    col_xs = [28, 356, 684]
    ends = []
    for cx, col in zip(col_xs, COLS):
        y = 580
        for num, title in col:
            item = f"{num}. {title}"
            w = f_brief.getlength(item)
            if w > 312:
                diag.append(f"OVERFLOW brief {num}: {w:.1f}/312 :: {item}")
            d.text((cx, y), item, font=f_brief, fill=INK)
            y += 24
        ends.append(y - 7)
    diag.append(f"brief column ends {ends} (limit <=940)")

    # ---- Regions line (946..960)
    d.text((28, 946), REGIONS_LINE, font=f_reg, fill=GREY)
    diag.append(f"regions line {f_reg.getlength(REGIONS_LINE):.1f}/968")

    # ---- H. Footer (964..1000)
    d.rectangle([28, 964, 996, 966], fill=INK)
    d.text((28, 972), SOURCES_LINE, font=f_src, fill=GREY)
    fdate = "WEDNESDAY, 25 NOVEMBER 2026"
    d.text((996 - f_fdate.getlength(fdate), 972), fdate, font=f_fdate, fill=INK)
    diag.append(f"sources line {f_src.getlength(SOURCES_LINE):.1f} vs date at "
                f"{996 - f_fdate.getlength(fdate):.0f}")

    img.save("entry.png", optimize=True)
    print("\n".join(diag))


if __name__ == "__main__":
    main()
