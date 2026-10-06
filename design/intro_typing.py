"""Generate Bluu's self-contained, three-phrase introduction.

The interaction is adapted, with the author's permission, from lora-sys/lora-sys
at 82c4333e88d2dc48d67194da588ce62a02235e70:
scripts/build_approved_profile.py:95-135 (v5 typing_svg), and
scripts/build_profile_v4.py:94-152 (v4's 24-second, three-phrase cycle).
Those sources use per-character CSS opacity and a moving, blinking cursor.
This is an interaction/design adaptation, not a verbatim source-code copy:
it uses the profile's outlined fonts, reusable glyphs and discrete SVG SMIL.
Only Bluu's own introduction appears. There are no font or runtime requests.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

import svgtext as ST


PHRASES = (
    "我是 Bluu，做 AI 应用与开发者工具。",
    "让问题、资料与执行，留在同一条研究线上。",
    "维护 ThreadCove / Clawtide，参与开源贡献。",
)
MOBILE_ROWS = (
    ("我是 Bluu，", "做 AI 应用与开发者工具。"),
    ("让问题、资料与执行，", "留在同一条研究线上。"),
    ("维护 ThreadCove / Clawtide，", "参与开源贡献。"),
)
PALETTES = {
    "dark": {"text": "#8EBDC8", "cursor": "#8EBDC8"},
    "light": {"text": "#365E73", "cursor": "#365E73"},
}
CYCLE = 24.0
SLOT = 8.0
TYPE_START = 0.25
TYPE_DURATION = 2.7
DELETE_START = 6.2
DELETE_DURATION = 1.15
ACTIVE_END = 7.75


def fmt(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".") or "0"


def animate(attribute: str, events: list[tuple[float, str]]) -> str:
    """One global clock avoids drift and keeps all phrase intervals disjoint."""
    assert events[0][0] == 0 and events[-1][0] == CYCLE
    assert all(a[0] < b[0] for a, b in zip(events, events[1:]))
    times = ";".join(fmt(time / CYCLE) for time, _ in events)
    values = ";".join(value for _, value in events)
    tag = "animateTransform" if attribute == "transform" else "animate"
    extra = ' type="translate"' if attribute == "transform" else ""
    return (f'<{tag} attributeName="{attribute}"{extra} dur="24s" '
            f'calcMode="discrete" repeatCount="indefinite" '
            f'keyTimes="{times}" values="{values}"/>')


def typing_svg(mode: str, mobile: bool = False, still: bool = False) -> str:
    palette = PALETTES[mode]
    width, height = (600, 150) if mobile else (900, 100)
    size = 32 if mobile else 30
    rows = MOBILE_ROWS if mobile else tuple((text,) for text in PHRASES)
    axes = {"wght": 600}
    glyphs: dict[tuple[int, int, float], tuple[str, str]] = {}
    body: list[str] = []

    def glyph(font, gid: int, scale: float) -> str:
        key = (id(font), gid, scale)
        if key not in glyphs:
            ident = f"g{len(glyphs)}"
            pen = SVGPathPen(None, ntos=lambda value: f"{value:.1f}".rstrip("0").rstrip("."))
            font.draw_glyph_with_pen(gid, TransformPen(pen, (scale, 0, 0, -scale, 0, 0)))
            glyphs[key] = ident, pen.getCommands()
        return glyphs[key][0]

    for phrase_index, phrase_rows in enumerate(rows):
        if still and phrase_index:
            break
        offset = phrase_index * SLOT
        count = sum(map(len, phrase_rows))
        assert "".join(phrase_rows) == PHRASES[phrase_index]
        layouts = []
        for row_index, text in enumerate(phrase_rows):
            shaped, advance = ST._layout(text, size, "plex", axes, 0)
            # These phrases contain no combining clusters or ligatures.
            assert len(shaped) == len(text), text
            x = (width - advance) / 2
            assert x >= 20, (text, x)
            y = (64 + row_index * 44) if mobile else 60
            layouts.append((text, shaped, x, y))

        start_x, start_y = layouts[0][2], layouts[0][3] - size * .82
        cursor_events = [(0.0, f"{fmt(start_x)} {fmt(start_y)}")]
        char_index = 0
        for text, shaped, x, y in layouts:
            for local_index, (font, gid, gx, gy, scale) in enumerate(shaped):
                reveal = offset + TYPE_START + (char_index + 1) * TYPE_DURATION / count
                erase = offset + DELETE_START + (count - 1 - char_index) * DELETE_DURATION / count
                ident = glyph(font, gid, scale)
                use = (f'<use href="#{ident}" x="{fmt(x + gx)}" y="{fmt(y - gy)}"'
                       f' opacity="{1 if phrase_index == 0 else 0}">')
                if not still:
                    use += animate("opacity", [(0.0, "0"), (reveal, "1"), (erase, "0"), (CYCLE, "0")])
                use += "</use>"
                body.append(use)
                right = x + ST.measure(text[:local_index + 1], size, "plex", axes)
                left = x + ST.measure(text[:local_index], size, "plex", axes)
                cursor_y = y - size * .82
                cursor_events.extend([
                    (reveal, f"{fmt(right + 4)} {fmt(cursor_y)}"),
                    (erase, f"{fmt(left + 4)} {fmt(cursor_y)}"),
                ])
                char_index += 1

        # Move the just-appended glyphs into this phrase's exclusive slot.
        phrase_glyphs = body[-count:]
        del body[-count:]
        group = (f'<g id="phrase-{phrase_index}" data-phrase="{escape(PHRASES[phrase_index], quote=True)}" '
                 f'fill="{palette["text"]}" opacity="{1 if phrase_index == 0 else 0}">')
        if not still:
            active = [(0.0, "1" if phrase_index == 0 else "0")]
            if phrase_index:
                active.append((offset, "1"))
            active.extend([(offset + ACTIVE_END, "0"), (CYCLE, "0")])
            group += animate("opacity", active)
        group += "".join(phrase_glyphs)
        if not still:
            cursor_events.sort(key=lambda event: event[0])
            cursor_events.append((CYCLE, cursor_events[-1][1]))
            group += ('<g class="typing-cursor">' + animate("transform", cursor_events)
                      + f'<rect width="2.3" height="{fmt(size * .92)}" rx=".5" fill="{palette["cursor"]}">'
                      + '<animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" '
                        'dur="1.1s" calcMode="discrete" repeatCount="indefinite"/>'
                      + '</rect></g>')
        body.append(group + "</g>")

    defs = "".join(f'<path id="{ident}" d="{path}"/>' for ident, path in glyphs.values())
    description = ("Bluu 的三段介绍：逐字显示，停顿，倒序删除，再进入下一段。每次只显示一段，24 秒循环。"
                   if not still else "Bluu 的介绍静态版本。")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">'
            f'<title id="title">{escape(" ".join(PHRASES))}</title>'
            f'<desc id="description">{description}</desc>'
            f'<defs>{defs}</defs>{"".join(body)}</svg>\n')


def make_typing_assets(assets: Path) -> None:
    for mode in PALETTES:
        for mobile in (False, True):
            for still in (False, True):
                filename = f'typing{"-mobile" if mobile else ""}-{mode}{"-still" if still else ""}.svg'
                (assets / filename).write_text(typing_svg(mode, mobile, still), encoding="utf-8")


if __name__ == "__main__":
    make_typing_assets(Path(__file__).resolve().parents[1] / "assets")
