#!/usr/bin/env python3
"""
Premium GitHub Profile README SVG Generator
Generates three cinematic, SMIL-animated SVG files:
  1. github-contribution-animation.svg  — diagonal-reveal contribution graph
  2. terminal-card.svg                  — macOS terminal with ASCII avatar
  3. info-card.svg                      — neofetch-style info panel
Automatically injects them into README.md between marker comments.
"""

import os
import sys
import math
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[warn] Pillow not installed – ASCII portrait will use a placeholder.", file=sys.stderr)

# ══════════════════════════════════════════════════════════════════
# ── CONFIG ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
GH_USERNAME = os.getenv("GH_USERNAME", "ShivanshGarg007")
GH_TOKEN    = os.getenv("GH_TOKEN", "")

NAME      = "Shivansh Garg"
ROLE      = "Full-Stack Software Engineer"
EDUCATION = "Chitkara University  ·  CGPA 10.00"
LOCATION  = "India 🇮🇳"
PORTFOLIO = "shivanshgarg.vercel.app"
EMAIL     = "shivanshgarg007@gmail.com"
STACK     = ["React", "TypeScript", "Node.js", "Python", "Java", "MongoDB", "PostgreSQL", "AWS S3"]
HIGHLIGHTS = [
    "🥇 Build with Bharat 3.0 — Winner",
    "🏅 Hack4Delhi 2026 — Top 30 / 4,500+",
    "📊 Notora · 100+ users · 1,700+ views",
]

BASE_DIR    = Path(__file__).resolve().parent.parent
ASSETS_DIR  = BASE_DIR / "assets"
README_PATH = BASE_DIR / "README.md"
ASSETS_DIR.mkdir(exist_ok=True)

# ── Palette ────────────────────────────────────────────────────────
BG      = "#0d1117"
SURFACE = "#161b22"
BORDER  = "#21262d"
BORDER2 = "#30363d"
TEXT    = "#e6edf3"
DIM     = "#8b949e"
CYAN    = "#79c0ff"
GREEN   = "#56d364"
ORANGE  = "#ffa657"
PURPLE  = "#d2a8ff"
YELLOW  = "#e3b341"
RED     = "#ff7b72"

CONTRIB_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

README_MARKER_START = "<!-- PROFILE-SVG-START -->"
README_MARKER_END   = "<!-- PROFILE-SVG-END -->"


# ══════════════════════════════════════════════════════════════════
# ── GITHUB DATA ────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
def fetch_contributions() -> list[list[int]]:
    """Return a 53×7 grid of contribution levels (0-4). Cols=weeks, rows=weekdays (Sun-Sat)."""
    if not GH_TOKEN:
        return _fake_contributions()

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }
    """
    try:
        resp = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"login": GH_USERNAME}},
            headers={"Authorization": f"Bearer {GH_TOKEN}"},
            timeout=10,
        )
        weeks = (resp.json()["data"]["user"]["contributionsCollection"]
                 ["contributionCalendar"]["weeks"])

        grid = []
        for week in weeks[-53:]:
            col = [0] * 7
            for day in week["contributionDays"]:
                dow = (datetime.strptime(day["date"], "%Y-%m-%d").weekday() + 1) % 7
                col[dow] = day["contributionCount"]
            grid.append(col)

        while len(grid) < 53:
            grid.insert(0, [0] * 7)

        def to_level(c: int) -> int:
            return 0 if c == 0 else 1 if c < 3 else 2 if c < 7 else 3 if c < 12 else 4

        return [[to_level(c) for c in col] for col in grid]
    except Exception as exc:
        print(f"[warn] GitHub API: {exc}", file=sys.stderr)
        return _fake_contributions()


def _fake_contributions() -> list[list[int]]:
    random.seed(abs(hash(GH_USERNAME)) % (2 ** 31))
    grid = []
    for col in range(53):
        col_data = []
        for row in range(7):
            weekend = row in (0, 6)
            base = 0.18 if weekend else min(0.65 + col * 0.004, 0.80)
            r = random.random()
            level = 0 if r > base else 1 if r > base * 0.55 else 2 if r > base * 0.28 else 3 if r > base * 0.10 else 4
            col_data.append(level)
        grid.append(col_data)
    return grid


# ── ASCII avatar ───────────────────────────────────────────────────
_ASCII_CHARS = " .'`^,:;Il!i~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


def fetch_avatar_ascii(cols: int = 46, rows: int = 21) -> list[str]:
    """Download avatar, resize to cols×rows, return list of ASCII strings."""
    if not HAS_PIL:
        return _placeholder_ascii(cols, rows)
    try:
        url = f"https://avatars.githubusercontent.com/{GH_USERNAME}?size=300"
        r   = requests.get(url, timeout=10)
        img = Image.open(BytesIO(r.content)).convert("L")
        img = img.resize((cols, rows), Image.LANCZOS)
        lines = []
        for y in range(rows):
            row_str = ""
            for x in range(cols):
                pix     = img.getpixel((x, y))
                idx     = int(pix / 255 * (len(_ASCII_CHARS) - 1))
                row_str += _ASCII_CHARS[idx]
            lines.append(row_str)
        return lines
    except Exception as exc:
        print(f"[warn] avatar: {exc}", file=sys.stderr)
        return _placeholder_ascii(cols, rows)


def _placeholder_ascii(cols: int, rows: int) -> list[str]:
    lines = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            d = math.hypot(c - cols // 2, r - rows // 2)
            line += ("@" if d < 2 else "#" if d < 5 else "*" if d < 8
                     else "+" if d < 11 else "-" if d < 14 else ".")
        lines.append(line)
    return lines


# ══════════════════════════════════════════════════════════════════
# ── SVG 1: CONTRIBUTION GRAPH ──────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
def generate_contribution_svg(grid: list[list[int]]) -> str:
    CELL  = 12
    GAP   = 3
    STEP  = CELL + GAP
    COLS  = len(grid)   # 53
    ROWS  = 7
    MARGIN_L = 32
    MARGIN_T = 46

    grid_w = COLS * STEP - GAP
    W = grid_w + MARGIN_L + 24
    H = ROWS * STEP - GAP + MARGIN_T + 42

    p = []   # SVG parts accumulator
    p.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'xmlns="http://www.w3.org/2000/svg">')

    # ── defs ──────────────────────────────────────────────────────
    p.append('<defs>')
    p.append(f'''
  <linearGradient id="cBg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%"   stop-color="#0d1117"/>
    <stop offset="100%" stop-color="#161b22"/>
  </linearGradient>
  <linearGradient id="glassSheen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stop-color="#ffffff" stop-opacity="0.05"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0.00"/>
  </linearGradient>
  <linearGradient id="accentH" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="{CYAN}"/>
    <stop offset="50%"  stop-color="{PURPLE}"/>
    <stop offset="100%" stop-color="{ORANGE}"/>
  </linearGradient>
  <filter id="glow3" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="b"/>
    <feComposite   in="b" in2="SourceGraphic" operator="over"/>
  </filter>
  <filter id="glow4" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="b"/>
    <feComposite   in="b" in2="SourceGraphic" operator="over"/>
  </filter>''')
    p.append('</defs>')

    # ── background card ───────────────────────────────────────────
    p.append(f'<rect width="{W}" height="{H}" fill="url(#cBg)" rx="14"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#glassSheen)" rx="14"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="none" stroke="{BORDER2}" '
             f'stroke-width="1" rx="14" opacity="0.7"/>')
    p.append(f'<rect x="0" y="0" width="{W}" height="3" fill="url(#accentH)" rx="14"/>')

    # ── title ─────────────────────────────────────────────────────
    p.append(f'<text x="14" y="26" font-family="\'JetBrains Mono\',monospace" '
             f'font-size="12" font-weight="600" fill="{TEXT}">Contributions</text>')
    p.append(f'<text x="{W - 12}" y="26" text-anchor="end" '
             f'font-family="\'JetBrains Mono\',monospace" font-size="11" fill="{DIM}">'
             f'@{GH_USERNAME}</text>')

    # ── month labels ──────────────────────────────────────────────
    today      = datetime.now()
    start_date = today - timedelta(weeks=52)
    month_abbr = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"]
    prev_month = None
    for col in range(COLS):
        d = start_date + timedelta(weeks=col)
        if d.month != prev_month:
            x = MARGIN_L + col * STEP
            p.append(f'<text x="{x}" y="{MARGIN_T - 10}" '
                     f'font-family="\'JetBrains Mono\',monospace" font-size="9" fill="{DIM}">'
                     f'{month_abbr[d.month - 1]}</text>')
            prev_month = d.month

    # ── day labels ────────────────────────────────────────────────
    days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    for row in range(ROWS):
        if row % 2 == 1:
            y = MARGIN_T + row * STEP + CELL
            p.append(f'<text x="{MARGIN_L - 5}" y="{y}" text-anchor="end" '
                     f'font-family="\'JetBrains Mono\',monospace" font-size="8" fill="{DIM}">'
                     f'{days[row]}</text>')

    # ── grid cells ────────────────────────────────────────────────
    for col in range(COLS):
        for row in range(ROWS):
            level = grid[col][row]
            color = CONTRIB_COLORS[level]
            x     = MARGIN_L + col * STEP
            y     = MARGIN_T + row * STEP
            delay = (col + (ROWS - 1 - row)) * 0.024  # diagonal reveal

            filt = (' filter="url(#glow3)"' if level == 3 else
                    ' filter="url(#glow4)"' if level == 4 else '')

            # Cell – reveals with fade-in
            p.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}"{filt} opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="0.28s" fill="freeze"/>'
                f'</rect>'
            )
            # Glint – white flash that settles to transparent
            if level > 0:
                p.append(
                    f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                    f'fill="white" opacity="0">'
                    f'<animate attributeName="opacity" '
                    f'values="0;0;0.85;0" keyTimes="0;0.01;0.25;1" '
                    f'begin="{delay:.3f}s" dur="0.55s" fill="freeze"/>'
                    f'</rect>'
                )

    # ── legend ────────────────────────────────────────────────────
    lx = W - 148
    ly = H - 16
    p.append(f'<text x="{lx}" y="{ly}" font-family="\'JetBrains Mono\',monospace" '
             f'font-size="9" fill="{DIM}">Less</text>')
    for i, c in enumerate(CONTRIB_COLORS):
        p.append(f'<rect x="{lx + 32 + i * 16}" y="{ly - 10}" '
                 f'width="12" height="12" rx="2" fill="{c}"/>')
    p.append(f'<text x="{lx + 32 + 5 * 16 + 4}" y="{ly}" '
             f'font-family="\'JetBrains Mono\',monospace" font-size="9" fill="{DIM}">More</text>')

    p.append('</svg>')
    return "\n".join(p)


# ══════════════════════════════════════════════════════════════════
# ── SVG 2: TERMINAL CARD ───────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
def generate_terminal_svg(ascii_rows: list[str]) -> tuple[str, int, int]:
    COLS    = max((len(r) for r in ascii_rows), default=46)
    ROWS    = len(ascii_rows)
    FS      = 10.4   # font-size (px)
    LH      = 13.0   # line-height (px)
    CW      = 6.25   # approx char width at FS for Courier New
    TITLE_H = 36
    PAD_H   = 14     # horizontal padding
    PAD_V   = 12     # vertical padding (below title bar)
    FOOTER  = 40     # footer area height

    content_w = int(COLS * CW)
    W = content_w + PAD_H * 2
    W = max(W, 400)
    H = TITLE_H + PAD_V + int(ROWS * LH) + PAD_V + FOOTER

    p = []
    p.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'xmlns="http://www.w3.org/2000/svg">')

    p.append('<defs>')
    p.append(f'''
  <linearGradient id="winBg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stop-color="#1c2128"/>
    <stop offset="100%" stop-color="#0d1117"/>
  </linearGradient>
  <linearGradient id="titleBg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stop-color="#21262d"/>
    <stop offset="100%" stop-color="#1c2128"/>
  </linearGradient>
  <filter id="scanFuzz" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0 0.65"
                  numOctaves="1" result="noise"/>
    <feDisplacementMap in="SourceGraphic" in2="noise"
                       scale="0.35" xChannelSelector="R" yChannelSelector="G"/>
  </filter>''')
    p.append('</defs>')

    # Window
    p.append(f'<rect width="{W}" height="{H}" fill="url(#winBg)" rx="12" '
             f'stroke="{BORDER2}" stroke-width="1"/>')
    # Title bar
    p.append(f'<rect width="{W}" height="{TITLE_H}" fill="url(#titleBg)" rx="12"/>')
    p.append(f'<rect y="24" width="{W}" height="12" fill="url(#titleBg)"/>')
    # Separator
    p.append(f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" '
             f'stroke="{BORDER}" stroke-width="1"/>')
    # Traffic lights
    DOT_Y = TITLE_H // 2
    p.append(f'<circle cx="16" cy="{DOT_Y}" r="6" fill="#ff5f57"/>')
    p.append(f'<circle cx="36" cy="{DOT_Y}" r="6" fill="#ffbd2e"/>')
    p.append(f'<circle cx="56" cy="{DOT_Y}" r="6" fill="#28c840"/>')
    # Title text
    p.append(f'<text x="{W // 2}" y="{DOT_Y + 4}" text-anchor="middle" '
             f'font-family="\'JetBrains Mono\',monospace" font-size="12" fill="{DIM}">'
             f'shivansh@garg007: ~</text>')

    # ── ASCII rows ─────────────────────────────────────────────────
    tx = PAD_H
    for i, row_text in enumerate(ascii_rows):
        y     = TITLE_H + PAD_V + int((i + 1) * LH)
        delay = i * 0.07
        safe  = (row_text
                 .replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;"))
        p.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{delay:.3f}s" dur="0.04s" fill="freeze"/>'
            f'<text x="{tx}" y="{y}" '
            f'font-family="\'Courier New\',Courier,monospace" font-size="{FS}" '
            f'fill="{GREEN}" xml:space="preserve">{safe}</text>'
            f'</g>'
        )

    # ── Blinking cursor (appears after all rows) ───────────────────
    all_done = ROWS * 0.07 + 0.18
    cur_y    = TITLE_H + PAD_V + int(ROWS * LH)
    p.append(
        f'<rect x="{tx}" y="{cur_y - int(LH * 0.78)}" '
        f'width="{int(CW)}" height="{int(LH * 0.85)}" fill="{CYAN}" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" '
        f'begin="{all_done:.2f}s" dur="0.001s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="1;0;1" '
        f'begin="{all_done + 0.5:.2f}s" dur="1s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    # ── Typewriter footer ─────────────────────────────────────────
    footer_y   = cur_y + 26
    tw_delay   = all_done + 0.5
    prompt     = f"$ whoami  →  {GH_USERNAME}"
    prompt_w   = int(len(prompt) * CW + 12)
    tw_dur     = f"{len(prompt) * 0.048:.2f}s"

    p.append(
        f'<clipPath id="twClip">'
        f'<rect x="{tx}" y="{footer_y - 14}" width="0" height="20">'
        f'<animate attributeName="width" from="0" to="{prompt_w}" '
        f'begin="{tw_delay:.2f}s" dur="{tw_dur}" fill="freeze"/>'
        f'</rect></clipPath>'
    )
    p.append(
        f'<text x="{tx}" y="{footer_y}" clip-path="url(#twClip)" '
        f'font-family="\'Courier New\',Courier,monospace" font-size="{FS}" fill="{CYAN}" '
        f'xml:space="preserve">{prompt}</text>'
    )

    # Subtle scanlines for CRT atmosphere
    for scan_y in range(TITLE_H, H, 4):
        p.append(f'<line x1="0" y1="{scan_y}" x2="{W}" y2="{scan_y}" '
                 f'stroke="white" stroke-opacity="0.012"/>')

    p.append('</svg>')
    return "\n".join(p), W, H


# ══════════════════════════════════════════════════════════════════
# ── SVG 3: INFO CARD ───────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
def generate_info_svg(card_h: int) -> str:
    W   = 380
    H   = card_h
    FS  = 11.5
    LH  = 19.5
    PAD = 16

    # Build row definitions  (key, value, value_color, bold)
    rows: list[tuple[str, str, str, bool]] = [
        ("",      GH_USERNAME,                   PURPLE, True),
        ("",      "─" * 21,                      BORDER2, False),
        ("OS",    "GitHub Profile · Linux",       CYAN,   False),
        ("Role",  ROLE,                           GREEN,  False),
        ("Edu",   EDUCATION,                      ORANGE, False),
        ("Loc",   LOCATION,                       TEXT,   False),
        ("",      "",                             DIM,    False),
        ("Stack", "",                             YELLOW, True),
    ]
    for i in range(0, len(STACK), 3):
        chunk = "  ·  ".join(STACK[i:i + 3])
        rows.append(("", f"  {chunk}", CYAN, False))
    rows += [
        ("",    "",                        DIM,    False),
        ("Wins","",                        ORANGE, True),
    ]
    for h in HIGHLIGHTS:
        rows.append(("", f"  {h}", TEXT, False))
    rows += [
        ("",    "",                        DIM,    False),
        ("Web",  PORTFOLIO,                CYAN,   False),
        ("Mail", EMAIL,                    DIM,    False),
    ]

    p = []
    p.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'xmlns="http://www.w3.org/2000/svg">')
    p.append('<defs>')
    p.append(f'''
  <linearGradient id="icBg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%"   stop-color="#0d1117"/>
    <stop offset="100%" stop-color="#0f1923"/>
  </linearGradient>
  <linearGradient id="accentV" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="{CYAN}"/>
    <stop offset="50%"  stop-color="{PURPLE}"/>
    <stop offset="100%" stop-color="{ORANGE}"/>
  </linearGradient>
  <filter id="dotGlow" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="2.8" result="b"/>
    <feComposite   in="b" in2="SourceGraphic" operator="over"/>
  </filter>''')
    p.append('</defs>')

    # Card background
    p.append(f'<rect width="{W}" height="{H}" fill="url(#icBg)" rx="12" '
             f'stroke="{BORDER2}" stroke-width="1"/>')
    # Accent top bar
    p.append(f'<rect x="0" y="0" width="{W}" height="3" fill="url(#accentV)" rx="12"/>')

    # Rows with staggered slide-up + fade-in
    y = PAD + int(LH) + 8
    for idx, (key, val, color, bold) in enumerate(rows):
        delay = idx * 0.06
        fw    = "700" if bold else "400"
        fsize = FS + 1.5 if (bold and not key) else FS

        safe_key = key.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        safe_val = val.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

        anim = (
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 10" to="0 0" begin="{delay:.3f}s" dur="0.22s" fill="freeze"/>'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{delay:.3f}s" dur="0.22s" fill="freeze"/>'
        )

        if key:
            p.append(
                f'<g transform="translate(0,10)" opacity="0">{anim}'
                f'<text x="{PAD}" y="{y}" '
                f'font-family="\'JetBrains Mono\',monospace" font-size="{fsize}" '
                f'font-weight="{fw}">'
                f'<tspan fill="{ORANGE}">{safe_key}</tspan>'
                f'<tspan fill="{DIM}">: </tspan>'
                f'<tspan fill="{color}">{safe_val}</tspan>'
                f'</text></g>'
            )
        else:
            p.append(
                f'<g transform="translate(0,10)" opacity="0">{anim}'
                f'<text x="{PAD}" y="{y}" '
                f'font-family="\'JetBrains Mono\',monospace" font-size="{fsize}" '
                f'font-weight="{fw}" fill="{color}" xml:space="preserve">'
                f'{safe_val}</text></g>'
            )
        y += int(LH)

    # Neon colour palette dots at bottom
    palette_y = H - 18
    dot_x = PAD
    for dot_color in [RED, ORANGE, YELLOW, GREEN, CYAN, PURPLE]:
        p.append(f'<circle cx="{dot_x}" cy="{palette_y}" r="5" '
                 f'fill="{dot_color}" filter="url(#dotGlow)"/>')
        dot_x += 20

    p.append('</svg>')
    return "\n".join(p)


# ══════════════════════════════════════════════════════════════════
# ── README INJECTION ───────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
def update_readme():
    svg_block = (
        f"{README_MARKER_START}\n"
        f'<table align="center">\n'
        f'  <tr>\n'
        f'    <td valign="top" align="center">\n'
        f'      <img src="assets/terminal-card.svg" />\n'
        f'    </td>\n'
        f'    <td valign="top" align="center">\n'
        f'      <img src="assets/info-card.svg" />\n'
        f'    </td>\n'
        f'  </tr>\n'
        f'</table>\n\n'
        f'<div align="center">\n'
        f'  <img src="assets/github-contribution-animation.svg" />\n'
        f'</div>\n'
        f"{README_MARKER_END}"
    )

    try:
        content = README_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        content = ""

    if README_MARKER_START in content and README_MARKER_END in content:
        before = content[: content.index(README_MARKER_START)]
        after  = content[content.index(README_MARKER_END) + len(README_MARKER_END):]
        content = before + svg_block + after
    else:
        # Inject after the opening <br/> (after profile-views badge)
        br_tag = "<br/>"
        idx = content.find(br_tag)
        if idx != -1:
            insert_at = idx + len(br_tag)
            content = content[:insert_at] + "\n\n" + svg_block + "\n" + content[insert_at:]
        else:
            content = svg_block + "\n\n" + content

    README_PATH.write_text(content, encoding="utf-8")
    print("  ✓ README.md updated")


# ══════════════════════════════════════════════════════════════════
# ── MAIN ───────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
def main():
    print("⚡  Generating premium SVG assets for github.com/" + GH_USERNAME)

    # 1. Contribution graph
    print("  → Fetching contribution data …")
    grid       = fetch_contributions()
    contrib_svg = generate_contribution_svg(grid)
    out1 = ASSETS_DIR / "github-contribution-animation.svg"
    out1.write_text(contrib_svg, encoding="utf-8")
    print(f"  ✓ {out1.name}")

    # 2. Terminal card
    print("  → Generating ASCII avatar …")
    ascii_rows   = fetch_avatar_ascii(cols=46, rows=21)
    term_svg, _, term_h = generate_terminal_svg(ascii_rows)
    out2 = ASSETS_DIR / "terminal-card.svg"
    out2.write_text(term_svg, encoding="utf-8")
    print(f"  ✓ {out2.name}")

    # 3. Info card (matches terminal height)
    print("  → Generating info card …")
    info_svg = generate_info_svg(card_h=term_h)
    out3 = ASSETS_DIR / "info-card.svg"
    out3.write_text(info_svg, encoding="utf-8")
    print(f"  ✓ {out3.name}")

    # 4. Update README
    print("  → Injecting into README.md …")
    update_readme()

    print("\n✅  All done! Commit assets/ and README.md to see your new profile.")


if __name__ == "__main__":
    main()
