#!/usr/bin/env python3
"""
Premium GitHub Profile README SVG Generator
Generates three cinematic, SMIL-animated SVG files:
  1. github-contribution-animation.svg  — diagonal-reveal contribution graph
  2. terminal-card.svg                  — code typing animation
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

# ══════════════════════════════════════════════════════════════════
# ── CONFIG ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
GH_USERNAME = os.getenv("GH_USERNAME", "ShivanshGarg007")
GH_TOKEN    = os.getenv("GH_TOKEN", "")

NAME      = "Shivansh Garg"
ROLE      = "Associate Software Engineer @ Lowe's"
EDUCATION = "Chitkara University (CGPA: 10.00)"
LOCATION  = "India"
PORTFOLIO = "shivanshgarg.vercel.app"
EMAIL     = "shivanshgarg007@gmail.com"

HIGHLIGHTS = [
    "Build with Bharat 3.0 — Winner",
    "Hack4Delhi 2026 — Top 30 / 4,500+",
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

# ══════════════════════════════════════════════════════════════════
# ── SVG 1: CONTRIBUTION GRAPH ──────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
def generate_contribution_svg(grid: list[list[int]]) -> str:
    CELL  = 12
    GAP   = 3
    STEP  = CELL + GAP
    COLS  = len(grid)
    ROWS  = 7
    MARGIN_L = 32
    MARGIN_T = 46

    grid_w = COLS * STEP - GAP
    W = grid_w + MARGIN_L + 24
    H = ROWS * STEP - GAP + MARGIN_T + 42

    p = []
    p.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')
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

    p.append(f'<rect width="{W}" height="{H}" fill="url(#cBg)" rx="14"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#glassSheen)" rx="14"/>')
    p.append(f'<rect width="{W}" height="{H}" fill="none" stroke="{BORDER2}" stroke-width="1" rx="14" opacity="0.7"/>')
    p.append(f'<rect x="0" y="0" width="{W}" height="3" fill="url(#accentH)" rx="14"/>')

    p.append(f'<text x="14" y="26" font-family="\'JetBrains Mono\',monospace" font-size="12" font-weight="600" fill="{TEXT}">Contributions</text>')
    p.append(f'<text x="{W - 12}" y="26" text-anchor="end" font-family="\'JetBrains Mono\',monospace" font-size="11" fill="{DIM}">@{GH_USERNAME}</text>')

    today = datetime.now()
    start_date = today - timedelta(weeks=52)
    month_abbr = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    prev_month = None
    for col in range(COLS):
        d = start_date + timedelta(weeks=col)
        if d.month != prev_month:
            x = MARGIN_L + col * STEP
            p.append(f'<text x="{x}" y="{MARGIN_T - 10}" font-family="\'JetBrains Mono\',monospace" font-size="9" fill="{DIM}">{month_abbr[d.month - 1]}</text>')
            prev_month = d.month

    days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    for row in range(ROWS):
        if row % 2 == 1:
            y = MARGIN_T + row * STEP + CELL
            p.append(f'<text x="{MARGIN_L - 5}" y="{y}" text-anchor="end" font-family="\'JetBrains Mono\',monospace" font-size="8" fill="{DIM}">{days[row]}</text>')

    for col in range(COLS):
        for row in range(ROWS):
            level = grid[col][row]
            color = CONTRIB_COLORS[level]
            x     = MARGIN_L + col * STEP
            y     = MARGIN_T + row * STEP
            delay = (col + (ROWS - 1 - row)) * 0.024
            filt = (' filter="url(#glow3)"' if level == 3 else ' filter="url(#glow4)"' if level == 4 else '')
            p.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"{filt} opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.28s" fill="freeze"/></rect>')
            if level > 0:
                p.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="white" opacity="0"><animate attributeName="opacity" values="0;0;0.85;0" keyTimes="0;0.01;0.25;1" begin="{delay:.3f}s" dur="0.55s" fill="freeze"/></rect>')

    lx = W - 148
    ly = H - 16
    p.append(f'<text x="{lx}" y="{ly}" font-family="\'JetBrains Mono\',monospace" font-size="9" fill="{DIM}">Less</text>')
    for i, c in enumerate(CONTRIB_COLORS):
        p.append(f'<rect x="{lx + 32 + i * 16}" y="{ly - 10}" width="12" height="12" rx="2" fill="{c}"/>')
    p.append(f'<text x="{lx + 32 + 5 * 16 + 4}" y="{ly}" font-family="\'JetBrains Mono\',monospace" font-size="9" fill="{DIM}">More</text>')

    p.append('</svg>')
    return "\n".join(p)

# ══════════════════════════════════════════════════════════════════
# ── SVG 2: ACTIVITY PANEL CARD ─────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
def generate_code_svg(card_h: int) -> str:
    """Git-log style 'What I'm Building' activity card — distinct from the neofetch info-card."""
    W  = 400
    H  = card_h
    FS = 11.5
    LH = 22
    PAD_H  = 18
    TITLE_H = 36
    PAD_V  = 14

    # Entries: (hash_color, hash, type_color, type, message)
    entries = [
        (CYAN,   "a3f9b2c", GREEN,  "feat",  "OpenLearning: voice mentor module"),
        (CYAN,   "d17c841", ORANGE, "wip",   "Distributed caching layer (Redis)"),
        (CYAN,   "88e2f34", PURPLE, "arch",  "Microservices split in progress"),
        (CYAN,   "c5a0912", GREEN,  "feat",  "Notora v2: real-time collab editor"),
        (CYAN,   "f9d3b77", YELLOW, "perf",  "Query optimisation — 3× speedup"),
        (CYAN,   "02e8c1a", RED,    "fix",   "Race condition in auth middleware"),
        (CYAN,   "b44f203", GREEN,  "feat",  "LLM eval pipeline (LangChain)"),
        (CYAN,   "7cb8d56", ORANGE, "wip",   "Portfolio v3 redesign"),
    ]

    p = []
    p.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')
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
  <linearGradient id="accentLine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="{GREEN}"/>
    <stop offset="50%"  stop-color="{CYAN}"/>
    <stop offset="100%" stop-color="{PURPLE}"/>
  </linearGradient>''')
    p.append('</defs>')

    # Window frame
    p.append(f'<rect width="{W}" height="{H}" fill="url(#winBg)" rx="12" stroke="{BORDER2}" stroke-width="1"/>')
    # Title bar
    p.append(f'<rect width="{W}" height="{TITLE_H}" fill="url(#titleBg)" rx="12"/>')
    p.append(f'<rect y="24" width="{W}" height="12" fill="url(#titleBg)"/>')
    p.append(f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="{BORDER}" stroke-width="1"/>')
    # Traffic lights
    DOT_Y = TITLE_H // 2
    p.append(f'<circle cx="16" cy="{DOT_Y}" r="6" fill="#ff5f57"/>')
    p.append(f'<circle cx="36" cy="{DOT_Y}" r="6" fill="#ffbd2e"/>')
    p.append(f'<circle cx="56" cy="{DOT_Y}" r="6" fill="#28c840"/>')
    # Title text
    p.append(f'<text x="{W // 2}" y="{DOT_Y + 4}" text-anchor="middle" font-family="\'JetBrains Mono\',monospace" font-size="12" fill="{DIM}">git log --oneline</text>')

    # Pulsing live dot + "ACTIVE" label
    p.append(
        f'<circle cx="{W - 56}" cy="{DOT_Y}" r="5" fill="{GREEN}" opacity="0.9">'
        f'<animate attributeName="opacity" values="0.9;0.2;0.9" dur="2s" repeatCount="indefinite"/>'
        f'</circle>'
        f'<text x="{W - 47}" y="{DOT_Y + 4}" font-family="\'JetBrains Mono\',monospace" font-size="10" fill="{GREEN}">LIVE</text>'
    )

    # Accent top bar
    p.append(f'<rect x="0" y="0" width="{W}" height="3" fill="url(#accentLine)" rx="12"/>')

    # Log entries with staggered fade-in
    y = TITLE_H + PAD_V + LH
    for i, (hc, sha, tc, typ, msg) in enumerate(entries):
        delay = 0.15 + i * 0.1
        safe_msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        p.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.2s" fill="freeze"/>'
            # hash
            f'<text x="{PAD_H}" y="{y}" font-family="\'JetBrains Mono\',monospace" font-size="{FS}" fill="{hc}">{sha}</text>'
            # type badge background
            f'<rect x="{PAD_H + 62}" y="{y - 13}" width="36" height="15" rx="3" fill="{tc}" opacity="0.18"/>'
            f'<text x="{PAD_H + 80}" y="{y}" text-anchor="middle" font-family="\'JetBrains Mono\',monospace" font-size="{FS - 1}" fill="{tc}">{typ}</text>'
            # message
            f'<text x="{PAD_H + 104}" y="{y}" font-family="\'JetBrains Mono\',monospace" font-size="{FS}" fill="{TEXT}">{safe_msg}</text>'
            f'</g>'
        )
        y += LH

    # Bottom separator + footer
    footer_y = H - 20
    p.append(f'<line x1="{PAD_H}" y1="{footer_y - 10}" x2="{W - PAD_H}" y2="{footer_y - 10}" stroke="{BORDER}" stroke-width="1" opacity="0.5"/>')
    p.append(f'<text x="{PAD_H}" y="{footer_y}" font-family="\'JetBrains Mono\',monospace" font-size="10" fill="{DIM}">github.com/{GH_USERNAME}</text>')
    p.append(f'<text x="{W - PAD_H}" y="{footer_y}" text-anchor="end" font-family="\'JetBrains Mono\',monospace" font-size="10" fill="{DIM}">8 recent commits</text>')

    p.append('</svg>')
    return "\n".join(p), W, H

# ══════════════════════════════════════════════════════════════════
# ── SVG 3: INFO CARD ───────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════
def generate_info_svg(card_h: int) -> str:
    W   = 380
    H   = card_h
    FS  = 12.5
    LH  = 22
    PAD = 20

    rows: list[tuple[str, str, str, bool]] = [
        ("",      NAME,                           PURPLE, True),
        ("",      "─" * 21,                      BORDER2, False),
        ("Role",  ROLE,                           GREEN,  False),
        ("Edu",   EDUCATION,                      ORANGE, False),
        ("Focus", "Systems & Full-Stack",         TEXT,   False),
        ("",      "",                             DIM,    False),
        ("Langs", "Python · TS · Java · C++",     CYAN,   False),
        ("Tech",  "React · Node · AWS · SQL",     YELLOW, False),
        ("",    "",                        DIM,    False),
        ("Wins","",                        ORANGE, True),
    ]
    for h in HIGHLIGHTS:
        rows.append(("", f"  {h}", TEXT, False))
    rows += [
        ("",    "",                        DIM,    False),
        ("Web",  PORTFOLIO,                CYAN,   False),
    ]

    p = []
    p.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')
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

    p.append(f'<rect width="{W}" height="{H}" fill="url(#icBg)" rx="12" stroke="{BORDER2}" stroke-width="1"/>')
    p.append(f'<rect x="0" y="0" width="{W}" height="3" fill="url(#accentV)" rx="12"/>')

    y = PAD + int(LH) + 8
    for idx, (key, val, color, bold) in enumerate(rows):
        delay = idx * 0.06
        fw    = "700" if bold else "400"
        fsize = FS + 1.5 if (bold and not key) else FS
        safe_key = key.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        safe_val = val.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

        anim = (
            f'<animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="{delay:.3f}s" dur="0.22s" fill="freeze"/>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.22s" fill="freeze"/>'
        )

        if key:
            p.append(
                f'<g transform="translate(0,10)" opacity="0">{anim}'
                f'<text x="{PAD}" y="{y}" font-family="\'JetBrains Mono\',monospace" font-size="{fsize}" font-weight="{fw}">'
                f'<tspan fill="{ORANGE}">{safe_key}</tspan>'
                f'<tspan fill="{DIM}">: </tspan>'
                f'<tspan fill="{color}">{safe_val}</tspan>'
                f'</text></g>'
            )
        else:
            p.append(
                f'<g transform="translate(0,10)" opacity="0">{anim}'
                f'<text x="{PAD}" y="{y}" font-family="\'JetBrains Mono\',monospace" font-size="{fsize}" font-weight="{fw}" fill="{color}" xml:space="preserve">{safe_val}</text></g>'
            )
        y += int(LH)

    palette_y = H - 20
    dot_x = PAD
    for dot_color in [RED, ORANGE, YELLOW, GREEN, CYAN, PURPLE]:
        p.append(f'<circle cx="{dot_x}" cy="{palette_y}" r="5" fill="{dot_color}" filter="url(#dotGlow)"/>')
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
        f'      <img src="assets/info-card.svg" />\n'
        f'    </td>\n'
        f'    <td valign="top" align="center">\n'
        f'      <img src="assets/terminal-card.svg" />\n'
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
        br_tag = "<br/>"
        idx = content.find(br_tag)
        if idx != -1:
            insert_at = idx + len(br_tag)
            content = content[:insert_at] + "\n\n" + svg_block + "\n" + content[insert_at:]
        else:
            content = svg_block + "\n\n" + content

    README_PATH.write_text(content, encoding="utf-8")
    print("  ✓ README.md updated")

def main():
    print("⚡  Generating premium SVG assets for github.com/" + GH_USERNAME)
    grid = fetch_contributions()
    out1 = ASSETS_DIR / "github-contribution-animation.svg"
    out1.write_text(generate_contribution_svg(grid), encoding="utf-8")
    print(f"  ✓ {out1.name}")

    card_h = 320

    term_svg, _, _ = generate_code_svg(card_h=card_h)
    out2 = ASSETS_DIR / "terminal-card.svg"
    out2.write_text(term_svg, encoding="utf-8")
    print(f"  ✓ {out2.name}")

    info_svg = generate_info_svg(card_h=card_h)
    out3 = ASSETS_DIR / "info-card.svg"
    out3.write_text(info_svg, encoding="utf-8")
    print(f"  ✓ {out3.name}")

    update_readme()

if __name__ == "__main__":
    main()
