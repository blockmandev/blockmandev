#!/usr/bin/env python3
"""
Generates the README chart set (dark + light) into ./profile/.
Edit the DATA block below — everything else is layout.
Run: python3 make_charts.py
"""
import math, os

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
    print("done")
