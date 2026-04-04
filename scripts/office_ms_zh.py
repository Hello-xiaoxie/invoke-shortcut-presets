"""
Map Pie Menu / Microsoft Office shortcut descriptions (EN) to zh-Hans using
Microsoft Support article text (data/support + data/ms_*_en_to_zh.json).
"""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Pie（Mac 列表）与 Windows 版帮助文案不一致时，直接使用微软用语习惯的译文
WORD_PIE_ZH_OVERRIDES: dict[str, str] = {
    "Cut selected text or graphics": "将所选内容剪切到剪贴板中。",
    "Copy selected text or graphics to the Clipboard": "将所选内容复制到剪贴板中。",
    "Paste the Clipboard contents": "粘贴剪贴板的内容。",
    "Cut selected text to the clipboard": "将所选文本剪切到剪贴板。",
    "Cut selected text to the Clipboard": "将所选文本剪切到剪贴板。",
    "Find ": "查找",
    "Find": "查找",
    "Open the Spelling and Grammar dialog box": "打开“拼写和语法”对话框。",
    "Choose the Go To command (Edit menu)": (
        "显示“转到”对话框，导航到特定页面、书签、脚注、表格、批注、图形或其他位置。"
    ),
    "Go to the next window": "打开多个文档时切换到下一个文档窗口。",
    "Go to the previous window": "打开多个文档时切换到上一个文档窗口。",
    "Choose the Save As command (File menu).": "显示“另存为”对话框。",
    "Extend a selection": "开始扩展所选内容。",
    "Open the Thesaurus pane": "显示“同义词库”任务窗格。",
    "Find the next misspelling or grammatical error. The Check spelling as you type check box must be selected (Word menu, Preferences command, Spelling and Grammar).": (
        "查找下一个拼写或语法错误（需在“Word”>“偏好设置”>“拼写和语法”中启用“键入时检查拼写”。）"
    ),
    "Apply the List style when the cursor is at the beginning of a line": (
        "在光标位于行首时应用“列表”样式。"
    ),
    "Set lines as single-spaced": "对段落应用单倍行距。",
    "Set lines as double-spaced": "对段落应用双倍行距。",
    "Set lines as 1.5-line spacing": "对段落应用 1.5 倍行距。",
    "Add or remove one line of space directly preceding a paragraph": (
        "在段落前直接增加或删除一行间距。"
    ),
    "Change the formatting of characters (Font command, Format menu)": (
        "更改字符格式（“格式”菜单中的“字体”命令）。"
    ),
    "Format in all capital letters": "将文本更改为全部大写。",
    "Format in all small capital letters": "设置为小型大写字母格式。",
    "Move a single column line; Retain table width.": "移动单列线；保留表格宽度。",
    "Equally resize all columns to the right; Retain table width.": "等宽调整右侧所有列；保留表格宽度。",
    "Proportionally resize all columns to the right; Retain table width.": "按比例调整右侧所有列；保留表格宽度。",
    "Retain column sizes to the right; Change table width.": "保留右侧列宽；更改表格宽度。",
    "Look up selected text on the Internet": "在 Internet 上查找所选文本。",
    "Go to the beginning of the list of comments when in the Reviewing Pane": (
        "在审阅窗格中转到评论列表的开头。"
    ),
    "Go to the end of the list of comments when in the Reviewing Pane": (
        "在审阅窗格中转到评论列表的末尾。"
    ),
    "Change letters to uppercase, lowercase, or mixed case": "切换字母大小写（大写、小写或混合大小写）。",
    "Apply superscript formatting (automatic spacing)": "应用上标格式。",
    "Expand text under a heading": "展开标题下的文本。",
    "Collapse text under a heading": "折叠标题下的文本。",
}

# Pie 英文 -> 帮助英文表中的等价描述（用于 ms_word_en_to_zh 精确键）
WORD_PIE_TO_MS_EN: dict[str, str] = {
    "Undo the last action": "Undo the previous action.",
    "Redo the last action": "Redo the previous action, if possible.",
    "Copy selected text": "Copy the selected content to the Clipboard.",
    "Shrink a selection": (
        "Shift+F8: reduces the selection. For example, if a paragraph is selected, "
        "the selection size is reduced to one sentence."
    ),
    "Close the window": "Ctrl+F4: closes the active window.",
    "Expand or minimize the ribbon": "Expand or collapse the ribbon.",
    "Edit a bookmark": "Shift+F5: moves to the previous insertion point.",
}

EXCEL_PIE_ZH_OVERRIDES: dict[str, str] = {
    "Paste": "粘贴",
    "Copy": "复制",
    "Clear": "清除",
    "Save": "保存工作簿。",
    "Undo": "撤消最近的操作。",
    "Cut": "剪切所选内容。",
    "Bold": "应用加粗格式。",
    "Print": "打印",
    "New blank workbook": "新建空白工作簿。",
    "Fill Right": "使用“填充”将左侧单元格的内容和格式复制到右侧。",
    "Increase font size": "增大字号",
    "Decrease font size": "减小字号",
    "Enter a formula as an array formula": "以数组公式的形式输入公式。",
    "Insert an Excel 4.0 macro sheet": "插入 Excel 4.0 宏工作表。",
    "Move between unlocked cells on a protected sheet": "在受保护的工作表中，在未锁定的单元格之间移动。",
}

EXCEL_PIE_TO_MS_EN: dict[str, str] = {
    "Redo": "Redo the last action.",
    "Open Visual Basic": "Open Visual Basic",
    "Fill Down": "Use the Fill Down command to copy the contents and format of the topmost cell of a selected range into the cells below.",
    "Quit Excel": "Quit Excel",
    "Hide Excel.": "Hide Excel.",
    "Display the Save As dialog box": "Display the Save As dialog box.",
    "Display the Open dialog box": "Display the Open dialog box.",
    "Check spelling": "Check spelling",
    "Open the thesaurus": "Open the thesaurus",
    "Display the Help window": "Display the Help window",
    "Insert cells": "Insert cells",
    "Delete cells": "Delete cells",
    "Calculate all open workbooks": "Calculate all open workbooks",
    "Close window": "Close window",
    "Paste Special": "Paste Special",
    "Underline": "Underline",
    "Italic": "Italic",
    "Select All": "Select All",
}


def _is_shortcut_line(s: str) -> bool:
    s = s.strip()
    if not s or s.startswith("##"):
        return False
    if len(s) > 72:
        return False
    if s in ("Press", "按", "To do this", "执行的操作", "若要"):
        return False
    if "plus sign" in s.lower() or ("加号" in s and "快捷方式" in s):
        return False
    if re.match(r"^(Ctrl|Command|Option|Alt|Shift|⌘|⌥|⌃|⇧)\+", s, re.I):
        return True
    if re.match(r"^F\d+\b", s, re.I):
        return True
    if s in ("Esc", "Tab", "Delete", "Insert", "Home", "End", "Spacebar", "Return", "Enter"):
        return True
    if re.match(r"^Page (up|down)\b", s, re.I):
        return True
    if re.match(r"^箭头键", s):
        return True
    if re.match(r"^Shift\+F10", s, re.I):
        return True
    if re.match(r"^Tab 键", s):
        return True
    return False


def _action_indices(en_lines: list[str]) -> list[int]:
    out: list[int] = []
    for i in range(len(en_lines)):
        if not en_lines[i].strip() or en_lines[i].startswith("##"):
            continue
        j = i + 1
        while j < len(en_lines) and not en_lines[j].strip():
            j += 1
        if j < len(en_lines) and _is_shortcut_line(en_lines[j]):
            out.append(i)
    return out


def _tokenize(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


class OfficeMsZh:
    def __init__(self) -> None:
        self._word_map: dict[str, str] = {}
        self._excel_map: dict[str, str] = {}
        self._word_en_lines: list[str] = []
        self._word_zh_lines: list[str] = []
        self._excel_en_lines: list[str] = []
        self._excel_zh_lines: list[str] = []
        self._word_idx: list[int] = []
        self._excel_idx: list[int] = []
        wj = ROOT / "data" / "ms_word_en_to_zh.json"
        ej = ROOT / "data" / "ms_excel_en_to_zh.json"
        if wj.is_file():
            self._word_map = json.loads(wj.read_text(encoding="utf-8"))
        if ej.is_file():
            self._excel_map = json.loads(ej.read_text(encoding="utf-8"))
        we = ROOT / "data" / "support" / "word_en.txt"
        wz = ROOT / "data" / "support" / "word_zh.txt"
        ee = ROOT / "data" / "support" / "excel_en.txt"
        ez = ROOT / "data" / "support" / "excel_zh.txt"
        if we.is_file() and wz.is_file():
            self._word_en_lines = we.read_text(encoding="utf-8").splitlines()
            self._word_zh_lines = wz.read_text(encoding="utf-8").splitlines()
            self._word_idx = _action_indices(self._word_en_lines)
        if ee.is_file() and ez.is_file():
            self._excel_en_lines = ee.read_text(encoding="utf-8").splitlines()
            self._excel_zh_lines = ez.read_text(encoding="utf-8").splitlines()
            self._excel_idx = _action_indices(self._excel_en_lines)

    def word_title_zh(self, en: str) -> str | None:
        if en in WORD_PIE_ZH_OVERRIDES:
            return WORD_PIE_ZH_OVERRIDES[en]
        ms = WORD_PIE_TO_MS_EN.get(en, en)
        for k in (ms, ms.rstrip("."), ms + "."):
            if k in self._word_map:
                return self._word_map[k]
        m = difflib.get_close_matches(ms, list(self._word_map.keys()), n=1, cutoff=0.88)
        if m:
            return self._word_map[m[0]]
        if self._word_idx:
            pw = _tokenize(en)
            if len(pw) >= 2:
                best = (-1.0, -1.0, -1)
                for i in self._word_idx:
                    line = self._word_en_lines[i].strip()
                    lw = _tokenize(line)
                    overlap = len(pw & lw) / len(pw)
                    r = difflib.SequenceMatcher(None, en.lower(), line.lower()).ratio()
                    if overlap < 0.35:
                        continue
                    key = (overlap, r)
                    if key > (best[0], best[1]):
                        best = (overlap, r, i)
                if best[2] >= 0 and best[0] >= 0.45:
                    return self._word_zh_lines[best[2]].strip()
        return None

    def excel_title_zh(self, en: str) -> str | None:
        if en in EXCEL_PIE_ZH_OVERRIDES:
            return EXCEL_PIE_ZH_OVERRIDES[en]
        ms = EXCEL_PIE_TO_MS_EN.get(en, en)
        for k in (ms, ms.rstrip("."), ms + "."):
            if k in self._excel_map:
                return self._excel_map[k]
        m = difflib.get_close_matches(ms, list(self._excel_map.keys()), n=1, cutoff=0.88)
        if m:
            return self._excel_map[m[0]]
        if self._excel_idx:
            pw = _tokenize(en)
            if len(pw) >= 1:
                best = (-1.0, -1.0, -1)
                for i in self._excel_idx:
                    line = self._excel_en_lines[i].strip()
                    lw = _tokenize(line)
                    overlap = len(pw & lw) / max(len(pw), 1)
                    r = difflib.SequenceMatcher(None, en.lower(), line.lower()).ratio()
                    if overlap < 0.3:
                        continue
                    key = (overlap, r)
                    if key > (best[0], best[1]):
                        best = (overlap, r, i)
                if best[2] >= 0 and best[0] >= 0.4:
                    return self._excel_zh_lines[best[2]].strip()
        return None


_cached: OfficeMsZh | None = None


def get_office_ms_zh() -> OfficeMsZh:
    global _cached
    if _cached is None:
        _cached = OfficeMsZh()
    return _cached


def title_zh_for_bundle(bundle_id: str, en: str) -> str | None:
    if bundle_id == "com.microsoft.Word":
        return get_office_ms_zh().word_title_zh(en)
    if bundle_id == "com.microsoft.Excel":
        return get_office_ms_zh().excel_title_zh(en)
    return None
