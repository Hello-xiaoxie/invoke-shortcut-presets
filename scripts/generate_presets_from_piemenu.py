#!/usr/bin/env python3
"""
Fetch Pie Menu shortcut pages and emit invoke-shortcut-presets JSON.
Parses <tbody id="SectionId" role="rowgroup"> blocks with <h3> titles.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, unquote

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from office_ms_zh import title_zh_for_bundle  # noqa: E402

CMD, SHIFT, OPT, CTRL = 256, 512, 2048, 4096

# Matches Swift `KeyboardShortcutConfiguration.none` (UInt16.max) — no key binding in source HTML.
EMPTY_KEY_CODE = 65535

# kVK_ANSI_* style (US layout) for displayKey when not special key
VK_TO_CHAR = {
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
    20: "3",
    21: "4",
    22: "6",
    23: "5",
    24: "=",
    25: "9",
    26: "7",
    27: "-",
    28: "8",
    29: "0",
    31: "O",
    32: "U",
    33: "[",
    34: "I",
    35: "P",
    37: "L",
    38: "J",
    40: "K",
    41: ";",
    42: "\\",
    43: ",",
    44: "/",
    45: "N",
    46: "M",
    47: ".",
    48: "⇥",
    49: "Space",
    50: "`",
    51: "⌫",
    53: "⎋",
    76: "↩",
    96: "F5",
    97: "F6",
    98: "F7",
    99: "F3",
    100: "F8",
    101: "F9",
    103: "F11",
    107: "F1",
    109: "F10",
    111: "F12",
    115: "Home",
    116: "Page Up",
    119: "End",
    120: "F2",
    121: "Page Down",
    122: "F1",
    118: "F4",
    123: "←",
    124: "→",
    125: "↓",
    126: "↑",
}


def carbon(mod_str: str) -> int:
    if not mod_str or mod_str.strip().lower() in ("", "undefined", "none"):
        return 0
    m = 0
    s = unquote(mod_str).lower().replace(",", " ")
    for token in re.split(r"[\s,]+", s):
        token = token.strip()
        if token == "command":
            m |= CMD
        elif token == "shift":
            m |= SHIFT
        elif token == "option":
            m |= OPT
        elif token == "control":
            m |= CTRL
    return m


def display_key(key_code: int) -> str:
    if key_code == EMPTY_KEY_CODE:
        return ""
    return VK_TO_CHAR.get(key_code, str(key_code))


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (InvokePresetGen)"})
    last: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as e:
            last = e
            time.sleep(1.0 * (attempt + 1))
    raise last  # type: ignore[misc]


def parse_piemenu_href(href: str) -> dict | None:
    href = unescape(href)
    if "piemenu://" not in href:
        return None
    q = href.split("?", 1)
    if len(q) < 2:
        return None
    qs = parse_qs(q[1], keep_blank_values=True)

    def g(k: str) -> str:
        v = qs.get(k, [""])[0]
        return unquote(v) if v else ""

    desc = g("description")
    if not desc:
        return None
    kc_raw = g("key_code")
    if not kc_raw or kc_raw.strip().lower() in ("undefined", "none", "null", "nan"):
        key_code = EMPTY_KEY_CODE
    else:
        try:
            key_code = int(kc_raw)
        except ValueError:
            key_code = EMPTY_KEY_CODE
    return {
        "description": desc,
        "key_code": key_code,
        "modifiers": g("modifiers"),
        "bundleid": g("bundleid"),
        "carbon": carbon(g("modifiers")),
    }


def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:48] or "misc"


def stable_item_id(prefix: str, desc: str, key_code: int, carbon_m: int) -> str:
    h = hashlib.sha1(f"{desc}|{key_code}|{carbon_m}".encode()).hexdigest()[:10]
    return f"{prefix}.{h}"


# --- Category title (EN sidebar / h3) -> zh-Hans ---
CATEGORY_ZH: dict[str, str] = {
    "Frequently used shortcuts": "常用快捷键",
    "Frequently Used Shortcuts": "常用快捷键",
    "Work in windows and dialogs": "窗口与对话框",
    "Move and scroll in a sheet or workbook": "在工作表或工作簿中移动与滚动",
    "Enter data on a sheet": "在工作表中输入数据",
    "Work in cells or the Formula bar": "在单元格或编辑栏中操作",
    "Format and edit data": "设置格式与编辑数据",
    "Select cells, columns, or rows": "选择单元格、列或行",
    "Work with a selection": "使用所选区域",
    "Use charts": "使用图表",
    "Sort, filter, and use PivotTable reports": "排序、筛选与数据透视表",
    "Outline data": "分级显示数据",
    "Function key shortcuts for Excel 2016": "Excel 功能键",
    "Global Shortcuts": "全局快捷键",
    "Tools": "工具",
    "Layout": "布局",
    "View": "视图",
    "Publish": "发布",
    "Quick Actions": "快捷操作",
    "Alignment": "对齐",
    "Edit": "编辑",
    "Group": "编组",
    "Text": "文本",
    "Component": "组件",
    "Navigation": "导航",
    "Call actions": "通话操作",
    "Files and snippets": "文件与代码片段",
    "Format messages": "设置消息格式",
    "Take an action on a message": "对消息执行操作",
    "Mark messages read or unread": "标记已读/未读",
    "Switch workspaces": "切换工作区",
    "All Unreads navigation": "全部未读导航",
    "Meetings and Calls": "会议与通话",
    "Messaging": "消息",
    "General": "通用",
    "Move the Cursor": "移动光标",
    "Select text and graphics": "选择文本与图形",
    "Extend a selection": "扩展所选内容",
    "Edit text and graphics": "编辑文本与图形",
    "Align and format paragraphs": "对齐与设置段落格式",
    "Set line spacing": "设置行距",
    "Format characters": "设置字符格式",
    "Insert special characters": "插入特殊字符",
    "Work with fields": "使用域",
    "Outline a document": "大纲",
    "Review a document": "审阅文档",
    "Print a document": "打印文档",
    "Move around in a table": "在表格中移动",
    "Resize table columns by using the ruler": "使用标尺调整表格列宽",
    "Resize table columns directly in a table.": "在表格中直接调整列宽",
    "Insert paragraphs and tab characters in a table": "在表格中插入段落和制表符",
    "Use footnotes and endnotes": "脚注和尾注",
    "Right-to-left language features": "从右向左语言功能",
    "Function key shortcuts": "功能键快捷键",
    # Affinity / Principle / Canva / Rive / Miro
    "File": "文件",
    "Layers": "图层",
    "Text Formatting": "文本格式",
    "Opacity": "不透明度",
    "Editing": "编辑",
    "Canvas Navigation": "画布导航",
    "Driver Navigation": "驱动导航",
    "Animate Navigation": "动画导航",
    "Selection": "选择",
    "Preview": "预览",
    "Editor": "编辑器",
    "Hierarchy": "层级",
    "Advanced Text": "高级文本",
}

# Exact English item title -> zh-Hans (short UI labels; avoids bad partial regex matches)
EXACT_TITLE_ZH: dict[str, str] = {
    # Arc
    "Add split view": "添加分屏",
    "Toggle sidebar": "切换侧边栏",
    "Close tab": "关闭标签页",
    "Capture": "截图",
    "Copy page url": "复制页面链接",
    "Enter reader mode": "进入阅读模式",
    "New tab": "新建标签页",
    "Developer tools": "开发者工具",
    # Framer — tools & panels
    "Insert": "插入",
    "Library": "资源库",
    "Frame": "画框",
    "Image": "图片",
    "Stack": "堆栈",
    "Rows": "行",
    "Columns": "列",
    "Wrap": "换行排列",
    "Grid": "网格",
    "Text": "文本",
    "Interaction": "交互",
    "Graphic": "图形",
    "Comment": "评论",
    "Zoom": "缩放",
    "Sample Color": "吸取颜色",
    "Add Frame": "添加画框",
    "Add Stack": "添加堆栈",
    "Remove Wrapper": "移除包装",
    "Bring Forward": "前移一层",
    "Send Backward": "后移一层",
    "Bring to Front": "置于顶层",
    "Send to Back": "置于底层",
    "Night Mode": "夜间模式",
    "Zoom In": "放大",
    "Zoom Out": "缩小",
    "Zoom to 100%": "缩放到 100%",
    "Zoom to Fit": "缩放以适合",
    "Zoom to Selection": "缩放至所选",
    "Toggle Interface": "切换界面",
    "Show Rulers": "显示标尺",
    "Collapse All Layers": "折叠全部图层",
    "Show Guides": "显示参考线",
    "Show Pages": "显示页面",
    "Show Layer": "显示图层",
    "Show Assets": "显示资源",
    "Open Site": "打开站点",
    "Open Settings": "打开设置",
    "Open Preview": "打开预览",
    "Publish": "发布",
    "Quick Actions": "快捷操作",
    "New": "新建",
    "Upload Image": "上传图片",
    "Version History": "版本历史",
    "Align Left": "左对齐",
    "Align Horizontally": "水平对齐",
    "Align Right": "右对齐",
    "Align Top": "顶对齐",
    "Align Vertically": "垂直对齐",
    "Align Bottom": "底对齐",
    "Distribute Horizontally": "水平分布",
    "Distribute Vertically": "垂直分布",
    "Copy Style": "复制样式",
    "Paste Style": "粘贴样式",
    "Duplicate": "创建副本",
    "Delete": "删除",
    "Lock": "锁定",
    "Hide": "隐藏",
    "Rename": "重命名",
    "Back To Page": "返回页面",
    "Select Parent": "选择父级",
    "Select All Siblings": "选择全部同级",
    "Select All Children": "选择全部子级",
    "Group": "编组",
    "Ungroup": "取消编组",
    "Create Component": "创建组件",
    "Create From Code": "从代码创建",
    # Slack (short)
    "Toggle full screen view": "切换全屏",
    "Open previous search": "打开上次搜索",
    "Search current channel or conversation": "在当前频道或对话中搜索",
    "Saved items": "已保存项目",
    "People": "人员",
    "Mentions & reactions": "提及与反应",
    "Channel info pane": "频道信息面板",
    "Open or close right pane": "打开或关闭右侧面板",
    "Next channel or DM visited": "下一个访问过的频道或私信",
    "Previous channel or DM visited": "上一个访问过的频道或私信",
    "Next unread channel or DM": "下一个未读频道或私信",
    "Previous unread channel or DM": "上一个未读频道或私信",
    "Open the Threads view": "打开话题视图",
    "Open channel browser": "打开频道浏览器",
    "Compose a new message": "撰写新消息",
    "Open direct messages menu": "打开私信菜单",
    "Jump to a conversation": "跳转到对话",
    "Create new Snippet": "新建代码片段",
    "Upload file": "上传文件",
    "Apply formatting to markdown text": "对 Markdown 文本应用格式",
    "Codeblock selected text": "将所选设为代码块",
    "Code selected text": "将所选设为行内代码",
    "Quote selected text": "引用所选文本",
    "Strikethrough selected text": "为所选添加删除线",
    "Italicize selected text": "将所选设为斜体",
    "Bold selected text": "将所选设为粗体",
    "Create a new line in your message": "在消息中换行",
    "Edit your last message": "编辑上一条消息",
    "Mark all messages as read": "将全部消息标为已读",
    "Mark all messages in current channel or DM as read": "将当前频道或私信标为已读",
    "Open All Unreads view": "打开「全部未读」视图",
    "Collapse channels": "折叠频道列表",
    "Open channels": "展开频道列表",
    "Move to message below": "移至下一条消息",
    "Move to message above": "移至上一条消息",
    # Teams
    "Toggle fullscreen": "切换全屏",
    "Go to sharing toolbar": "转到共享工具栏",
    "Toggle video": "开关视频",
    "Toggle mute": "开关静音",
    "Start video call": "开始视频通话",
    "Start audio call": "开始语音通话",
    "Decline call": "拒接来电",
    "Accept audio call": "接听语音",
    "Accept video call": "接听视频",
    "Reply to thread": "回复话题",
    "Start new line": "换行",
    "Attach file": "附加文件",
    "Send (expanded compose box)": "发送（展开撰写框）",
    "Expand compose box": "展开撰写框",
    "Go to compose box": "转到撰写框",
    "Go to next section": "转到下一区域",
    "Go to previous section": "转到上一区域",
    "Move selected team down": "将所选团队下移",
    "Move selected team up": "将所选团队上移",
    "Go to next list item": "下一列表项",
    "Go to previous list item": "上一列表项",
    "Open Files": "打开文件",
    "Open Calls": "打开通话",
    "Open Calendar": "打开日历",
    "Open Teams": "打开团队",
    "Open Chat": "打开聊天",
    "Open Activity": "打开活动",
    "Return to default zoom": "恢复默认缩放",
    "Zoom out": "缩小",
    "Zoom in": "放大",
    "Open Help": "打开帮助",
    "Start a new chat": "开始新聊天",
    "Goto": "转到",
    "Show commands": "显示命令",
    "Go to Search": "前往搜索",
    "Show keyboard shortcuts": "显示键盘快捷键",
    # Excel — frequent short rows
    "Open Visual Basic": "打开 Visual Basic",
    "Fill Down": "向下填充",
    "Fill Right": "向右填充",
    "Insert cells": "插入单元格",
    "Delete cells": "删除单元格",
    "Calculate all open workbooks": "计算所有打开的工作簿",
    "Close window": "关闭窗口",
    "Quit Excel": "退出 Excel",
    "Paste Special": "选择性粘贴",
    "New blank workbook": "新建空白工作簿",
    "New workbook from template": "从模板新建工作簿",
    "Display the Save As dialog box": "显示「另存为」对话框",
    "Display the Open dialog box": "显示「打开」对话框",
    "Display the Go To dialog box": "显示「定位」对话框",
    "Display the Replace dialog box": "显示「替换」对话框",
    "Display the Format Cells dialog box": "显示「设置单元格格式」对话框",
    "Check spelling": "拼写检查",
    "Open the thesaurus": "打开同义词库",
    "Display the Formula Builder": "显示公式生成器",
    "Open the Define Name dialog box": "显示「定义名称」对话框",
    "Open the Create names dialog box": "显示「指定名称」对话框",
    "Insert a new sheet *": "插入新工作表 *",
    "Insert a new sheet*": "插入新工作表*",
}


def rough_zh_sentence(en: str) -> str:
    """Light-touch zh for item titles; prefer keeping official EN for edge cases."""
    if not en:
        return en
    if en in EXACT_TITLE_ZH:
        return EXACT_TITLE_ZH[en]
    # Fix Pie Menu / Word typos
    fixes = {
        "Add the to Reader": "添加到阅读列表",
        "Select to select the entire document": "全选文档",
    }
    if en in fixes:
        return fixes[en]
    z = en
    repl = [
        (r"\bUndo the last action\b", "撤消上一操作"),
        (r"\bRedo the last action\b", "恢复上一操作"),
        (r"\bCut\b", "剪切"),
        (r"\bCopy\b", "复制"),
        (r"\bPaste\b", "粘贴"),
        (r"\bFind\b", "查找"),
        (r"\bPrint\b", "打印"),
        (r"\bSave\b", "存储"),
        (r"\bOpen\b", "打开"),
        (r"\bClose\b", "关闭"),
        (r"\bBold\b", "加粗"),
        (r"\bItalic\b", "斜体"),
        (r"\bUnderline\b", "下划线"),
        (r"\bSelect All\b", "全选"),
        (r"\bPreferences\b", "偏好设置"),
        (r"\bDeveloper Tools\b", "开发者工具"),
        (r"\bNew tab\b", "新建标签页"),
        (r"\bClose tab\b", "关闭标签页"),
        (r"\bToggle sidebar\b", "切换侧边栏"),
        (r"\bQuit\b", "退出"),
        (r"\bMinimize\b", "最小化"),
    ]
    for pat, zh in repl:
        z = re.sub(pat, zh, z, flags=re.I)
    # If almost unchanged, append nothing — return mixed line (many Office strings stay EN in CN docs)
    if z == en and len(en) < 60:
        # short labels
        short = {
            "Paste": "粘贴",
            "Copy": "复制",
            "Clear": "清除",
            "Save": "存储",
            "Undo": "撤消",
            "Redo": "恢复",
            "Cut": "剪切",
            "Bold": "加粗",
            "Print": "打印",
            "Italic": "斜体",
            "Underline": "下划线",
        }
        if en.strip() in short:
            return short[en.strip()]
    return z if z != en else en


def extract_sections(html: str, expected_bundle: str) -> list[tuple[str, str, list[dict]]]:
    """
    Returns list of (category_en, category_id_slug, [parsed link dicts])
    """
    out: list[tuple[str, str, list[dict]]] = []
    for m in re.finditer(
        r'<tbody([^>]*)>(.*?)</tbody>',
        html,
        re.DOTALL | re.IGNORECASE,
    ):
        open_attrs = m.group(1)
        if 'role="rowgroup"' not in open_attrs and "role='rowgroup'" not in open_attrs:
            continue
        idm = re.search(r'\bid="([A-Za-z][A-Za-z0-9]*)"', open_attrs)
        if not idm:
            continue
        block = m.group(2)
        h3 = re.search(r"<h3[^>]*itemProp=\"name\"[^>]*>([^<]+)</h3>", block)
        if not h3:
            h3 = re.search(r"<h3[^>]*>([^<]+)</h3>", block)
        if not h3:
            continue
        cat_en = unescape(h3.group(1)).strip()
        items: list[dict] = []
        for am in re.finditer(r'href="(piemenu://[^"]+)"', block):
            parsed = parse_piemenu_href(am.group(1))
            if not parsed:
                continue
            if parsed["bundleid"] and parsed["bundleid"] != expected_bundle:
                continue
            items.append(parsed)
        if items:
            out.append((cat_en, slug(cat_en), items))
    return out


def item_zh_hans(bundle_id: str, desc: str) -> str:
    if bundle_id in ("com.microsoft.Word", "com.microsoft.Excel"):
        z = title_zh_for_bundle(bundle_id, desc)
        if z:
            return z
    return rough_zh_sentence(desc)


def build_json(bundle_id: str, slug_prefix: str, sections: list[tuple[str, str, list[dict]]]) -> dict:
    categories = []
    for cat_en, cat_slug, items in sections:
        cat_zh = CATEGORY_ZH.get(cat_en, rough_zh_sentence(cat_en))
        rows = []
        for p in items:
            desc = p["description"]
            rows.append(
                {
                    "id": stable_item_id(f"remote.{slug_prefix}.{cat_slug}", desc, p["key_code"], p["carbon"]),
                    "title": {"en": desc, "zh-Hans": item_zh_hans(bundle_id, desc)},
                    "shortcutConfiguration": {
                        "keyCode": p["key_code"],
                        "carbonModifiers": p["carbon"],
                        "displayKey": display_key(p["key_code"]),
                    },
                }
            )
        categories.append(
            {
                "id": f"remote.{slug_prefix}.{cat_slug}",
                "title": {"en": cat_en, "zh-Hans": cat_zh},
                "items": rows,
            }
        )
    return {
        "bundleIdentifier": bundle_id,
        "i18n": {"defaultLocale": "en", "locales": ["en", "zh-Hans"]},
        "categories": categories,
    }


# Manual fixes: description substring -> (keyCode, carbonModifiers, displayKey)
MANUAL_FIXES: dict[str, dict[str, object]] = {
    # Word — Pie Menu data errors vs Office for Mac
    "Choose the Save As command (File menu).": {"carbonModifiers": CMD | SHIFT, "displayKey": "S"},
    "Go to the previous window": {"carbonModifiers": CMD | SHIFT, "displayKey": "`"},
    "Edit a bookmark": {"carbonModifiers": CMD | SHIFT, "displayKey": "F5"},
    "Look up selected text on the Internet": {"carbonModifiers": CMD | SHIFT, "displayKey": "L"},
    "Insert a LISTNUM field": {"carbonModifiers": CMD | OPT | SHIFT, "displayKey": "L"},
    "Unlink a field": {"carbonModifiers": CMD | SHIFT, "displayKey": "F9"},
    "Unlock a field": {"carbonModifiers": CMD | SHIFT, "displayKey": "F11"},
    "Demote to body text": {"carbonModifiers": CMD | SHIFT, "displayKey": "N"},
    "Underline words but not spaces": {"carbonModifiers": CMD | SHIFT, "displayKey": "W"},
    "Double-underline text": {"carbonModifiers": CMD | SHIFT, "displayKey": "D"},
    "Format in all small capital letters": {"carbonModifiers": CMD | SHIFT, "displayKey": "K"},
    "Apply superscript formatting (automatic spacing)": {"carbonModifiers": CMD | SHIFT, "displayKey": "+"},
    "Apply strike-through formatting": {"carbonModifiers": CMD | SHIFT, "displayKey": "X"},
    "Insert a column break": {"carbonModifiers": CMD | SHIFT, "displayKey": "↩"},
    "Insert a nonbreaking hyphen": {"carbonModifiers": CMD | SHIFT, "displayKey": "-"},
    "Expand text under a heading": {"carbonModifiers": CTRL | SHIFT, "displayKey": "+"},
    "Collapse text under a heading": {"carbonModifiers": CTRL | SHIFT, "displayKey": "-"},
    # Teams — obvious HTML mistakes from Pie Menu
    "Attach file": {"carbonModifiers": CMD, "displayKey": "O"},
    "Open Files": {"carbonModifiers": CMD | SHIFT, "displayKey": "6"},
    "Open Calls": {"carbonModifiers": CMD | SHIFT, "displayKey": "5"},
    "Open Calendar": {"carbonModifiers": CMD | SHIFT, "displayKey": "4"},
    "Open Teams": {"carbonModifiers": CMD | SHIFT, "displayKey": "3"},
    "Open Chat": {"carbonModifiers": CMD | SHIFT, "displayKey": "2"},
    "Open Activity": {"carbonModifiers": CMD | SHIFT, "displayKey": "1"},
    "Open Settings": {"carbonModifiers": CMD, "displayKey": ","},
    "Start a new chat": {"carbonModifiers": CMD, "displayKey": "N"},
    "Goto": {"carbonModifiers": CMD | SHIFT, "displayKey": "G"},
    "Open Help": {"carbonModifiers": CMD, "displayKey": "F1"},
}

# Framer: Pie Menu uses key_code=6 for "Frame" but 6 is Z on macOS; real shortcut is F (key 3).
FRAMER_KEY_FIXES = {
    "Frame": (3, 0, "F"),
}


def apply_manual_fixes(bundle_id: str, sections: list[tuple[str, str, list[dict]]]):
    for _cat_en, _slug, items in sections:
        for p in items:
            desc = p["description"]
            if desc in MANUAL_FIXES:
                fx = MANUAL_FIXES[desc]
                if "carbonModifiers" in fx:
                    p["carbon"] = int(fx["carbonModifiers"])  # type: ignore
                # display key overridden after
            if bundle_id == "com.framer.electron" and desc in FRAMER_KEY_FIXES:
                kc, cm, _dk = FRAMER_KEY_FIXES[desc]
                p["key_code"] = kc
                p["carbon"] = cm


def main():
    pages = [
        ("https://www.pie-menu.com/shortcuts/microsoft-word", "com.microsoft.Word", "word"),
        ("https://www.pie-menu.com/shortcuts/microsoft-excel", "com.microsoft.Excel", "excel"),
        ("https://www.pie-menu.com/shortcuts/arc", "company.thebrowser.Browser", "arc"),
        ("https://www.pie-menu.com/shortcuts/framer", "com.framer.electron", "framer"),
        ("https://www.pie-menu.com/shortcuts/slack", "com.tinyspeck.slackmacgap", "slack"),
        ("https://www.pie-menu.com/shortcuts/teams", "com.microsoft.teams2", "teams"),
        ("https://www.pie-menu.com/shortcuts/affinity-publisher", "com.seriflabs.affinitypublisher2", "affinity-publisher"),
        ("https://www.pie-menu.com/shortcuts/principle", "com.danielhooper.principle", "principle"),
        ("https://www.pie-menu.com/shortcuts/canva", "com.canva.canvaeditor", "canva"),
        ("https://www.pie-menu.com/shortcuts/rive", "app.rive.editor", "rive"),
        ("https://www.pie-menu.com/shortcuts/miro", "com.electron.realtimeboard", "miro"),
        ("https://www.pie-menu.com/shortcuts/affinityDesigner", "com.seriflabs.affinitydesigner2", "affinity-designer"),
    ]
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "presets"
    for url, bundle, prefix in pages:
        print("fetch", url, file=sys.stderr)
        html = fetch(url)
        sections = extract_sections(html, bundle)
        if not sections:
            print("no sections", url, file=sys.stderr)
            continue
        apply_manual_fixes(bundle, sections)
        data = build_json(bundle, prefix, sections)
        # apply display overrides
        for cat in data["categories"]:
            for it in cat["items"]:
                desc = it["title"]["en"]
                if desc in MANUAL_FIXES and "displayKey" in MANUAL_FIXES[desc]:
                    it["shortcutConfiguration"]["displayKey"] = str(MANUAL_FIXES[desc]["displayKey"])
        fname = f"{out_dir}/{bundle.replace('/', '_')}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        n = sum(len(c["items"]) for c in data["categories"])
        print(fname, "categories", len(data["categories"]), "items", n, file=sys.stderr)


if __name__ == "__main__":
    main()
