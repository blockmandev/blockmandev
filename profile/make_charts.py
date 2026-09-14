#!/usr/bin/env python3
"""
Generates the README chart set (dark + light) into ./profile/.
Edit the DATA block below — everything else is layout.
Run: python3 make_charts.py
"""
import json, math, os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
try:
    D = json.load(open(DATA_FILE, encoding="utf-8"))
    print(f"using real data from data.json (fetched {D.get('generated','?')})")
except Exception:
    D = {}
    print("!! data.json not found — the GitHub and activity charts will draw")
    print("!! placeholder numbers. Run  python3 fetch_data.py  first.")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------- DATA
LANGS = [
    # label,             depth, family
    ("Rust",              95, "systems"),
    ("Go",                92, "systems"),
    ("C / C++",           90, "systems"),
    ("x86-64 / ARM asm",  86, "systems"),
    ("Python",            88, "applied"),
    ("TypeScript",        82, "applied"),
    ("Swift / Obj-C",     74, "mobile"),
    ("Kotlin / Java",     70, "mobile"),
]

FAMILIES = [("systems", "Systems & low level", "blue"),
            ("applied", "Applied & tooling",   "green"),
            ("mobile",  "Mobile platforms",    "purple")]

DOMAINS = [
    ("Reverse\nengineering", 96),
    ("Binary\nanalysis",     93),
    ("Software\nprotection", 90),
    ("Mobile\nsecurity",     84),
    ("AI / ML\ntooling",     78),
    ("Backend\n& data",      80),
]

FOCUS = [
    ("Reverse engineering", 30, "blue"),
    ("Software protection", 22, "teal"),
    ("AI / ML tooling",     18, "green"),
    ("Backend & data",      17, "purple"),
    ("Product & interface", 13, "amber"),
]

MATRIX_COLS = ["Windows", "macOS", "Linux", "Android", "iOS", "WASM"]
MATRIX_ROWS = [
    ("Reverse engineering",    [4, 4, 4, 4, 4, 3]),
    ("Dynamic instrumentation",[4, 3, 4, 4, 3, 2]),
    ("Devirtualization",       [4, 3, 3, 3, 2, 2]),
    ("Protocol / API analysis",[4, 4, 4, 4, 3, 3]),
    ("Native library dev",     [4, 3, 4, 4, 3, 3]),
]

# --- measured data (from data.json when present, placeholders otherwise)
FALLBACK = dict(
    waka_days=[3.1, 5.4, 6.2, 2.0, 7.1, 4.8, 5.9, 6.6, 3.3, 8.0, 5.1, 4.2, 6.8, 7.4,
               2.6, 5.5, 6.1, 4.9, 7.8, 3.7, 5.2, 6.9, 4.4, 8.3, 5.7, 3.9, 6.4, 7.0,
               4.6, 5.8],
    waka_langs=[("Rust", 46.2), ("Go", 31.8), ("Python", 22.4), ("TypeScript", 17.1),
                ("C++", 12.6), ("Other", 9.3)],
    waka_total=162.0, waka_daily_avg=5.4,
    monthly=[210, 265, 190, 310, 288, 245, 330, 275, 240, 305, 260, 295],
    month_labels=["10", "11", "12", "01", "02", "03", "04", "05", "06", "07", "08", "09"],
    commits=3213, prs=118, issues=64, contributions=3641,
    repos=48, stars=312, followers=190, calendar=None,
)


def d(key):
    v = D.get(key)
    return FALLBACK[key] if v in (None, [], 0, {}) else v


# ---------------------------------------------------------------- THEME
THEMES = {
    "dark": dict(
        bg="#0d1117", panel="#11161d", grid="#222c38", rule="#1c2530",
        text="#e6edf3", dim="#7d8590", faint="#4b5563",
        blue="#1f6feb", teal="#0e7490", green="#10a37f",
        amber="#f59e0b", purple="#8957e5", track="#1a2028",
    ),
    "light": dict(
        bg="#f8fafc", panel="#ffffff", grid="#dbe3ec", rule="#e2e8f0",
        text="#0f172a", dim="#64748b", faint="#94a3b8",
        blue="#1f6feb", teal="#0e7490", green="#0d8f70",
        amber="#d97706", purple="#7c3aed", track="#eef2f7",
    ),
}

SANS = "ui-sans-serif,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,Liberation Mono,monospace"


def esc(s):
    """SVG is XML — a bare & or < in a label makes the whole file fail to render."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def head(w, h, t):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img">\n'
            f'<rect width="{w}" height="{h}" rx="10" fill="{t["bg"]}"/>\n')


def title(x, y, label, sub, t):
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="17" font-weight="640" '
            f'fill="{t["text"]}">{esc(label)}</text>\n'
            f'<text x="{x}" y="{y+19}" font-family="{SANS}" font-size="12" '
            f'fill="{t["dim"]}">{esc(sub)}</text>\n')


# ------------------------------------------------------- 1. LANGUAGE BARS
def bars(t, name):
    W, H = 1200, 452
    x0, top, gap = 250, 132, 38
    track_w = W - x0 - 95
    fam_col = {k: t[c] for k, _, c in FAMILIES}
    s = head(W, H, t)
    s += title(32, 44, "Languages I reach for",
               "Depth by family, so the colour tells you which layer of the stack it is.", t)

    lx = 32
    for key, label, colkey in FAMILIES:
        s += f'<rect x="{lx}" y="{top-36}" width="10" height="10" rx="2.5" fill="{t[colkey]}"/>\n'
        s += (f'<text x="{lx+18}" y="{top-27}" font-family="{SANS}" font-size="12" '
              f'fill="{t["dim"]}">{esc(label)}</text>\n')
        lx += 30 + 7.4 * len(label)
    s += f'<line x1="32" y1="{top-14}" x2="{W-32}" y2="{top-14}" stroke="{t["rule"]}" stroke-width="1"/>\n'

    for i, (label, val, fam) in enumerate(LANGS):
        y = top + i * gap
        w = track_w * val / 100.0
        s += (f'<text x="{x0-16}" y="{y+13}" text-anchor="end" font-family="{SANS}" '
              f'font-size="14" fill="{t["text"]}">{esc(label)}</text>\n')
        s += f'<rect x="{x0}" y="{y}" width="{track_w}" height="18" rx="4" fill="{t["track"]}"/>\n'
        s += (f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="18" rx="4" fill="{fam_col[fam]}">'
              f'<animate attributeName="width" from="0" to="{w:.1f}" dur="0.9s" '
              f'begin="{0.06*i:.2f}s" fill="freeze" '
              f'calcMode="spline" keySplines="0.22 1 0.36 1" keyTimes="0;1"/></rect>\n')
        s += (f'<text x="{x0+track_w+14}" y="{y+13}" font-family="{MONO}" font-size="12.5" '
              f'fill="{t["dim"]}">{val}</text>\n')

    s += (f'<text x="32" y="{H-22}" font-family="{SANS}" font-size="11.5" '
          f'fill="{t["faint"]}">Self-rated depth, not lines of code.</text>\n')
    s += "</svg>\n"
    write(name, s)


# ------------------------------------------------------------ 2. RADAR
def radar(t, name):
    W, H = 580, 400
    cx, cy, R = 290, 228, 106
    n = len(DOMAINS)
    s = head(W, H, t)
    s += title(26, 40, "Where the depth is", "Six areas most of the work lands in.", t)

    def pt(i, r):
        a = -math.pi / 2 + 2 * math.pi * i / n
        return cx + r * math.cos(a), cy + r * math.sin(a)

    for ring in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, R * ring) for i in range(n)))
        s += (f'<polygon points="{pts}" fill="none" stroke="{t["grid"]}" '
              f'stroke-width="1"/>\n')
    for i in range(n):
        x, y = pt(i, R)
        s += f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{t["grid"]}" stroke-width="1"/>\n'

    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in
                   (pt(i, R * v / 100.0) for i, (_, v) in enumerate(DOMAINS)))
    ctr = " ".join(f"{cx},{cy}" for _ in range(n))
    s += (f'<polygon points="{pts}" fill="{t["blue"]}" fill-opacity="0.22" '
          f'stroke="{t["blue"]}" stroke-width="2" stroke-linejoin="round">'
          f'<animate attributeName="points" from="{ctr}" to="{pts}" dur="1s" '
          f'fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1" keyTimes="0;1"/>'
          f'</polygon>\n')

    for i, (label, v) in enumerate(DOMAINS):
        x, y = pt(i, R * v / 100.0)
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{t["amber"]}"/>\n'
        lx, ly = pt(i, R + 30)
        anchor = "middle"
        if lx > cx + 12: anchor = "start"
        elif lx < cx - 12: anchor = "end"
        lines = label.split("\n")
        oy = -6 if ly < cy else 2
        for j, ln in enumerate(lines):
            s += (f'<text x="{lx:.0f}" y="{ly + oy + j*13:.0f}" text-anchor="{anchor}" '
                  f'font-family="{SANS}" font-size="11.5" fill="{t["dim"]}">{esc(ln)}</text>\n')
    s += "</svg>\n"
    write(name, s)


# ------------------------------------------------------------ 3. DONUT
def donut(t, name):
    W, H = 580, 400
    cx, cy, R, r = 168, 238, 98, 58
    s = head(W, H, t)
    s += title(26, 40, "How a typical month splits",
               "Rough share of working hours, not a contract.", t)

    total = sum(v for _, v, _ in FOCUS)
    a0 = -math.pi / 2
    for label, v, colkey in FOCUS:
        sweep = 2 * math.pi * v / total
        a1 = a0 + sweep
        large = 1 if sweep > math.pi else 0
        x0, y0 = cx + R * math.cos(a0), cy + R * math.sin(a0)
        x1, y1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
        xi, yi = cx + r * math.cos(a1), cy + r * math.sin(a1)
        xj, yj = cx + r * math.cos(a0), cy + r * math.sin(a0)
        d = (f"M{x0:.1f},{y0:.1f} A{R},{R} 0 {large} 1 {x1:.1f},{y1:.1f} "
             f"L{xi:.1f},{yi:.1f} A{r},{r} 0 {large} 0 {xj:.1f},{yj:.1f} Z")
        s += f'<path d="{d}" fill="{t[colkey]}"/>\n'
        a0 = a1

    ly = cy - 34 * (len(FOCUS) - 1) / 2 + 5
    for label, v, colkey in FOCUS:
        s += f'<rect x="306" y="{ly-10}" width="10" height="10" rx="2.5" fill="{t[colkey]}"/>\n'
        s += (f'<text x="326" y="{ly}" font-family="{SANS}" font-size="13" '
              f'fill="{t["text"]}">{esc(label)}</text>\n')
        s += (f'<text x="{W-26}" y="{ly}" text-anchor="end" font-family="{MONO}" '
              f'font-size="12.5" fill="{t["dim"]}">{v}%</text>\n')
        ly += 34
    s += "</svg>\n"
    write(name, s)


# ------------------------------------------------------ 4. PLATFORM MATRIX
def matrix(t, name):
    W, H = 1200, 382
    x0, y0 = 250, 118
    cw, ch = 140, 34
    s = head(W, H, t)
    s += title(32, 44, "Platform coverage",
               "How much of the work actually happens at each intersection.", t)
    s += f'<line x1="32" y1="72" x2="{W-32}" y2="72" stroke="{t["rule"]}" stroke-width="1"/>\n'

    for j, col in enumerate(MATRIX_COLS):
        s += (f'<text x="{x0 + j*cw + cw/2 - 8}" y="{y0-14}" text-anchor="middle" '
              f'font-family="{SANS}" font-size="12.5" fill="{t["dim"]}">{esc(col)}</text>\n')

    for i, (row, vals) in enumerate(MATRIX_ROWS):
        y = y0 + i * (ch + 6)
        s += (f'<text x="{x0-18}" y="{y+22}" text-anchor="end" font-family="{SANS}" '
              f'font-size="13.5" fill="{t["text"]}">{esc(row)}</text>\n')
        for j, v in enumerate(vals):
            op = {1: 0.12, 2: 0.32, 3: 0.62, 4: 1.0}[v]
            x = x0 + j * cw
            s += (f'<rect x="{x}" y="{y}" width="{cw-16}" height="{ch}" rx="5" '
                  f'fill="{t["track"]}"/>\n')
            s += (f'<rect x="{x}" y="{y}" width="{cw-16}" height="{ch}" rx="5" '
                  f'fill="{t["blue"]}" fill-opacity="{op}"/>\n')

    lx = x0 - 18
    s += (f'<text x="{lx-32}" y="{H-24}" font-family="{SANS}" font-size="11.5" '
          f'fill="{t["faint"]}">less</text>\n')
    for k, op in enumerate([0.12, 0.32, 0.62, 1.0]):
        s += (f'<rect x="{lx+38+k*20}" y="{H-36}" width="16" height="16" rx="3.5" '
              f'fill="{t["track"]}"/>\n'
              f'<rect x="{lx+38+k*20}" y="{H-36}" width="16" height="16" rx="3.5" '
              f'fill="{t["blue"]}" fill-opacity="{op}"/>\n')
    s += (f'<text x="{lx+128}" y="{H-24}" font-family="{SANS}" font-size="11.5" '
          f'fill="{t["faint"]}">more</text>\n')
    s += "</svg>\n"
    write(name, s)


# ------------------------------------------------- 5. CODING HOURS (30 DAYS)
def hours(t, name):
    W, H = 1200, 400
    x0, y0 = 62, 128
    pw, ph = W - x0 - 46, 190
    days = d("waka_days")[-30:]
    peak = max(days) if days else 1
    top = math.ceil(peak / 2.0) * 2
    n = len(days)
    step = pw / max(n - 1, 1)

    s = head(W, H, t)
    s += title(32, 44, "Coding activity", "Hours at the keyboard, last 30 days.", t)

    for k, v in enumerate([("total", f'{d("waka_total")} h'),
                           ("daily average", f'{d("waka_daily_avg")} h'),
                           ("best day", f"{peak:g} h")]):
        x = W - 46 - (2 - k) * 150
        s += (f'<text x="{x}" y="34" text-anchor="end" font-family="{MONO}" font-size="19" '
              f'font-weight="600" fill="{t["text"]}">{v[1]}</text>\n')
        s += (f'<text x="{x}" y="50" text-anchor="end" font-family="{SANS}" font-size="11" '
              f'fill="{t["dim"]}">{v[0]}</text>\n')
    s += f'<line x1="32" y1="72" x2="{W-32}" y2="72" stroke="{t["rule"]}" stroke-width="1"/>\n'

    for g in range(5):
        gy = y0 + ph - ph * g / 4
        s += (f'<line x1="{x0}" y1="{gy:.0f}" x2="{x0+pw}" y2="{gy:.0f}" '
              f'stroke="{t["grid"]}" stroke-width="1"/>\n')
        s += (f'<text x="{x0-12}" y="{gy+4:.0f}" text-anchor="end" font-family="{MONO}" '
              f'font-size="11" fill="{t["faint"]}">{top*g/4:g}</text>\n')

    pts = [(x0 + i * step, y0 + ph - ph * v / top) for i, v in enumerate(days)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    s += (f'<polygon points="{x0},{y0+ph} {line} {x0+pw:.1f},{y0+ph}" '
          f'fill="{t["green"]}" fill-opacity="0.16"/>\n')
    s += (f'<polyline points="{line}" fill="none" stroke="{t["green"]}" stroke-width="2.2" '
          f'stroke-linejoin="round" stroke-linecap="round"/>\n')
    bx, by = pts[days.index(peak)]
    s += f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="4" fill="{t["amber"]}"/>\n'

    for i in range(0, n, 5):
        s += (f'<text x="{x0+i*step:.0f}" y="{y0+ph+22}" text-anchor="middle" '
              f'font-family="{MONO}" font-size="11" fill="{t["faint"]}">{n-i}d</text>\n')
    s += (f'<text x="32" y="{H-20}" font-family="{SANS}" font-size="11.5" '
          f'fill="{t["faint"]}">Measured by Wakapi across every editor session.</text>\n')
    s += "</svg>\n"
    write(name, s)


# ------------------------------------------------------ 6. TIME BY LANGUAGE
def timelangs(t, name):
    W, H = 1200, 196
    x0, bw = 32, 1200 - 64
    rows = d("waka_langs")
    total = sum(v for _, v in rows) or 1
    cols = [t[k] for k in ("blue", "green", "teal", "purple", "amber", "faint", "dim", "faint")]

    s = head(W, H, t)
    s += title(32, 44, "Time by language", "The same 30 days, split by what was open.", t)

    x = x0
    for i, (label, v) in enumerate(rows):
        w = bw * v / total
        r = 5 if i in (0, len(rows) - 1) else 0
        s += (f'<rect x="{x:.1f}" y="80" width="{max(w-3,2):.1f}" height="30" rx="{r}" '
              f'fill="{cols[i % len(cols)]}"/>\n')
        x += w

    lx, ly = 32, 152
    for i, (label, v) in enumerate(rows):
        if lx > W - 240:
            lx, ly = 32, ly + 28
        s += f'<rect x="{lx}" y="{ly-10}" width="10" height="10" rx="2.5" fill="{cols[i % len(cols)]}"/>\n'
        s += (f'<text x="{lx+18}" y="{ly}" font-family="{SANS}" font-size="13" '
              f'fill="{t["text"]}">{esc(label)}'
              f'<tspan dx="8" font-family="{MONO}" font-size="12" fill="{t["dim"]}">{v:g}h</tspan>'
              f'</text>\n')
        lx += 92 + 7.6 * len(label)
    s += "</svg>\n"
    write(name, s)


# ------------------------------------------------------- 7. GIT YEAR IN BARS
def gityear(t, name):
    W, H = 1200, 400
    x0, y0 = 62, 150
    pw, ph = W - x0 - 46, 170
    MONTH = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
             "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
    vals = d("monthly")
    labels = [MONTH.get(str(m)[-2:], str(m)) for m in d("month_labels")]
    top = max(vals) or 1
    bw = pw / len(vals)

    s = head(W, H, t)
    s += title(32, 44, "The last twelve months", "Contributions per month, and the year's totals.", t)

    stats = [("commits", d("commits")), ("pull requests", d("prs")),
             ("stars earned", d("stars")), ("public repos", d("repos"))]
    for k, (lab, v) in enumerate(stats):
        x = 32 + k * 190
        s += (f'<text x="{x}" y="106" font-family="{MONO}" font-size="24" font-weight="600" '
              f'fill="{t["text"]}">{v}</text>\n')
        s += (f'<text x="{x}" y="124" font-family="{SANS}" font-size="11.5" '
              f'fill="{t["dim"]}">{lab}</text>\n')
    s += f'<line x1="32" y1="72" x2="{W-32}" y2="72" stroke="{t["rule"]}" stroke-width="1"/>\n'

    s += (f'<line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" '
          f'stroke="{t["grid"]}" stroke-width="1"/>\n')
    for i, v in enumerate(vals):
        h = ph * v / top
        x = x0 + i * bw
        col = t["amber"] if v == top else t["blue"]
        s += (f'<rect x="{x+22:.1f}" y="{y0+ph-h:.1f}" width="{bw-44:.1f}" height="{h:.1f}" '
              f'rx="4" fill="{col}">'
              f'<animate attributeName="height" from="0" to="{h:.1f}" dur="0.8s" '
              f'begin="{0.05*i:.2f}s" fill="freeze" calcMode="spline" '
              f'keySplines="0.22 1 0.36 1" keyTimes="0;1"/>'
              f'<animate attributeName="y" from="{y0+ph}" to="{y0+ph-h:.1f}" dur="0.8s" '
              f'begin="{0.05*i:.2f}s" fill="freeze" calcMode="spline" '
              f'keySplines="0.22 1 0.36 1" keyTimes="0;1"/></rect>\n')
        s += (f'<text x="{x+bw/2:.0f}" y="{y0+ph+22}" text-anchor="middle" font-family="{MONO}" '
              f'font-size="11" fill="{t["faint"]}">{esc(labels[i])}</text>\n')
        s += (f'<text x="{x+bw/2:.0f}" y="{y0+ph-h-9:.0f}" text-anchor="middle" '
              f'font-family="{MONO}" font-size="11" fill="{t["dim"]}">{v}</text>\n')
    s += "</svg>\n"
    write(name, s)


# ---------------------------------------------------------- 8. CONTRIBUTIONS
def heatmap(t, name):
    W, H = 1200, 320
    cell, gap = 16, 4
    x0, y0 = 74, 112
    weeks = D.get("calendar")
    if not weeks:
        weeks = []
        seed = 7
        for w in range(53):
            col = []
            for day in range(7):
                seed = (seed * 1103515245 + 12345) % 2147483648
                r = seed % 100
                col.append(0 if day in (0, 6) and r < 55 else max(0, (r - 30) // 9))
            weeks.append(col)
    weeks = weeks[-53:]
    peak = max((max(w) for w in weeks if w), default=1) or 1
    total = D.get("contributions", sum(sum(w) for w in weeks))

    s = head(W, H, t)
    s += title(32, 44, "Contribution calendar", f"{total} contributions in the last year.", t)
    s += f'<line x1="32" y1="72" x2="{W-32}" y2="72" stroke="{t["rule"]}" stroke-width="1"/>\n'

    for i, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        s += (f'<text x="{x0-12}" y="{y0+i*(cell+gap)+13}" text-anchor="end" '
              f'font-family="{SANS}" font-size="11" fill="{t["faint"]}">{lab}</text>\n')

    for wi, week in enumerate(weeks):
        for di, v in enumerate(week):
            lvl = 0 if v == 0 else min(4, 1 + int(3 * v / max(peak, 1)))
            op = {0: 0.0, 1: 0.30, 2: 0.52, 3: 0.75, 4: 1.0}[lvl]
            x, y = x0 + wi * (cell + gap), y0 + di * (cell + gap)
            s += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3.5" fill="{t["track"]}"/>\n'
            if op:
                s += (f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3.5" '
                      f'fill="{t["green"]}" fill-opacity="{op}"/>\n')

    ly = y0 + 7 * (cell + gap) + 26
    s += f'<text x="{x0}" y="{ly}" font-family="{SANS}" font-size="11.5" fill="{t["faint"]}">less</text>\n'
    for k, op in enumerate([0.0, 0.30, 0.52, 0.75, 1.0]):
        x = x0 + 36 + k * 22
        s += f'<rect x="{x}" y="{ly-12}" width="15" height="15" rx="3.5" fill="{t["track"]}"/>\n'
        if op:
            s += (f'<rect x="{x}" y="{ly-12}" width="15" height="15" rx="3.5" '
                  f'fill="{t["green"]}" fill-opacity="{op}"/>\n')
    s += f'<text x="{x0+156}" y="{ly}" font-family="{SANS}" font-size="11.5" fill="{t["faint"]}">more</text>\n'
    s += "</svg>\n"
    write(name, s)


def write(name, svg):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  wrote {p}  ({len(svg)} bytes)")


if __name__ == "__main__":
    for mode, t in THEMES.items():
        bars(t,   f"skills-langs-{mode}.svg")
        radar(t,  f"skills-radar-{mode}.svg")
        donut(t,  f"skills-focus-{mode}.svg")
        matrix(t, f"skills-platforms-{mode}.svg")
        hours(t,     f"activity-hours-{mode}.svg")
        timelangs(t, f"activity-langs-{mode}.svg")
        gityear(t,   f"git-year-{mode}.svg")
        heatmap(t,   f"git-heatmap-{mode}.svg")
    print("done")
