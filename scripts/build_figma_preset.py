#!/usr/bin/env python3
"""Build presets/com.figma.Desktop.json from scripts/data/pie-menu-figma.md."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "scripts" / "data" / "pie-menu-figma.md"
OUT_JSON = ROOT / "presets" / "com.figma.Desktop.json"
ICON_DIR = ROOT / "presets" / "icons" / "com.figma.Desktop"

# (id, en title, zh title, row count) — counts must sum to rows in pie-menu-figma.md (99 total;
# Pie Menu HTML inserts a markdown separator after the first Tools row).
CATEGORY_SPECS = [
    ("remote.figma.tools", "Tools", "工具", 11),
    ("remote.figma.components", "Components", "组件", 4),
    ("remote.figma.arrange", "Arrange", "排列", 7),
    ("remote.figma.transform", "Transform", "变换", 7),
    ("remote.figma.edit", "Edit", "编辑", 9),
    ("remote.figma.selection", "Selection", "选择", 12),
    ("remote.figma.shape", "Shape", "形状", 11),
    ("remote.figma.text", "Text", "文本", 13),
    ("remote.figma.zoom", "Zoom", "缩放", 11),
    ("remote.figma.view", "View", "视图", 11),
    ("remote.figma.essential", "Essential", "常用", 3),
]

# Carbon modifier flags (decimal)
CMD = 256
SHIFT = 512
OPT = 2048
CTRL = 4096

# macOS kVK virtual key code -> primary keycap label (US keyboard)
KEYCODE_DISPLAY: dict[int, str] = {
    0: "A",
    1: "S",
    2: "D",
    3: "F",
    4: "H",
    5: "G",
    6: "Z",
    7: "X",
    8: "C",
    9: "V",
    11: "B",
    12: "Q",
    13: "W",
    14: "E",
    15: "R",
    16: "Y",
    17: "T",
    18: "1",
    19: "2",
    23: "5",
    24: "+",
    25: "9",
    27: "-",
    28: "8",
    29: "0",
    30: "]",
    31: "O",
    32: "U",
    33: "[",
    34: "I",
    35: "P",
    37: "L",
    38: "J",
    39: "'",
    40: "K",
    42: "\\",
    43: "<",
    44: "/",
    45: "N",
    46: "M",
    48: "⇥",
    53: "⎋",
    55: "⌘",
    76: "↵",
    115: "Home",
    116: "PgUp",
    119: "End",
    121: "PgDn",
}

# zh-Hans: UI-oriented names (Figma 简体界面常用说法；帮助中心该篇无完整中文对照，故为人工校对用语)
ZH_TITLE: dict[str, str] = {
    "Slice Tool": "切片工具",
    "Add/Show Comments": "添加/显示评论",
    "Arrow Tool": "箭头工具",
    "Line Tool": "直线工具",
    "Ellipse Tool": "椭圆工具",
    "Rectangle Tool": "矩形工具",
    "Text Tool": "文字工具",
    "Pencil Tool": "铅笔工具",
    "Pen Tool": "钢笔工具",
    "Frame Tool": "画框工具",
    "Move Tool": "移动工具",
    "Detach Instance": "分离实例",
    "Create Component": "创建组件",
    "Team Library": "团队组件库",
    "Show Assets": "显示资源",
    "Remove Auto Layout": "移除自动布局",
    "Add Auto Layout": "添加自动布局",
    "Tidy Up": "整理",
    "Send to Back": "置于底层",
    "Bring to Front": "置于顶层",
    "Send Backward": "后移一层",
    "Bring Forward": "前移一层",
    "Set Opacity to 100%": "不透明度 100%",
    "Set Opacity to 50%": "不透明度 50%",
    "Set Opacity to 10%": "不透明度 10%",
    "Place Image": "放置图片",
    "Use as Mask": "用作蒙版",
    "Flip Vertical": "垂直翻转",
    "Flip Horizontal": "水平翻转",
    "Paste Properties": "粘贴属性",
    "Copy Properties": "复制属性",
    "Export": "导出",
    "Rename Selection": "重命名所选",
    "Duplicate": "创建副本",
    "Paste Over Selection": "粘贴至所选图层",
    "Paste": "粘贴",
    "Cut": "剪切",
    "Copy": "复制",
    "Lock/Unlock Selection": "锁定/解锁所选",
    "Show/Hide Selection": "显示/隐藏所选",
    "Frame Selection": "添加画框",
    "Ungroup Selection": "取消编组",
    "Group Selection": "编组",
    "Select Previous Sibling": "选择上一个同级图层",
    "Select Next Sibling": "选择下一个同级图层",
    "Select Parents": "选择父级",
    "Select Child": "选择子级",
    "Select None": "取消选择",
    "Select Inverse": "反选",
    "Select All": "全选",
    "Smooth Join Selection (After selecting points)": "平滑连接（选中锚点后）",
    "Join Selection (After selecting points)": "连接（选中锚点后）",
    "Flatten Selection": "拼合所选",
    "Outline Stroke": "轮廓化描边",
    "Swap Fill Stroke": "交换填充和描边",
    "Remove Stroke": "移除描边",
    "Remove Fill": "移除填充",
    "Bend Tool": "弯折工具",
    "Paint Bucket (While editing a shape)": "油漆桶（编辑形状时）",
    "Pencil": "铅笔",
    "Pen": "钢笔",
    "Adjust Line Height": "调整行高",
    "Adjust Letter Spacing": "调整字间距",
    "Adjust Font Weight": "调整字重",
    "Adjust Font Size": "调整字号",
    "Text Align Justified": "两端对齐",
    "Text Align Right": "右对齐",
    "Text Align Center": "居中对齐",
    "Text Align Left": "左对齐",
    "Create Link": "创建链接",
    "Paste Match Style": "粘贴并匹配样式",
    "Underline": "下划线",
    "Italic": "斜体",
    "Bold": "粗体",
    "Find Next Frame": "查找下一画框",
    "Find Previous Frame": "查找上一画框",
    "Next Page": "下一页",
    "Previous Page": "上一页",
    "Zoom to Next Frame": "缩放至下一画框",
    "Zoom to Previous Frame": "缩放至上一画框",
    "Zoom to Selection": "缩放至所选",
    "Zoom to Fit": "缩放至合适大小",
    "Zoom to 100%": "缩放至 100%",
    "Zoom Out": "缩小",
    "Zoom In": "放大",
    "Open Code Panel": "打开代码面板",
    "Open Prototype Panel": "打开原型面板",
    "Open Design Panel": "打开设计面板",
    "Open Assets Panel": "打开资源面板",
    "Open Layers Panel": "打开图层面板",
    "Pixel Grid": "像素网格",
    "Layout Grids": "布局网格",
    "Pixel Preview": "像素预览",
    "Outlines": "轮廓",
    "Rulers": "标尺",
    "Multiplayer Cursors": "多人光标",
    "Search": "搜索",
    "Pick Color": "拾取颜色",
    "Show/Hide UI": "显示/隐藏界面",
}

# Space before "[Add..." avoids ambiguity with ⌘ + [ ; URL may contain ")" in query (greedy .* to final ") |").
ROW_RE = re.compile(
    r"^\| (?P<label>[^|]+) \| (?P<shortcut>.+?) \[Add to Pie Menu\]\((?P<url>.*)\) \|$"
)


def carbon_modifiers(modifiers_param: str) -> int:
    s = unquote(modifiers_param or "").lower()
    m = 0
    if "command" in s:
        m |= CMD
    if "shift" in s:
        m |= SHIFT
    if "option" in s:
        m |= OPT
    if "control" in s:
        m |= CTRL
    return m


def parse_row(line: str) -> tuple[str, dict[str, str]] | None:
    m = ROW_RE.match(line.strip())
    if not m:
        return None
    label = m.group("label").strip()
    url = m.group("url")
    q = parse_qs(urlparse(url).query)
    desc = unquote(q["description"][0])
    key_code = int(q["key_code"][0])
    mods = q.get("modifiers", [""])[0]
    icon = q.get("icon", [None])[0]
    return label, {"description": desc, "key_code": key_code, "modifiers": mods, "icon": icon}


def slug_id(description: str) -> str:
    s = description.lower().replace("/", "-").replace("(", "").replace(")", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return "remote.figma." + s.strip("-")


def placeholder_svg(name: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        f'viewBox="0 0 24 24" role="img"><title>{name}</title>'
        r'<rect width="24" height="24" rx="5" fill="none" stroke="currentColor" '
        r'stroke-width="1.5" opacity="0.35"/></svg>\n'
    )


def main() -> int:
    text = DATA_FILE.read_text(encoding="utf-8")
    rows: list[tuple[str, dict[str, str]]] = []
    for line in text.splitlines():
        parsed = parse_row(line)
        if parsed:
            rows.append(parsed)

    expected = sum(spec[3] for spec in CATEGORY_SPECS)
    if len(rows) != expected:
        print(f"Expected {expected} rows, got {len(rows)}", file=sys.stderr)
        return 1

    icons_needed: set[str] = set()
    categories_out: list[dict] = []
    offset = 0
    for cat_id, en_title, zh_title, count in CATEGORY_SPECS:
        chunk = rows[offset : offset + count]
        offset += count
        items: list[dict] = []
        for _label, data in chunk:
            desc = data["description"]
            kc = data["key_code"]
            cm = carbon_modifiers(data["modifiers"])
            display = KEYCODE_DISPLAY.get(kc, str(kc))
            item_id = slug_id(desc)
            icon_slug = data["icon"]
            icon_path: str | None
            if icon_slug:
                icons_needed.add(icon_slug)
                icon_path = f"icons/com.figma.Desktop/{icon_slug}.svg"
            else:
                icon_path = None
            zh = ZH_TITLE.get(desc)
            if not zh:
                print(f"Missing zh-Hans for: {desc!r}", file=sys.stderr)
                return 1
            item: dict = {
                "id": item_id,
                "title": {"en": desc, "zh-Hans": zh},
                "shortcutConfiguration": {
                    "keyCode": kc,
                    "carbonModifiers": cm,
                    "displayKey": display,
                },
            }
            if icon_path:
                item["icon"] = {"type": "svg", "path": icon_path}
            items.append(item)
        categories_out.append(
            {
                "id": cat_id,
                "title": {"en": en_title, "zh-Hans": zh_title},
                "items": items,
            }
        )

    doc = {
        "bundleIdentifier": "com.figma.Desktop",
        "i18n": {
            "defaultLocale": "en",
            "locales": ["en", "zh-Hans"],
        },
        "categories": categories_out,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    ICON_DIR.mkdir(parents=True, exist_ok=True)
    for slug in sorted(icons_needed):
        p = ICON_DIR / f"{slug}.svg"
        p.write_text(placeholder_svg(slug), encoding="utf-8")

    print(f"Wrote {OUT_JSON} ({len(rows)} shortcuts)")
    print(f"Wrote {len(icons_needed)} placeholder SVGs under {ICON_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
