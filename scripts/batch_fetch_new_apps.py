#!/usr/bin/env python3
"""
Batch fetch ALL new apps from Pie Menu website and generate preset JSON files.
Skips apps that already have preset files in the presets/ directory.

Usage:
    python scripts/batch_fetch_new_apps.py [presets_dir]
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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CMD, SHIFT, OPT, CTRL = 256, 512, 2048, 4096
EMPTY_KEY_CODE = 65535
BASE_URL = "https://www.pie-menu.com"

VK_TO_CHAR = {
    0: "A", 1: "S", 2: "D", 3: "F", 4: "H", 5: "G", 6: "Z", 7: "X",
    8: "C", 9: "V", 11: "B", 12: "Q", 13: "W", 14: "E", 15: "R",
    16: "Y", 17: "T", 18: "1", 19: "2", 20: "3", 21: "4", 22: "6",
    23: "5", 24: "=", 25: "9", 26: "7", 27: "-", 28: "8", 29: "0",
    31: "O", 32: "U", 33: "[", 34: "I", 35: "P", 37: "L", 38: "J",
    40: "K", 41: ";", 42: "\\", 43: ",", 44: "/", 45: "N", 46: "M",
    47: ".", 48: "⇥", 49: "Space", 50: "`", 51: "⌫", 53: "⎋",
    76: "↩", 96: "F5", 97: "F6", 98: "F7", 99: "F3", 100: "F8",
    101: "F9", 103: "F11", 107: "F1", 109: "F10", 111: "F12",
    115: "Home", 116: "Page Up", 118: "F4", 119: "End", 120: "F2",
    121: "Page Down", 122: "F1", 123: "←", 124: "→", 125: "↓", 126: "↑",
}

# ---------------------------------------------------------------------------
# Already existing bundle IDs (from presets/ dir) — will be populated at runtime
# ---------------------------------------------------------------------------
EXISTING_BUNDLES: set[str] = set()

# ---------------------------------------------------------------------------
# Category zh-Hans mapping
# ---------------------------------------------------------------------------
CATEGORY_ZH: dict[str, str] = {
    "Frequently used shortcuts": "常用快捷键",
    "Frequently Used Shortcuts": "常用快捷键",
    "Global Shortcuts": "全局快捷键",
    "Tools": "工具",
    "Layout": "布局",
    "View": "视图",
    "Edit": "编辑",
    "File": "文件",
    "Layers": "图层",
    "Selection": "选择",
    "Text": "文本",
    "Text Formatting": "文本格式",
    "Navigation": "导航",
    "General": "通用",
    "Window": "窗口",
    "Tabs": "标签页",
    "Toolbar": "工具栏",
    "Search": "搜索",
    "Bookmarks": "书签",
    "Preferences": "偏好设置",
    "Panels": "面板",
    "Canvas": "画布",
    "Canvas Navigation": "画布导航",
    "Shapes": "形状",
    "Objects": "对象",
    "Transform": "变换",
    "Zoom": "缩放",
    "Playback": "播放",
    "Recording": "录制",
    "Mixing": "混音",
    "Tracks": "轨道",
    "Transport": "走带控制",
    "Editing": "编辑",
    "Timeline": "时间线",
    "Export": "导出",
    "Import": "导入",
    "Preview": "预览",
    "Component": "组件",
    "Components": "组件",
    "Alignment": "对齐",
    "Group": "编组",
    "Arrange": "排列",
    "Publish": "发布",
    "Quick Actions": "快捷操作",
    "Opacity": "不透明度",
    "Editor": "编辑器",
    "Hierarchy": "层级",
    "Advanced Text": "高级文本",
    "Code": "代码",
    "Debug": "调试",
    "Run": "运行",
    "Build": "构建",
    "Refactor": "重构",
    "Source Control": "版本控制",
    "Terminal": "终端",
    "Sidebar": "侧边栏",
    "Workspace": "工作区",
    "Project": "项目",
    "Navigator": "导航器",
    "Library": "资源库",
    "Inspector": "检查器",
    "Insert": "插入",
    "Format": "格式",
    "Table": "表格",
    "Media": "媒体",
    "Annotations": "批注",
    "Comments": "注释",
    "Drawing": "绘图",
    "Filters": "过滤",
    "Markers": "标记",
    "Effects": "效果",
    "Trim": "修剪",
    "Color": "颜色",
    "Audio": "音频",
    "Video": "视频",
    "Clips": "片段",
    "Sequences": "序列",
    "Render": "渲染",
    "Compositing": "合成",
    "Modeling": "建模",
    "Sculpting": "雕刻",
    "Animation": "动画",
    "UV Editing": "UV 编辑",
    "Shading": "着色",
    "Shortcuts": "快捷键",
    "Messages": "消息",
    "Messaging": "消息",
    "Meetings and Calls": "会议与通话",
    "Communication": "通信",
    "Keyboard": "键盘",
    "Document": "文档",
    "Cursor": "光标",
    "Display": "显示",
    "Paragraph": "段落",
    "Block": "块",
    "Page": "页面",
    "App": "应用",
    "Mail": "邮件",
    "Contacts": "通讯录",
    "Notes": "备忘录",
    "Tasks": "任务",
    "Calendar": "日历",
    "Composer": "编辑器",
    "Reader": "阅读器",
    "Viewer": "查看器",
    "Board": "看板",
    "List": "列表",
    "Cards": "卡片",
    "Dialog": "对话框",
    "Panels & Tools": "面板与工具",
    "Markers & Regions": "标记与区域",
    "Basic": "基础",
    "Interface": "界面",
    "Actions": "操作",
    "Management": "管理",
}

# ---------------------------------------------------------------------------
# Common item title EN -> zh-Hans
# ---------------------------------------------------------------------------
COMMON_TITLE_ZH: dict[str, str] = {
    "Copy": "复制", "Paste": "粘贴", "Cut": "剪切", "Undo": "撤消",
    "Redo": "恢复", "Save": "存储", "Save As": "另存为", "Open": "打开",
    "Close": "关闭", "New": "新建", "Print": "打印", "Find": "查找",
    "Replace": "替换", "Select All": "全选", "Delete": "删除",
    "Duplicate": "创建副本", "Rename": "重命名", "Quit": "退出",
    "Minimize": "最小化", "Hide": "隐藏", "Bold": "加粗",
    "Italic": "斜体", "Underline": "下划线", "Zoom In": "放大",
    "Zoom Out": "缩小", "Zoom to Fit": "缩放以适合",
    "Zoom to 100%": "缩放到 100%", "Group": "编组", "Ungroup": "取消编组",
    "Lock": "锁定", "Unlock": "解锁", "Show Rulers": "显示标尺",
    "Show Grid": "显示网格", "Toggle Sidebar": "切换侧边栏",
    "Toggle sidebar": "切换侧边栏", "New tab": "新建标签页",
    "Close tab": "关闭标签页", "New Tab": "新建标签页",
    "Close Tab": "关闭标签页", "Preferences": "偏好设置",
    "Settings": "设置", "Fullscreen": "全屏", "Full Screen": "全屏",
    "Toggle fullscreen": "切换全屏", "Toggle Full Screen": "切换全屏",
    "Refresh": "刷新", "Reload": "重新加载", "Back": "后退",
    "Forward": "前进", "Home": "主页", "Search": "搜索",
    "Bookmark": "书签", "Developer Tools": "开发者工具",
    "Developer tools": "开发者工具", "Console": "控制台",
    "Import": "导入", "Export": "导出", "Share": "共享",
    "Comment": "评论", "Align Left": "左对齐", "Align Right": "右对齐",
    "Align Center": "居中对齐", "Align Top": "顶对齐",
    "Align Bottom": "底对齐", "Bring Forward": "前移一层",
    "Send Backward": "后移一层", "Bring to Front": "置于顶层",
    "Send to Back": "置于底层", "Flatten": "拼合",
    "Play": "播放", "Pause": "暂停", "Stop": "停止",
    "Record": "录制", "Mute": "静音", "Solo": "独奏",
    "Loop": "循环", "Split": "分割", "Merge": "合并",
    "Crop": "裁剪", "Trim": "修剪", "Snap": "吸附",
    "Paste Special": "选择性粘贴", "Find and Replace": "查找和替换",
    "Quick Open": "快速打开", "Command Palette": "命令面板",
    "Toggle Terminal": "切换终端", "New Window": "新建窗口",
    "Close Window": "关闭窗口", "Split Editor": "拆分编辑器",
    "Go to Line": "转到行", "Go to File": "转到文件",
    "Toggle Comment": "切换注释", "Indent": "缩进",
    "Outdent": "减少缩进", "Format Document": "格式化文档",
    "Fold": "折叠", "Unfold": "展开", "Fold All": "全部折叠",
    "Unfold All": "全部展开",
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
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
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (InvokePresetGen/2.0)"})
    last: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as e:
            last = e
            time.sleep(2.0 * (attempt + 1))
    raise last  # type: ignore[misc]


def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:48] or "misc"


def stable_item_id(prefix: str, desc: str, key_code: int, carbon_m: int) -> str:
    h = hashlib.sha1(f"{desc}|{key_code}|{carbon_m}".encode()).hexdigest()[:10]
    return f"{prefix}.{h}"


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


def rough_zh(en: str) -> str:
    """Translate item title EN -> zh-Hans using common mappings + regex."""
    if not en:
        return en
    if en in COMMON_TITLE_ZH:
        return COMMON_TITLE_ZH[en]
    z = en
    repl = [
        (r"\bUndo the last action\b", "撤消上一操作"),
        (r"\bRedo the last action\b", "恢复上一操作"),
        (r"\bCut\b", "剪切"), (r"\bCopy\b", "复制"), (r"\bPaste\b", "粘贴"),
        (r"\bFind\b", "查找"), (r"\bPrint\b", "打印"), (r"\bSave\b", "存储"),
        (r"\bOpen\b", "打开"), (r"\bClose\b", "关闭"), (r"\bBold\b", "加粗"),
        (r"\bItalic\b", "斜体"), (r"\bUnderline\b", "下划线"),
        (r"\bSelect All\b", "全选"), (r"\bPreferences\b", "偏好设置"),
        (r"\bDeveloper Tools\b", "开发者工具"),
        (r"\bNew tab\b", "新建标签页"), (r"\bClose tab\b", "关闭标签页"),
        (r"\bToggle sidebar\b", "切换侧边栏"),
        (r"\bQuit\b", "退出"), (r"\bMinimize\b", "最小化"),
        (r"\bZoom in\b", "放大"), (r"\bZoom out\b", "缩小"),
        (r"\bNew Window\b", "新建窗口"), (r"\bClose Window\b", "关闭窗口"),
        (r"\bFull Screen\b", "全屏"), (r"\bSearch\b", "搜索"),
        (r"\bReplace\b", "替换"), (r"\bDelete\b", "删除"),
        (r"\bDuplicate\b", "创建副本"), (r"\bRename\b", "重命名"),
        (r"\bGroup\b", "编组"), (r"\bUngroup\b", "取消编组"),
        (r"\bLock\b", "锁定"), (r"\bUnlock\b", "解锁"),
        (r"\bHide\b", "隐藏"), (r"\bShow\b", "显示"),
        (r"\bExport\b", "导出"), (r"\bImport\b", "导入"),
        (r"\bInsert\b", "插入"), (r"\bAlign\b", "对齐"),
        (r"\bDistribute\b", "分布"),
    ]
    for pat, zh in repl:
        z = re.sub(pat, zh, z, flags=re.I)
    return z


def cat_zh(en: str) -> str:
    if en in CATEGORY_ZH:
        return CATEGORY_ZH[en]
    return rough_zh(en)


# ---------------------------------------------------------------------------
# HTML parsing
# ---------------------------------------------------------------------------
def extract_sections(html: str, expected_bundle: str) -> list[tuple[str, str, list[dict]]]:
    """Parse the Pie Menu app page HTML -> list of (category_en, category_slug, items)."""
    out: list[tuple[str, str, list[dict]]] = []
    for m in re.finditer(r'<tbody([^>]*)>(.*?)</tbody>', html, re.DOTALL | re.IGNORECASE):
        open_attrs = m.group(1)
        if 'role="rowgroup"' not in open_attrs and "role='rowgroup'" not in open_attrs:
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
            if parsed["bundleid"] and expected_bundle and parsed["bundleid"] != expected_bundle:
                continue
            items.append(parsed)
        if items:
            out.append((cat_en, slug(cat_en), items))
    return out


def extract_bundle_from_html(html: str) -> str:
    """Try to get bundleid from first piemenu:// link in page."""
    m = re.search(r'href="(piemenu://[^"]+)"', html)
    if m:
        parsed = parse_piemenu_href(m.group(1))
        if parsed and parsed["bundleid"]:
            return parsed["bundleid"]
    return ""


# ---------------------------------------------------------------------------
# Build JSON
# ---------------------------------------------------------------------------
def build_json(bundle_id: str, slug_prefix: str, sections: list[tuple[str, str, list[dict]]]) -> dict:
    categories = []
    for cat_en_name, cat_slug_name, items in sections:
        rows = []
        for p in items:
            desc = p["description"]
            rows.append({
                "id": stable_item_id(f"remote.{slug_prefix}.{cat_slug_name}", desc, p["key_code"], p["carbon"]),
                "title": {"en": desc, "zh-Hans": rough_zh(desc)},
                "shortcutConfiguration": {
                    "keyCode": p["key_code"],
                    "carbonModifiers": p["carbon"],
                    "displayKey": display_key(p["key_code"]),
                },
            })
        categories.append({
            "id": f"remote.{slug_prefix}.{cat_slug_name}",
            "title": {"en": cat_en_name, "zh-Hans": cat_zh(cat_en_name)},
            "items": rows,
        })
    return {
        "bundleIdentifier": bundle_id,
        "i18n": {"defaultLocale": "en", "locales": ["en", "zh-Hans"]},
        "categories": categories,
    }


# ---------------------------------------------------------------------------
# App list from shortcuts index page
# ---------------------------------------------------------------------------
def get_app_list(html: str) -> list[tuple[str, str]]:
    """Extract (app_name, url_path) from the shortcuts index page."""
    apps: list[tuple[str, str]] = []
    for m in re.finditer(
        r'<a[^>]*href="(/shortcuts/[^"]+)"[^>]*>.*?<h2[^>]*>([^<]+)</h2>',
        html, re.DOTALL
    ):
        path = m.group(1)
        name = unescape(m.group(2)).strip()
        # Skip category pages
        if "/category/" in path:
            continue
        apps.append((name, path))
    return apps


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "presets"
    out_dir.mkdir(exist_ok=True)

    # Load existing bundle IDs from preset files
    for f in out_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text("utf-8"))
            bid = data.get("bundleIdentifier", "")
            if bid:
                EXISTING_BUNDLES.add(bid)
        except (json.JSONDecodeError, KeyError):
            pass

    print(f"[INFO] Found {len(EXISTING_BUNDLES)} existing presets, will skip them.", file=sys.stderr)
    print(f"[INFO] Existing: {sorted(EXISTING_BUNDLES)}", file=sys.stderr)

    # Fetch index page
    print("[INFO] Fetching app list from pie-menu.com/shortcuts ...", file=sys.stderr)
    index_html = fetch(f"{BASE_URL}/shortcuts")
    apps = get_app_list(index_html)
    print(f"[INFO] Found {len(apps)} apps on website.", file=sys.stderr)

    # Process each app
    new_count = 0
    skip_count = 0
    fail_count = 0

    for app_name, url_path in apps:
        app_url = f"{BASE_URL}{url_path}"
        slug_prefix = slug(app_name)

        # Fetch app page to get bundle ID first
        try:
            print(f"[{new_count + skip_count + fail_count + 1}/{len(apps)}] Fetching {app_name} ...", file=sys.stderr, end=" ")
            html = fetch(app_url)
        except Exception as e:
            print(f"FAILED ({e})", file=sys.stderr)
            fail_count += 1
            continue

        bundle_id = extract_bundle_from_html(html)
        if not bundle_id:
            print(f"NO BUNDLE ID, skipping", file=sys.stderr)
            fail_count += 1
            continue

        # Check if already exists
        if bundle_id in EXISTING_BUNDLES:
            print(f"SKIP (exists: {bundle_id})", file=sys.stderr)
            skip_count += 1
            time.sleep(0.5)
            continue

        # Parse sections
        sections = extract_sections(html, bundle_id)
        if not sections:
            print(f"NO SECTIONS found", file=sys.stderr)
            fail_count += 1
            time.sleep(1)
            continue

        # Build JSON
        data = build_json(bundle_id, slug_prefix, sections)
        n_items = sum(len(c["items"]) for c in data["categories"])

        # Write file
        fname = out_dir / f"{bundle_id.replace('/', '_')}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

        EXISTING_BUNDLES.add(bundle_id)
        new_count += 1
        print(f"OK → {fname.name} ({len(data['categories'])} cats, {n_items} items)", file=sys.stderr)

        # Be polite
        time.sleep(2)

    print(f"\n[DONE] New: {new_count}, Skipped: {skip_count}, Failed: {fail_count}", file=sys.stderr)


if __name__ == "__main__":
    main()
