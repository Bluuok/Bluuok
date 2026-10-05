"""Project workflow figures for Bluuok's GitHub profile.

These are architecture illustrations using synthetic example text, not recordings.
The visual system and SMIL helpers follow sclfcz's authorized profile reference;
project content and layouts are specific to ThreadCove and Clawtide. Text is
outlined by svgtext so the figures do not need network fonts on GitHub.

Public interface: fig_threadcove(mode, still, mobile=False) and
fig_clawtide(mode, still, mobile=False). Generation is owned by design/build.py.
"""

from __future__ import annotations

from html import escape

import svgtext as ST


PALETTES = {
    "dark": {
        "ground": "#14202E", "plane": "#2E4054", "atom": "#5D7189",
        "text": "#E8ECF0", "muted": "#93A3B5", "straw": "#E3B75E",
        "bronze": "#C8783E", "purple": "#9366C4", "blue": "#5A8BE0",
    },
    "light": {
        "ground": "#E9EDF1", "plane": "#BCC7D3", "atom": "#7F8FA1",
        "text": "#17222E", "muted": "#52606F", "straw": "#A67A12",
        "bronze": "#A45220", "purple": "#6E44A0", "blue": "#2D5FB8",
    },
}


def fmt(v: float) -> str:
    value = f"{v:.1f}"
    return "0" if value in ("-0.0", "0.0") else value.rstrip("0").rstrip(".")


def text(label, x, y, size, c, key="text", weight=450, anchor="start", font="plex"):
    axes = {"wght": weight}
    if font == "archivo":
        axes["wdth"] = 104
    glyphs = ST.path(label, x, y, size, font, axes, anchor=anchor)
    return f'<path fill="{c[key]}" d="{glyphs}"/>'


def disc(attr: str, loop: float, initial: str, changes) -> str:
    """Discrete SMIL timeline with a well-defined frame at t=0."""
    normalized = []
    for moment, value in changes:
        if moment <= 0:
            initial = value
        elif moment < loop:
            normalized.append((moment, value))
    normalized.sort(key=lambda change: change[0])
    times = ";".join(["0"] + [f"{t / loop:.4f}" for t, _ in normalized])
    values = ";".join([initial] + [value for _, value in normalized])
    return (
        f'<animate attributeName="{attr}" dur="{fmt(loop)}s" '
        f'repeatCount="indefinite" calcMode="discrete" '
        f'keyTimes="{times}" values="{values}"/>'
    )


def travel(path_id: str, loop: float, start: float, finish: float, reverse=False) -> str:
    times = f"0;{start / loop:.4f};{finish / loop:.4f};1"
    points = "1;1;0;0" if reverse else "0;0;1;1"
    return (
        f'<animateMotion dur="{fmt(loop)}s" repeatCount="indefinite" '
        f'calcMode="linear" keyTimes="{times}" keyPoints="{points}">'
        f'<mpath href="#{path_id}"/></animateMotion>'
    )


def message(path_id, c, colour, loop, start, finish, reverse=False):
    show = disc("opacity", loop, "0", [(start, "1"), (finish, "0")])
    return (
        f'<circle r="5" fill="{c[colour]}" opacity="0">'
        f'{show}{travel(path_id, loop, start, finish, reverse)}</circle>'
    )


def link(path_id, d, c, colour="plane", dashed=False, arrow=False, width=1.8):
    dash = ' stroke-dasharray="5 6"' if dashed else ""
    marker = f' marker-end="url(#arrow-{colour})"' if arrow else ""
    return (
        f'<path id="{path_id}" d="{d}" fill="none" stroke="{c[colour]}" '
        f'stroke-width="{width}" stroke-linecap="round"{dash}{marker}/>'
    )


def frame(w, h, c, title, description, body):
    markers = "".join(
        f'<marker id="arrow-{key}" viewBox="0 0 10 10" refX="8" refY="5" '
        f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        f'<path d="M1 1 L8 5 L1 9" fill="none" stroke="{c[key]}" '
        'stroke-width="1.8" stroke-linejoin="round"/></marker>'
        for key in ("plane", "muted", "straw", "blue")
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-labelledby="title description">'
        f'<title id="title">{escape(title)}</title>'
        f'<desc id="description">{escape(description)}</desc><defs>{markers}</defs>'
        f'<rect width="{w}" height="{h}" rx="14" fill="{c["ground"]}"/>'
        f'{body}</svg>\n'
    )


def panel(x, y, w, h, c, colour="plane", animation="", dashed=False):
    dash = ' stroke-dasharray="5 6"' if dashed else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="11" '
        f'fill="{c["ground"]}" stroke="{c[colour]}" stroke-width="1.8"{dash}>'
        f'{animation}</rect>'
    )


def _active_border(c, still, loop, start, finish, base="plane"):
    if still:
        return ""
    initial = c["straw"] if start == 0 else c[base]
    return disc("stroke", loop, initial, [(start, c["straw"]), (finish, c[base])])


def _thread_card(x, y, w, h, index, label, title, lines, c, still, mobile):
    step = index * 3.0
    base = "blue" if index == 3 else "plane"
    active = _active_border(c, still, 12, step, step + 2.8, base)
    parts = [panel(x, y, w, h, c, base, active)]
    if mobile:
        size, head, top, baselines = 19, 22, y + 29, (y + 87, y + 114)
        title_y = y + 60
    else:
        size, head, top, baselines = 15.5, 19, y + 24, (y + 86, y + 110)
        title_y = y + 56
    parts.append(text(f"0{index + 1} / {label}", x + 16, top, 12.5 if mobile else 11.5,
                      c, "muted", 550))
    parts.append(text(title, x + 16, title_y, head, c, weight=600))
    for line, baseline in zip(lines, baselines):
        parts.append(text(line, x + 16, baseline, size, c, "muted", 420))
    # An archive mark makes the last card clear even without animation.
    if index == 3:
        tick = (
            f'<path d="M{fmt(x + w - 32)} {fmt(y + 19)} '
            f'l4 4 l7 -8" fill="none" stroke="{c["blue"]}" stroke-width="2.3" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
        )
        parts.append(tick)
    return "".join(parts)


def fig_threadcove(mode: str, still: bool, mobile: bool = False) -> str:
    """Question → retrieval/Pi subtasks → dialogue → a current research archive."""
    c = PALETTES[mode]
    w, h = (600, 560) if mobile else (900, 360)
    title = "ThreadCove — personal AI research workspace"
    description = (
        "Workflow illustration with a synthetic question, Compare agent toolchains. "
        "Question, source retrieval and Pi subtask collaboration, continuous dialogue, "
        "and an independent archive for the current research. "
        "Pi, DeepSeek and Claude have different tools and collaboration capabilities. "
        "This is not a screen recording."
    )
    parts = [text("ThreadCove", 32, 45, 28 if mobile else 26, c,
                  weight=720, font="archivo")]
    parts.append(text("个人 AI 研究工作台", 32, 74, 18 if mobile else 16, c, "muted"))
    if not mobile:
        parts.append(text("Workflow illustration", 868, 44, 13, c, "muted", anchor="end"))
    cards = [
        ("QUESTION", "提出问题", ("Compare agent", "toolchains")),
        ("RETRIEVE", "资料检索", ("检索与核对", "Pi · 子任务协作")),
        ("DIALOGUE", "连续对话", ("DeepSeek / Claude", "引擎能力有差异")),
        ("ARCHIVE", "研究档案", ("Evidence & notes", "当前研究独立归档")),
    ]
    if mobile:
        # Clockwise numbering keeps the mobile view large and legible.
        boxes = [(30, 120, 250, 152), (320, 120, 250, 152),
                 (320, 330, 250, 152), (30, 330, 250, 152)]
        routes = ["M280 196 H314", "M445 272 V324", "M320 406 H286"]
        parts.append(text("01 → 02 → 03 → 04", 568, 74, 14, c, "muted", anchor="end"))
    else:
        boxes = [(36 + i * 216, 121, 180, 144) for i in range(4)]
        routes = [f"M{216 + i * 216} 193 H{246 + i * 216}" for i in range(3)]
    for i, route in enumerate(routes):
        parts.append(link(f"tc-step-{i}", route, c, "muted", arrow=True))
    for i, ((label, heading, lines), (x, y, cw, ch)) in enumerate(zip(cards, boxes)):
        parts.append(_thread_card(x, y, cw, ch, i, label, heading, lines, c, still, mobile))
    if not still:
        for i in range(3):
            parts.append(message(f"tc-step-{i}", c, "straw", 12,
                                 i * 3 + 0.9, i * 3 + 2.1))
    if mobile:
        parts.append(text("Desktop + Web · 连续会话与独立研究档案", 32, 520, 17, c))
        parts.append(text("合成示例 · 工作流示意 · 各引擎能力有差异", 32, 546, 14, c, "muted"))
    else:
        parts.append(text("Desktop + Web · 连续会话与独立研究档案", 36, 310, 17, c))
        parts.append(text("合成示例 · 工作流示意 · 各引擎的工具与协作能力不同", 36, 337, 13.5,
                          c, "muted"))
    return frame(w, h, c, title, description, "".join(parts))


def _hub(x, y, w, h, c, mobile=False):
    return "".join([
        panel(x, y, w, h, c, "straw"),
        text("Clawtide", x + w / 2, y + (36 if mobile else 34), 28 if mobile else 26,
             c, weight=720, anchor="middle", font="archivo"),
        text("角色 · 独立工作区", x + w / 2, y + (62 if mobile else 59),
             17 if mobile else 15, c, "muted", anchor="middle"),
        text("连续会话", x + w / 2, y + (82 if mobile else 79),
             15 if mobile else 14, c, "muted", anchor="middle"),
    ])


def _output(x, y, w, h, label, sublabel, c, mobile=False):
    return "".join([
        panel(x, y, w, h, c),
        text(label, x + w / 2, y + 28, 20 if mobile else 18,
             c, weight=580, anchor="middle"),
        text(sublabel, x + w / 2, y + 50, 15 if mobile else 13.5,
             c, "muted", anchor="middle"),
    ])


def _claw_desktop(c, still):
    parts = []
    cy = 200
    for i, label in enumerate(CLAW_CHANNELS):
        y = 111 + i * 39
        route = f"M166 {y} C214 {y} 214 {cy} 247 {cy}"
        parts.append(link(f"ct-in-{i}", route, c, "straw"))
        parts.append(f'<circle cx="166" cy="{y}" r="3.5" fill="{c["straw"]}"/>')
        parts.append(_channel_label(label, 151, y + 6, 17, i, c, still, "end"))
    parts.append(link("ct-adapter-runtime", "M419 200 H459", c, "straw", arrow=True))
    parts.append(_adapter(247, 156, 172, 88, c))
    outputs = [(735, 111, 137, 70, "会话回复", "回到当前入口"),
               (735, 237, 137, 70, "执行记录", "结果与错误可追溯")]
    for j, (x, y, ow, oh, label, sublabel) in enumerate(outputs):
        oy = y + oh / 2
        route = f"M685 {cy} C712 {cy} 709 {oy} {x} {oy}"
        parts.append(link(f"ct-out-{j}", route, c, "blue", arrow=True))
        parts.append(_output(x, y, ow, oh, label, sublabel, c))
    parts.append(_hub(465, 156, 220, 88, c))
    parts.append(text("计划任务经同一 Runtime 执行", 247, 291, 14.5, c, "muted"))
    parts.append(text("六种 IM · 渠道适配层 · 流程示意，非屏幕录制", 247, 324, 14,
                      c, "muted"))
    if not still:
        parts.append(_claw_messages(c, "ct"))
    return "".join(parts)


def _claw_mobile(c, still):
    parts = []
    for i, label in enumerate(CLAW_CHANNELS):
        y = 119 + i * 33
        route = f"M173 {y} C263 {y} 267 201 340 201"
        parts.append(link(f"ct-mobile-in-{i}", route, c, "straw"))
        parts.append(f'<circle cx="173" cy="{y}" r="3.5" fill="{c["straw"]}"/>')
        parts.append(_channel_label(label, 158, y + 7, 20, i, c, still, "end"))
    parts.append(link("ct-mobile-adapter-runtime", "M456 242 C456 300 300 285 300 341",
                      c, "straw", arrow=True))
    parts.append(_adapter(340, 160, 232, 82, c, mobile=True))
    parts.append(text("六种 IM · 同一工作区", 30, 324, 16, c, "muted"))
    parts.append(link("ct-mobile-out-0", "M248 436 C248 450 154 450 154 467", c, "blue", arrow=True))
    parts.append(link("ct-mobile-out-1", "M352 436 C352 450 446 450 446 467", c, "blue", arrow=True))
    parts.append(_hub(140, 342, 320, 94, c, mobile=True))
    parts.append(_output(28, 467, 252, 62, "会话回复", "回到当前入口", c, mobile=True))
    parts.append(_output(320, 467, 252, 62, "执行记录", "结果与错误可追溯", c, mobile=True))
    parts.append(text("计划任务经同一 Runtime 执行 · 流程示意，非屏录", 30, 552, 14,
                      c, "muted"))
    if not still:
        parts.append(_claw_messages(c, "ct-mobile"))
    return "".join(parts)


CLAW_CHANNELS = ("Telegram", "Feishu", "QQ", "DingTalk", "WeChat", "Discord")


def _channel_label(label, x, y, size, index, c, still, anchor):
    glyph = ST.path(label, x, y, size, "plex", {"wght": 480}, anchor=anchor)
    active = "" if still else disc("fill", 12, c["text"],
                                  [(index * 2, c["straw"]), (index * 2 + 1.95, c["text"])])
    return f'<path fill="{c["text"]}" d="{glyph}">{active}</path>'


def _adapter(x, y, w, h, c, mobile=False):
    return "".join([
        panel(x, y, w, h, c, "straw"),
        text("渠道适配层", x + w / 2, y + 35, 21 if mobile else 18,
             c, weight=600, anchor="middle"),
        text("channel adapters", x + w / 2, y + 62, 17 if mobile else 14,
             c, "muted", anchor="middle"),
    ])


def _claw_messages(c, prefix):
    parts = []
    for i in range(len(CLAW_CHANNELS)):
        start = i * 2.0
        parts.append(message(f"{prefix}-in-{i}", c, "straw", 12, start + 0.05, start + 0.6))
        parts.append(message(f"{prefix}-adapter-runtime", c, "straw", 12, start + 0.7, start + 1.05))
        parts.append(message(f"{prefix}-out-{i % 2}", c, "blue", 12, start + 1.15, start + 1.55))
        parts.append(message(f"{prefix}-adapter-runtime", c, "blue", 12, start + 1.6, start + 1.72,
                             reverse=True))
        parts.append(message(f"{prefix}-in-{i}", c, "blue", 12, start + 1.76, start + 1.94,
                             reverse=True))
    return "".join(parts)


def fig_clawtide(mode: str, still: bool, mobile: bool = False) -> str:
    """Six IM channels share adapters and the Clawtide runtime."""
    c = PALETTES[mode]
    w, h = (600, 560) if mobile else (900, 360)
    title = "Clawtide — self-hosted AI digital employee workspace"
    description = (
        "Architecture illustration, not a screen recording. Telegram, Feishu, QQ, DingTalk, "
        "WeChat and Discord share a channel adapter layer leading to the Clawtide runtime. "
        "Clawtide has roles, independent workspaces, continuous sessions, conversation replies "
        "and execution records. Scheduled tasks execute through the same runtime."
    )
    parts = [text("Clawtide", 32, 43, 28 if mobile else 26, c,
                  weight=720, font="archivo")]
    parts.append(text("自托管 AI 数字员工工作台", 32, 72, 18 if mobile else 16, c, "muted"))
    if mobile:
        parts.append(_claw_mobile(c, still))
    else:
        parts.append(text("6 IM · 1 workspace", 868, 43, 14, c, "muted", anchor="end"))
        parts.append(_claw_desktop(c, still))
    return frame(w, h, c, title, description, "".join(parts))
