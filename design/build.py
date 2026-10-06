#!/usr/bin/env python3
"""Generate Bluuok profile artwork.

    python3 design/build.py

The hero shows an edge dislocation gliding through a crystal one lattice step at a
time: the way metals deform, and the idea behind "Small steps every day."
Everything is outlined (no font requests) and animated with SMIL, which GitHub's
image proxy leaves intact. Each figure also gets a *-still.svg that the README's
<picture> serves under prefers-reduced-motion.

Fonts (OFL, from github.com/google/fonts, saved into design/fonts/, not committed):
  Archivo.ttf  <- ofl/archivo/Archivo[wdth,wght].ttf
  Plex.ttf     <- ofl/ibmplexsans/IBMPlexSans[wdth,wght].ttf
  NotoSC.ttf   <- ofl/notosanssc/NotoSansSC[wght].ttf
Requires: pip install uharfbuzz fonttools
"""

from __future__ import annotations

import math
from decimal import Decimal
from pathlib import Path

import svgtext as ST

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# Temper colours: the oxide tints steel takes on as it heats, straw to blue.
PALETTES = {
    "dark": {
        "ground": "#14202E",
        "plane": "#2E4054",
        "atom": "#5D7189",
        "text": "#E8ECF0",
        "muted": "#93A3B5",
        "straw": "#E3B75E",
        "bronze": "#C8783E",
        "purple": "#9366C4",
        "blue": "#5A8BE0",
        "glow": 0.55,
    },
    "light": {
        "ground": "#E9EDF1",
        "plane": "#BCC7D3",
        "atom": "#7F8FA1",
        "text": "#17222E",
        "muted": "#52606F",
        "straw": "#A67A12",
        "bronze": "#A45220",
        "purple": "#6E44A0",
        "blue": "#2D5FB8",
        "glow": 0.34,
    },
}


def fmt(v: float) -> str:
    s = f"{v:.1f}"
    return "0" if s in ("-0.0", "0.0") else s.rstrip("0").rstrip(".")


def pts_d(points) -> str:
    # Keep the original 0.1px positions exactly, but encode shorter deltas.
    # This changes serialization only: every keyframe and lattice point remains.
    coords = [(Decimal(fmt(x)), Decimal(fmt(y))) for x, y in points]
    absolute = "M" + " ".join(f"{fmt(x)} {fmt(y)}" for x, y in coords)
    first, *rest = coords
    deltas, previous = [], first
    for current in rest:
        deltas.append(f"{fmt(current[0]-previous[0])} {fmt(current[1]-previous[1])}")
        previous = current
    relative = f"M{fmt(first[0])} {fmt(first[1])}l" + " ".join(deltas)
    return min((absolute, relative), key=len)


# --------------------------------------------------------------------------- hero
#
# Square lattice, spacing A, slip plane at SVG y = YS. An infinite row of edge
# dislocations with period P = N*A: displacement u_x = b/2pi * arg sin(pi z / P),
# the periodic sum of the textbook theta term, plus a small ln|sin| term for u_y.
# The core hops one lattice step every STEP seconds. Because the field is
# periodic, the state one cycle later is the same picture with the top half slipped
# by exactly one lattice vector, so the loop is seamless.

W, H = 1280, 440
A = 40.0  # lattice spacing (= Burgers vector b)
N = 15  # columns per period
P = N * A
STEP = 1.0  # seconds per lattice step
T = N * STEP
DWELL = 0.58  # share of each step spent at rest
YS = 214.0  # slip plane
ROWS = 4  # rows on each side of the slip plane
KAPPA = 0.26  # u_y strength (textbook ~0.14, boosted to read at small size)
WIN = (676.0, 1240.0)  # visible lattice window
X0 = 716.0  # reference column / core start

# Keyframe times within one step: rest, end of rest, then samples of the hop.


_Q = [i / 6 for i in range(1, 6)]


def ease(q: float) -> float:
    return q * q * q * (q * (6 * q - 15) + 10)  # smootherstep: a snap, then a settle


def _stops():
    out = []  # (phase seconds, lattice steps travelled)
    for k in range(N):
        t0 = k * STEP
        out.append((t0, float(k)))
        out.append((t0 + DWELL * STEP, float(k)))
        for q in _Q:
            out.append((t0 + (DWELL + (1 - DWELL) * q) * STEP, k + ease(q)))
    out.append((T, float(N)))
    return out


STOPS = _stops()


def _wrap(v: float) -> float:
    return (v + math.pi) % (2 * math.pi) - math.pi


def field(xi: float, ym: float) -> tuple[float, float]:
    """(u_x, u_y) in math coordinates for an atom at offset xi from the core, height ym.

    theta is the continuous branch of arg sin(pi (xi + i ym) / P): it tends to
    pi/2 - a above the plane and a - pi/2 below, plus a bounded periodic part.
    """
    a, bb = math.pi * xi / P, math.pi * ym / P
    re, im = math.sin(a) * math.cosh(bb), math.cos(a) * math.sinh(bb)
    lin = (math.pi / 2 - a) if ym > 0 else (a - math.pi / 2)
    theta = lin + _wrap(math.atan2(im, re) - lin)
    far = math.log(math.cosh(bb) ** 2)
    ux = A / (2 * math.pi) * theta
    uy = -A / (2 * math.pi) * KAPPA * (math.log(re * re + im * im) - far)
    return ux, uy


def row_y(side: int, k: int) -> float:
    """Math y (up) of row k on side +1 (above) / -1 (below) the slip plane."""
    return side * (k + 0.5) * A


def drift(side: int) -> float:
    """Rigid slide per step that makes every track close after one cycle."""
    return -side * A / (2 * N)


def track(side: int, k: int, s: float, j: int = 0) -> tuple[float, float]:
    """SVG position of the atom in column j, row k, when the core has moved s steps."""
    ym = row_y(side, k)
    ux, uy = field((j - s) * A, ym)
    return X0 + j * A + ux + drift(side) * s, YS - (ym + uy)


def offset(side: int, j: int) -> float:
    """Column j replays column 0's track j steps late, shifted by this much."""
    return j * (A + drift(side))


# How the lattice is animated without one animation per atom:
#
# The picture after one step equals the picture before it, shifted right by
# (A + drift) with every column index moved by one. So each half of the crystal is
# one path per row (atoms drawn as markers on its vertices) plus one path holding
# every column. `d` animates through a single step and repeats; a discrete
# translate adds one shift per step and resets after N steps, where the loop
# closes exactly (see drift()).

J = range(-17, 16)  # enough columns to cover the window across all N shifts
SIGMAS = [0.0, DWELL] + [DWELL + (1 - DWELL) * q for q in _Q] + [1.0]
SIGMA_S = [0.0, 0.0] + [ease(q) for q in _Q] + [1.0]


def row_d(side, k, s):
    return pts_d([track(side, k, s, j) for j in J])


def cols_d(side, s):
    parts = []
    for j in J:
        pts = [track(side, k, s, j) for k in range(ROWS)]
        parts.append(pts_d(pts))
    return " ".join(parts)


def anim_d(fn, still: bool) -> str:
    """A path whose d runs through one step. fn(s) -> d."""
    if still:
        return f'<path d="{fn(0.0)}"/>'
    values = ";".join(fn(s) for s in SIGMA_S)
    times = ";".join(fmt(t / 1) if t in (0, 1) else f"{t:.3f}" for t in SIGMAS)
    return (
        f'<path d="{fn(0.0)}"><animate attributeName="d" dur="{fmt(STEP)}s" '
        f'repeatCount="indefinite" calcMode="linear" keyTimes="{times}" values="{values}"/></path>'
    )


def shifter(side: int, still: bool) -> str:
    if still:
        return ""
    step = A + drift(side)
    vals = ";".join(f"{fmt(i * step)} 0" for i in range(N))
    times = ";".join(f"{i / N:.4f}" for i in range(N))
    return (
        f'<animateTransform attributeName="transform" type="translate" dur="{fmt(T)}s" '
        f'repeatCount="indefinite" calcMode="discrete" keyTimes="{times}" values="{vals}"/>'
    )


def lattice(still: bool) -> tuple[str, str]:
    """(rows group, columns group) for both halves."""
    rows, cols = [], []
    s0 = STILL_AT if still else 0.0
    for side in (1, -1):
        r = "".join(anim_d(lambda s, k=k: row_d(side, k, s + s0), still) for k in range(ROWS))
        c = anim_d(lambda s: cols_d(side, s + s0), still)
        rows.append(f"<g>{shifter(side, still)}{r}</g>")
        cols.append(f"<g>{shifter(side, still)}{c}</g>")
    return "".join(rows), "".join(cols)


STILL_AT = 7.0  # reduced-motion frame: the core sits mid-window


def core_motion(still: bool) -> str:
    if still:
        return ""
    vals = ";".join(f"{fmt(s * A)} 0" for _, s in STOPS)
    times = ";".join(f"{t / T:.4f}" for t, _ in STOPS)
    return (
        f'<animateTransform attributeName="transform" type="translate" dur="{fmt(T)}s" '
        f'repeatCount="indefinite" calcMode="linear" keyTimes="{times}" values="{vals}"/>'
    )


TX = 72  # left text margin


def core_glyph(c) -> str:
    """The edge-dislocation symbol, drawn at the origin."""
    return (
        f'<circle r="15" fill="{c["bronze"]}" opacity="{c["glow"] * 0.45}" filter="url(#soft)"/>'
        f'<path d="M-11 9 H11 M0 9 V-11" stroke="{c["bronze"]}" stroke-width="4" '
        'stroke-linecap="round" fill="none"/>'
    )


def hero(mode: str, still: bool, mobile: bool = False) -> str:
    c = PALETTES[mode]
    rows, cols = lattice(still)
    wx0, wx1 = WIN
    top, bot = YS - ROWS * A - 6, YS + ROWS * A + 6

    name = ST.path("Bluuok", 40 if mobile else TX - 4, 144 if mobile else 194, 104 if mobile else 94, "archivo", {"wght": 820, "wdth": 108}, tracking=-2.5)
    role = ST.path("AI applications & agent workbenches", 44 if mobile else TX, 198 if mobile else 246, 27 if mobile else 26, "plex", {"wght": 420, "wdth": 100})
    motto = ST.path("From questions to working tools.", 44 if mobile else TX, 252 if mobile else 318, 27 if mobile else 26, "plex", {"wght": 560, "wdth": 100})
    cap = "One lattice step. Another careful iteration."
    capd = ST.path(cap, 320 if mobile else (wx0 + wx1) / 2, 620 if mobile else bot + 40, 23 if mobile else 20, "plex", {"wght": 400}, anchor="middle")

    heat = "".join(
        f'<g transform="translate({fmt(X0 + off + (STILL_AT * A if still else 0))} {fmt(YS)})"><g>{core_motion(still)}'
        f'<ellipse rx="{fmt(1.25 * A)}" ry="{fmt(2.9 * A)}" cy="-{fmt(2.1 * A)}" fill="url(#hg)"/></g></g>'
        for off in (0.0, -P)
    )
    cores = "".join(
        f'<g transform="translate({fmt(X0 + off + (STILL_AT * A if still else 0))} {fmt(YS)})"><g>{core_motion(still)}{core_glyph(c)}</g></g>'
        for off in (0.0, -P)
    )
    stops = (
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset="0.14" stop-color="#fff"/><stop offset="0.86" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/>'
    )
    # Temper colours as a thin rule under the name: straw -> bronze -> purple -> blue.
    temper = "".join(
        f'<rect x="{fmt((44 if mobile else TX) + i * 38)}" y="{282 if mobile else 344}" width="36" height="6" rx="1" fill="{c[k]}"/>'
        for i, k in enumerate(("straw", "bronze", "purple", "blue"))
    )
    title = "Bluuok. AI applications and agent workbenches. From questions to working tools."
    width, height = (640, 660) if mobile else (W, H)
    shift = ' transform="translate(-640 228)"' if mobile else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{title}">
<title>{title}</title>
<defs>
<g id="lattice-columns">{cols}</g>
<g id="lattice-rows">{rows}</g>
<filter id="soft" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="5"/></filter>
<linearGradient id="fade" x1="{wx0}" x2="{wx1}" gradientUnits="userSpaceOnUse">{stops}</linearGradient>
<mask id="win" maskUnits="userSpaceOnUse" x="{wx0}" y="{top}" width="{wx1-wx0}" height="{bot-top}"><rect x="{wx0}" y="{top}" width="{wx1 - wx0}" height="{bot - top}" fill="url(#fade)"/></mask>
<radialGradient id="hg"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="heat" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">{heat}</mask>
<marker id="atom" viewBox="-6 -6 12 12" markerWidth="12" markerHeight="12" markerUnits="userSpaceOnUse">
<circle r="4.6" fill="{c["atom"]}"/></marker>
</defs>
<rect width="{width}" height="{height}" rx="18" fill="{c["ground"]}"/>
<g{shift}><g mask="url(#win)">
<use href="#lattice-columns" fill="none" stroke="{c["plane"]}" stroke-width="1.6" stroke-linejoin="round"/>
<use href="#lattice-columns" mask="url(#heat)" fill="none" stroke="{c["bronze"]}" stroke-width="2.4" stroke-linejoin="round"/>
<use href="#lattice-rows" fill="none" stroke="{c["plane"]}" stroke-width="1.6" stroke-linejoin="round" marker-start="url(#atom)" marker-mid="url(#atom)" marker-end="url(#atom)"/>
<path d="M{wx0} {YS} H{wx1}" stroke="{c["straw"]}" stroke-width="1.6" stroke-dasharray="2 6" stroke-linecap="round"/>
{cores}
</g></g>
<g fill="{c["text"]}"><path d="{name}"/></g>
<g fill="{c["muted"]}"><path d="{role}"/></g>
<g fill="{c["text"]}"><path d="{motto}"/></g>
<g fill="{c["muted"]}"><path d="{capd}"/></g>
{temper}
</svg>
"""




def main():
    from projects import fig_threadcove, fig_clawtide
    from extras import make_extras
    from intro_typing import make_typing_assets
    ASSETS.mkdir(exist_ok=True)
    for name, fn in {"hero": hero, "threadcove": fig_threadcove, "clawtide": fig_clawtide}.items():
        for mode in PALETTES:
            for mobile in (False, True):
                for still in (False, True):
                    path = ASSETS / f"{name}{'-mobile' if mobile else ''}-{mode}{'-still' if still else ''}.svg"
                    path.write_text(fn(mode, still, mobile), encoding="utf-8")
                    print(f"{path.name}: {path.stat().st_size / 1024:.1f} KB")
    make_extras(ASSETS)
    make_typing_assets(ASSETS)

if __name__ == "__main__":
    main()
