#!/usr/bin/env python3
"""Fix zh-Hans labels: remove CJK word spaces, shorten long labels, phrase overrides.

Updates presets/*.json and review/glossary.json, then regenerates review.csv.
"""
from __future__ import annotations

import json
import os
import re
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = os.path.join(REPO, "presets")
GLOSSARY = os.path.join(REPO, "review", "glossary.json")
WORK = os.path.join(REPO, "review", "_work")
OFFICE_BUNDLE_IDS = [
    "com.microsoft.Word",
    "com.microsoft.Excel",
    "com.microsoft.Powerpoint",
    "com.microsoft.Outlook",
]
MAX_LEN = 14

# Exact English -> short menu-style Chinese (official terms where known)
PHRASE_OVERRIDES: dict[str, str] = {
    # --- Safari / Chrome / browser ---
    "Switch to another Safari window": "切换 Safari 窗口",
    "Change Safari preferences": "Safari 设置",
    # --- GarageBand ---
    "Minimize the GarageBand window": "最小化窗口",
    "Show GarageBand preferences": "GarageBand 设置",
    "Hide GarageBand": "隐藏 GarageBand",
    "Quit GarageBand": "退出 GarageBand",
    "Show your garageband library": "显示资源库",
    "Add selected region to the Apple Loops Library": "添加到循环库",
    # --- iMovie ---
    "Open iMovie preferences": "iMovie 设置",
    "Go to iMovie theater": "iMovie 影院",
    "Switch to Clip Viewer or Timeline Viewer": "切换检视器",
    # --- Excel ---
    "Cycle through absoluteness of selected references": "切换引用绝对性",
    "Cycle through absoluteness of selected references of start an d end of cell": "切换起止引用",
    # --- Keynote ---
    "Go to previous slide(Slide Switcher)": "上一张幻灯片",
    # --- Numbers ---
    "Go to previous sheet if selected in sheets pane": "上一张表格",
    "Go to next sheet if selected in sheets pane": "下一张表格",
    # --- Pages ---
    "Open new document (You can choose the type of document you want to open in Pages Preferences.)": "打开新文稿",
    "Select all table borders or cell content, depending on initial selection": "全选表格边框/内容",
    "Copy contents of selected cells or whole table, if table is selected": "复制单元格/表格",
    "Cut contents of selected cells or whole table, if table is selected": "剪切单元格/表格",
    "Delete selection (whole table, border or border segment, or contents of selected cells)": "删除所选内容",
    "Hide Pages": "隐藏 Pages",
    "Quit Pages": "退出 Pages",
    "Center text": "文本居中",
    # --- Android Studio ---
    "Apply Changes and Restart Activity": "应用更改并重启",
    # --- WeChat / meeting ---
    "Voice Input to Text (hold Fn, or Fn+Control)": "语音输入",
    "Start / Stop Screen Sharing (global shortcut)": "开关屏幕共享",
    # --- Notion / Luki ---
    "Modify the current block (open page, check/uncheck to-do, open/close list item, etc.)": "修改当前块",
    "Expand or close all toggles in a toggle list": "展开/折叠全部",
    "Edit all selected cards at once in board view": "批量编辑卡片",
    "Edit any text inside a selected block (or open a page inside a page)": "编辑块内文本",
    "Create a new page or turn whatever you have on a line into a page": "新建/转为页面",
    # --- WeWork ---
    "Extend Selection to Data Edge (⌘⇧+Arrow)": "扩展至数据边缘",
    # --- Xcode ---
    "Comment Selection": "注释所选",
    "Next Issue": "下一问题",
    "Previous Issue": "上一问题",
    "File Template": "文件模板",
    # --- Final Cut Pro ---
    "Log clip": "记录片段",
    "Open selected file": "打开所选",
    "Open item editor": "项目编辑器",
    "Next edit": "下一编辑点",
    "Previous edit": "上一编辑点",
    # --- VS Code (JSON leftovers not in batch2 glossary) ---
    "Insert Cursor Above": "在上方插入光标",
    "Insert Cursor Below": "在下方插入光标",
    "Copy Line Up": "向上复制行",
    "Copy Line Down": "向下复制行",
    "Insert Line Above": "在上方插入行",
    "Insert Line Below": "在下方插入行",
    "Rename Symbol": "重命名符号",
    "Select current line": "选择当前行",
    # --- Keynote / Numbers ---
    "Duplicate object": "复制对象",
    "Selected Previous cell": "选择上一单元格",
    "Align text left": "文本左对齐",
    "Align text right": "文本右对齐",
    "Font Zoom in/Zoom out": "字体缩放",
    # --- Blender ---
    "Next frame": "下一帧",
    "Previous frame": "上一帧",
    "Edit/object mode": "编辑/对象模式",
    # --- Chrome ---
    "Log in as a different user, browse as a Guest, or access payment and password info": "用户/访客/密码",
    "Delete the character to the left of the insertion point, or delete the selection": "左删",
    "Delete the character to the right side of the cursor, or delete the selected text": "右删",
    # --- Logic Pro (keep notation) ---
    "1/1,2,4..128 Note": "1/1、2、4…128 音符",
}


def rebuild_glossary() -> dict[str, str]:
    """Merge batch overlays + office short labels; batch1 Word/Excel long entries are excluded."""
    g: dict[str, str] = {}
    for name in ("batch1_glossary.json", "batch2_glossary.json", "batch3_glossary.json", "office_ppt_outlook_exact.json"):
        path = os.path.join(WORK, name)
        if os.path.exists(path):
            g.update(json.load(open(path, encoding="utf-8")))
    for bid in OFFICE_BUNDLE_IDS:
        path = os.path.join(PRESETS, f"{bid}.json")
        if not os.path.exists(path):
            continue
        data = json.load(open(path, encoding="utf-8"))
        for cat in data.get("categories", []):
            for item in cat.get("items", []):
                g[item["title"]["en"].strip()] = item["title"]["zh-Hans"]
    g.update(PHRASE_OVERRIDES)
    return g


def normalize_zh(zh: str) -> str:
    zh = zh.strip().rstrip(".")
    # Remove spaces between CJK characters (word-by-word translation artifact)
    zh = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", zh)
    zh = re.sub(r"\s+", " ", zh).strip()
    return zh


def improve(en: str, zh: str) -> str:
    en = en.strip()
    if en in PHRASE_OVERRIDES:
        return PHRASE_OVERRIDES[en]
    return normalize_zh(zh)


def main():
    glossary = rebuild_glossary()
    overlay_keys = set(glossary)

    json_changed = 0
    glossary_changed = 0

    for fname in sorted(os.listdir(PRESETS)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(PRESETS, fname)
        data = json.load(open(path, encoding="utf-8"))
        file_n = 0
        for cat in data.get("categories", []):
            for item in cat.get("items", []):
                en = item["title"]["en"].strip()
                old = item["title"].get("zh-Hans", "")
                new = improve(en, old)
                if new != old:
                    item["title"]["zh-Hans"] = new
                    file_n += 1
                if en in overlay_keys:
                    g_old = glossary.get(en)
                    g_new = improve(en, glossary.get(en, new))
                    if g_new != g_old:
                        glossary[en] = g_new
                        glossary_changed += 1
        if file_n:
            json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            open(path, "a", encoding="utf-8").write("\n")
            json_changed += file_n
            if file_n:
                print(f"  {fname}: {file_n} labels fixed")

    json.dump(glossary, open(GLOSSARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print(f"JSON items updated: {json_changed} | glossary entries updated: {glossary_changed}")

    subprocess.run(["python3", os.path.join(REPO, "scripts", "build_review_table.py")], check=True)


if __name__ == "__main__":
    main()
