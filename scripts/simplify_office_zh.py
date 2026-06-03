#!/usr/bin/env python3
"""Replace Word/Excel zh-Hans with short menu-style labels (not help paragraphs)."""
import json
import os
import re
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY = os.path.join(REPO, "review", "glossary.json")
APPS = ["com.microsoft.Word", "com.microsoft.Excel", "com.microsoft.Powerpoint", "com.microsoft.Outlook"]

EXACT = {
    # Word
    "Undo the last action": "撤消",
    "Redo the last action": "恢复",
    "Cut selected text or graphics": "剪切",
    "Cut selected text to the Clipboard": "剪切",
    "Cut selected text to the clipboard": "剪切",
    "Copy selected text or graphics to the Clipboard": "复制",
    "Copy selected text or graphics to the clipboard": "复制",
    "Copy selected text": "复制",
    "Copy text or graphics": "复制",
    "Paste the Clipboard contents": "粘贴",
    "Choose the Go To command (Edit menu)": "定位",
    "Open the Spelling and Grammar dialog box": "拼写和语法",
    "Choose the Save As command (File menu).": "另存为",
    "Expand or minimize the ribbon": "展开/折叠功能区",
    "Find": "查找",
    "Find the next misspelling or grammatical error": "查找拼写/语法错误",
    "Find the next misspelling or grammatical error. The Check spelling as you type check box must be selected (Word menu, Preferences command, Spelling and Grammar).": "查找拼写/语法错误",
    "Go to the next window": "下一个窗口",
    "Go to the previous window": "上一个窗口",
    "Edit a bookmark": "编辑书签",
    "Paste and match the formatting of the surrounding text": "粘贴并匹配格式",
    "Look up selected text on the Internet": "Internet 查找",
    "Paste a style": "粘贴样式",
    "Copy text or graphics to the Scrapbook": "复制到图文场",
    "Insert the copyright symbol": "插入版权符号",
    "Insert a LISTNUM field": "插入 LISTNUM 域",
    "Run GOTOBUTTON or MACROBUTTON from the field that displays the field results": "运行域按钮",
    "Repeat a Find or Go To action": "重复查找/定位",
    "Run a macro": "运行宏",
    "Apply bold formatting": "加粗",
    "Apply italic formatting": "斜体",
    "Apply an underline": "下划线",
    "Apply strike-through formatting": "删除线",
    "Apply superscript formatting (automatic spacing)": "上标",
    "Apply subscript formatting (automatic spacing)": "下标",
    "Center a paragraph": "居中",
    "Left-align a paragraph": "左对齐",
    "Right-align a paragraph": "右对齐",
    "Justify a paragraph": "两端对齐",
    "Increase the font size": "增大字号",
    "Decrease the font size": "减小字号",
    "Change the font": "更改字体",
    "Change letters to uppercase, lowercase, or mixed case": "切换大小写",
    "Change the case of letters": "切换大小写",
    "Apply the Heading 1 style": "标题 1",
    "Apply the Heading 2 style": "标题 2",
    "Apply the Heading 3 style": "标题 3",
    "Apply the Normal style": "正文",
    "Apply the List style when the cursor is at the beginning of a line": "列表样式",
    "Start AutoFormat": "自动套用格式",
    "Create a hanging indent": "悬挂缩进",
    "Remove a hanging indent": "取消悬挂缩进",
    "Remove a paragraph indent from the left": "减少缩进",
    "Indent a paragraph from the left": "增加缩进",
    "Insert a page break": "分页符",
    "Insert a column break": "分栏符",
    "Insert a line break": "换行",
    "Insert a comment": "插入批注",
    "Insert a footnote": "插入脚注",
    "Insert an endnote": "插入尾注",
    "Insert a row": "插入行",
    "Print a document": "打印",
    "Close the window": "关闭窗口",
    "Open the Thesaurus pane": "同义词库",
    "Paste special": "选择性粘贴",
    "Copy a style": "复制样式",
    "Create AutoText": "创建自动图文集",
    "Insert AutoText": "插入自动图文集",
    "Turn track changes on or off": "修订开/关",
    "Go to the beginning of a comment": "转到批注开头",
    "Go to the end of a comment": "转到批注末尾",
    "Go to the next field": "下一个域",
    "Go to the previous field": "上一个域",
    "Show the first line of body text or all body text": "显示/隐藏正文",
    "Choose the Go To command (Edit menu)": "定位",
    # Excel
    "Undo": "撤消",
    "Redo": "恢复",
    "Cut": "剪切",
    "Copy": "复制",
    "Paste": "粘贴",
    "Bold": "加粗",
    "Italic": "斜体",
    "Underline": "下划线",
    "Clear": "清除",
    "Save": "存储",
    "Close": "关闭",
    "Print": "打印",
    "Search": "搜索",
    "Select All": "全选",
    "Check spelling": "拼写检查",
    "Quit Excel": "退出 Excel",
    "Open Visual Basic": "Visual Basic",
    "Insert cells": "插入单元格",
    "Delete cells": "删除单元格",
    "Display the Go To dialog": "定位",
    "Display the\u00a0Go To\u00a0dialog box": "定位",
    "Insert a new sheet *": "插入工作表",
    "Insert a new sheet*": "插入工作表",
    "Switch to full screen view": "全屏",
    "Close the active workbook window": "关闭工作簿",
    "Maximize or restore the active window": "最大化/还原",
    "Cancel the command and close": "取消",
    "Edit the active cell": "编辑单元格",
    "Toggle the formula reference style between absolute, relative, and mixed": "切换引用样式",
    "New workbook from template": "从模板新建",
    "Calculate all open workbooks": "计算全部",
    "Calculate the active sheet": "计算活动工作表",
    "Display the\u00a0Format Cells\u00a0dialog box": "设置单元格格式",
    "Open the\u00a0Create names\u00a0dialog box": "定义名称",
    "Open the\u00a0Define Name\u00a0dialog box": "定义名称",
    "Display the\u00a0Save As\u00a0dialog box": "另存为",
    "Display the Save As dialog": "另存为",
    "Display the\u00a0Open\u00a0dialog box": "打开",
    "Display the Open dialog": "打开",
    "Display the Find dialog": "查找",
    "Display the\u00a0Replace\u00a0dialog box": "替换",
    "Display the\u00a0Help\u00a0window": "帮助",
    "Display the Help window": "帮助",
    "Display the Macro dialog": "宏",
    "Display the\u00a0Formula Builder": "公式生成器",
    "Open the Formula Builder": "公式生成器",
    "Fill Down": "向下填充",
    "Fill down": "向下填充",
    "Fill Right": "向右填充",
    "Fill to the right": "向右填充",
    "Fill Right": "向右填充",
    "Expand or minimize the ribbon": "展开/折叠功能区",
    "Insert an Excel 4.0 macro sheet": "插入宏表",
    "Insert a new chart sheet.": "插入图表工作表",
    "Insert a new chart sheet*": "插入图表工作表",
    "New blank workbook": "新建工作簿",
    "Hide Excel.": "隐藏 Excel",
    "Insert the AutoSum formula": "自动求和",
    "Group selected cells": "组合",
    "Ungroup selected cells": "取消组合",
    "Apply the general number format": "常规格式",
    "Apply the percentage format with no decimal places": "百分比格式",
    "Complete a cell entry": "确认输入",
    "Cancel a cell entry": "取消输入",
    "Paste Special": "选择性粘贴",
    "Define a name": "定义名称",
    "Open the Define Name dialog": "定义名称",
    "Open the Save dialog": "存储",
    "Open the thesaurus": "同义词库",
    "Open the\u00a0Smart Lookup\u00a0pane": "智能查找",
    "Move to next workbook": "下一个工作簿",
    "Move to the beginning of the sheet": "工作表开头",
    "Move to the last cell in use on the sheet": "最后已用单元格",
    "Scroll to display the active cell": "滚动到活动单元格",
    "Alternate between displaying cell values and displaying cell formulas": "显示值/公式",
    "Copy the value from the cell above the active cell into the cell or the formula bar": "复制上方单元格值",
    "Copy a formula from the cell above the active cell into the cell or the formula bar": "复制上方公式",
    "Perform the action assigned to the default command button (the button with the bold outline, often the OK button)": "默认按钮",
    "Copy the image of the screen and save it to a Screen Shot file on your desktop.": "屏幕截图",
    "Edit the active cell and then clear it, or delete the preceding character in the active cell as you edit the cell contents": "编辑单元格",
    "Edit the active cell and position the insertion point at the end of the line": "编辑单元格",
    "Display the Formula Builder after you type a valid function name in a formula": "函数参数",
    "Move from top to bottom within the selection (down)*": "在所选内下移",
    "Move from bottom to top within the selection (up)*": "在所选内上移",
    "Move from left to right within the selection, or move down one cell if only one column is selected": "在所选内右移",
    "Move from right to left within the selection, or move down one cell if only one column is selected": "在所选内左移",
    "Move to the next box, ⌥, control, or command": "下一选项",
    "Move to the previous box, ⌥, control, or command": "上一选项",
    "Move between unlocked cells on a protected sheet": "未锁定单元格间移动",
    "Delete the character to the left of the insertion point, or delete the selection": "删除左侧字符",
    # --- second pass: remaining long / English fallbacks ---
    "To the end of a document": "移到文档末尾",
    "To the beginning of a document": "移到文档开头",
    "To the previous insertion point": "上一插入点",
    "Switch to the next application": "下一个 App",
    "Switch to the previous application": "上一个 App",
    "Minimize the active window": "最小化窗口",
    "Exit a dialog or cancel an action": "退出对话框",
    "Start a new line in the same cell": "单元格内换行",
    "Cancel an entry in the cell or formula bar": "取消输入",
    "Cancel an entry in the cell or the formula bar": "取消输入",
    "Start a formula": "开始公式",
    "Enter the date": "输入日期",
    "Enter the time": "输入时间",
    "Create a table": "创建表格",
    "Increase font size": "增大字号",
    "Decrease font size": "减小字号",
    "Align center": "居中",
    "Align left": "左对齐",
    "Apply the number format with two decimal places, thousands separator, and minus sign (-) for negative values": "数字格式",
    "Apply the outline border around the selected cells": "单元格边框",
    "Add an outline border to the right of the selection": "右边框",
    "Add an outline border to the left of the selection": "左边框",
    "Add an outline border to the top of the selection": "上边框",
    "Add an outline border to the bottom of the selection": "下边框",
    "Remove outline borders": "清除边框",
    "Apply or remove underscoring": "下划线",
    "Enter a formula as an array formula": "数组公式",
    "Extend the selection": "扩展所选",
    "Add to the selection": "添加到所选",
    "Extend a selection": "扩展所选",
    "Shrink a selection": "缩小所选",
    "Switch between a field code and its result": "切换域代码/结果",
    "Switch between a field code and its result.": "切换域代码/结果",
    "Switch between all field codes and their results": "切换全部域",
    "Turn on extend mode": "扩展模式开",
    "Turn off extend mode": "扩展模式关",
    "Reduce the size of a selection": "缩小所选",
    "Set lines as single-spaced": "单倍行距",
    "Set lines as double-spaced": "双倍行距",
    "Set lines as 1.5-line spacing": "1.5 倍行距",
    "Add or remove one line of space directly preceding a paragraph": "段前空一行",
    "Change the formatting of characters (Font command, Format menu)": "字符格式",
    "Double-underline text": "双下划线",
    "Update selected fields": "更新所选域",
    "Update selected fields.": "更新所选域",
    "Unlink a field": "取消域链接",
    "Lock a field": "锁定域",
    "Unlock a field": "解锁域",
    "Promote a paragraph": "提升段落",
    "Demote a paragraph": "降低段落",
    "Demote to body text": "降为正文",
    "Show all headings with the specified heading level": "显示指定标题",
    "Go to the beginning of the list of comments when in the Reviewing Pane": "批注列表开头",
    "Go to the end of the list of comments when in the Reviewing Pane": "批注列表末尾",
    "Start a new paragraph": "新段落",
    "Equally resize all columns to the right;\xa0Retain table width.": "等宽调整列",
    "Proportionally resize all columns to the right;\xa0Retain table width.": "比例调整列",
    "Extend a selection as a block selection": "块扩展所选",
    "Update linked information in a Word source document": "更新链接信息",
    "Create an AutoText entry": "创建自动图文集",
    "Move down one screen (scrolling)": "下滚一屏",
    "Move up one screen (scrolling)": "上滚一屏",
    "Select one screen down": "下选一屏",
    "Select one screen up": "上选一屏",
    "Move a single column line; Retain table width.": "移动列线",
    "Format in all capital letters": "全部大写",
    "Format in all small capital letters": "小型大写",
    "Insert a nonbreaking space": "不间断空格",
    "Insert a nonbreaking hyphen": "不间断连字符",
    "Insert an ellipsis": "省略号",
    "Insert the trademark symbol": "商标符号",
    "Insert the registered trademark symbol": "注册商标",
    "Insert the contents of the Spike": "插入图文场内容",
    "Cut the selection to the Spike": "剪切到图文场",
    "Cut to the Spike": "剪切到图文场",
    "Paste the Spike contents": "粘贴图文场",
    "Collapse text under a heading": "折叠标题下文本",
    "Expand text under a heading": "展开标题下文本",
    "Expand all body text and headings or collapse all body text": "展开/折叠正文",
    "Select to the end of a window": "选到窗口末尾",
    "Select to select the entire document": "全选文档",
    "Move to the top of the next page": "下一页顶部",
    "Move to the top of the previous page": "上一页顶部",
    "Move one cell to the left (in a table)": "表格左移一格",
    "Move one cell to the right (in a table)": "表格右移一格",
    "Move to the first cell in the column": "列首单元格",
    "Move to the last cell in the column": "列末单元格",
    "Move to the first cell in the row": "行首单元格",
    "Move to the last cell in the row": "行末单元格",
    "Move to the preceding cell": "上一单元格",
    "Move to the preceding or next row": "上/下一行",
    "Move to the previous insertion point": "上一插入点",
    "Insert a Tab character in a cell": "单元格内 Tab",
    "Insert a new paragraph in a cell": "单元格内新段",
    "Insert an empty field": "插入空域",
    "Insert a DATE field": "插入 DATE 域",
    "Insert a PAGE field": "插入 PAGE 域",
    "Insert a TIME field": "插入 TIME 域",
    "Display a contextual menu": "上下文菜单",
    "Display a contextual menu, or \"right click\" menu": "右键菜单",
    "Display or hide outline symbols": "显示/隐藏大纲符号",
    "Display the AutoComplete list": "自动完成列表",
    "Fill the selected cell range with the text that you type": "填充输入文本",
    "Move clockwise to the next corner of the selection": "选区下一角",
    "Move down one screen": "下滚一屏",
    "Move up one screen": "上滚一屏",
    "Move one screen to the left": "左滚一屏",
    "Move one screen to the right": "右滚一屏",
    "Move to the beginning of the line": "移到行首",
    "Move to the beginning of the row": "移到行首",
    "Move to the Search Sheet dialog": "搜索工作表",
    "Open and edit a cell comment": "编辑批注",
    "Insert or edit a cell comment": "插入/编辑批注",
    "Insert a comment": "插入批注",
    "Insert a hyperlink": "插入超链接",
    "Insert a line break in a cell": "单元格换行",
    "Paste text into the active cell": "粘贴到单元格",
    "Undo the last action": "撤消",
    "Apply the currency format with two decimal places (negative numbers appear in red with parentheses)": "货币格式",
    "Apply the date format with the day, month, and year": "日期格式",
    "Apply the exponential number format with two decimal places": "科学计数",
    "Apply the time format with the hour and minute, and indicate AM or PM": "时间格式",
}

_EXTRA = os.path.join(REPO, "review", "_work", "office_ppt_outlook_exact.json")
if os.path.exists(_EXTRA):
    _extra = json.load(open(_EXTRA, encoding="utf-8"))
    EXACT.update(_extra)
    for _k, _v in list(_extra.items()):
        EXACT[_k.replace("\u00a0", " ")] = _v
        EXACT[_k.replace(" ", "\u00a0")] = _v

# Regex patterns -> short label (applied after stripping parentheticals)
PATTERNS = [
    (r"^Move one character to the (left|right)$", lambda m: f"{'左' if m.group(1)=='left' else '右'}移一个字符"),
    (r"^Move one word to the (left|right)$", lambda m: f"{'左' if m.group(1)=='left' else '右'}移一词"),
    (r"^Select one character to the (left|right)$", lambda m: f"{'左' if m.group(1)=='left' else '右'}选一个字符"),
    (r"^Select one word to the (left|right)$", lambda m: f"{'左' if m.group(1)=='left' else '右'}选一词"),
    (r"^Delete one character to the (left|right)$", lambda m: f"{'左' if m.group(1)=='right' else '右'}删一字符"),
    (r"^Delete one word to the (left|right)$", lambda m: f"{'左' if m.group(1)=='left' else '右'}删一词"),
    (r"^Move one paragraph (up|down)$", lambda m: f"{'上' if m.group(1)=='up' else '下'}移一段"),
    (r"^Move (up|down) one line$", lambda m: f"{'上' if m.group(1)=='up' else '下'}移一行"),
    (r"^Move to the (beginning|end) of a line$", lambda m: f"移到行{'首' if m.group(1)=='beginning' else '尾'}"),
    (r"^Move to the (top|beginning) of", lambda m: "移到开头"),
    (r"^Move to the (end|last)", lambda m: "移到末尾"),
    (r"^Select to the (beginning|end) of a (line|paragraph|document)$", lambda m: f"选到{'行' if m.group(2)=='line' else '段' if m.group(2)=='paragraph' else '文'}{'首' if m.group(1)=='beginning' else '尾'}"),
    (r"^Insert a (.+) field$", lambda m: f"插入 {m.group(1).upper()} 域"),
    (r"^Apply or remove (bold|italic) formatting$", lambda m: f"{'加粗' if 'bold' in m.group(1) else '斜体'}"),
    (r"^Apply or remove (strikethrough|underscoring) formatting$", lambda m: "删除线" if "strike" in m.group(1) else "下划线"),
    (r"^Apply the (currency|date|time|percentage|general number|exponential number) format", lambda m: {
        "currency": "货币格式", "date": "日期格式", "time": "时间格式",
        "percentage": "百分比格式", "general number": "常规格式", "exponential number": "科学计数",
    }.get(m.group(1), "数字格式")),
    (r"^Hide (a |selected )?(row|column)s?$", lambda m: f"隐藏{'行' if m.group(2)=='row' else '列'}"),
    (r"^Unhide (a |selected )?(row|column)s?$", lambda m: f"取消隐藏{'行' if m.group(2)=='row' else '列'}"),
    (r"^Complete a cell entry and move (up|down|forward)", lambda m: f"确认并{'上' if m.group(1)=='up' else '下' if m.group(1)=='down' else '前'}移"),
    (r"^Complete a cell entry and move to the (left|right)", lambda m: f"确认并{'左' if m.group(1)=='left' else '右'}移"),
]

# Simple word replacements for fallback (keep under ~12 CJK chars)
WORDS = {
    "undo": "撤消", "redo": "恢复", "cut": "剪切", "copy": "复制", "paste": "粘贴",
    "find": "查找", "replace": "替换", "save": "存储", "open": "打开", "close": "关闭",
    "print": "打印", "bold": "加粗", "italic": "斜体", "underline": "下划线",
    "insert": "插入", "delete": "删除", "select": "选择", "move": "移动",
    "display": "显示", "edit": "编辑", "format": "格式", "cell": "单元格",
    "row": "行", "column": "列", "sheet": "工作表", "workbook": "工作簿",
    "paragraph": "段落", "line": "行", "word": "词", "character": "字符",
    "comment": "批注", "field": "域", "style": "样式", "table": "表格",
    "dialog": "对话框", "window": "窗口", "selection": "所选", "active": "活动",
    "expand": "展开", "collapse": "折叠", "indent": "缩进", "font": "字体",
    "heading": "标题", "bookmark": "书签", "macro": "宏", "formula": "公式",
    "chart": "图表", "border": "边框", "fill": "填充", "group": "组合",
    "ungroup": "取消组合", "spell": "拼写", "grammar": "语法",
}


def _strip_en(en: str) -> str:
    s = en.split(".")[0].strip()
    s = re.sub(r"\s*\([^)]*\)", "", s).strip()
    return s


def shorten(en: str) -> str:
    en = en.strip().replace("\u00a0", " ")
    if en in EXACT:
        return EXACT[en]
    base = _strip_en(en)
    if base in EXACT:
        return EXACT[base]
    for pat, repl in PATTERNS:
        m = re.match(pat, base, re.I)
        if m:
            return repl(m) if callable(repl) else repl
    # fallback: first 3-4 meaningful English words -> rough Chinese, max 14 chars
    low = base.lower()
    for key, zh in sorted(WORDS.items(), key=lambda x: -len(x[0])):
        if low.startswith(key + " ") or low == key:
            rest = base[len(key):].strip()
            if not rest:
                return zh
            # one more word
            w2 = rest.split()[0].lower() if rest.split() else ""
            if w2 in WORDS:
                out = zh + WORDS[w2]
                return out[:14] if len(out) > 14 else out
            return zh
    # last resort: never leave English — compress to ≤12 chars
    parts = re.findall(r"[A-Za-z]+", base.lower())
    if parts:
        zh_bits = []
        for p in parts[:4]:
            if p in WORDS:
                zh_bits.append(WORDS[p])
            elif len(zh_bits) < 2:
                zh_bits.append(p[:4])
        if zh_bits:
            out = "".join(zh_bits)
            return out[:12]
    return base[:12]


def apply_app(bundle_id: str) -> int:
    path = os.path.join(REPO, "presets", f"{bundle_id}.json")
    data = json.load(open(path, encoding="utf-8"))
    n = 0
    for cat in data["categories"]:
        for item in cat["items"]:
            en = item["title"]["en"].strip()
            short = shorten(en)
            if item["title"]["zh-Hans"] != short:
                item["title"]["zh-Hans"] = short
                n += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return n


def main():
    total = 0
    glossary = json.load(open(GLOSSARY, encoding="utf-8"))
    for bid in APPS:
        path = os.path.join(REPO, "presets", f"{bid}.json")
        data = json.load(open(path, encoding="utf-8"))
        for cat in data["categories"]:
            for item in cat["items"]:
                en = item["title"]["en"].strip()
                glossary[en] = item["title"]["zh-Hans"]  # will update after apply
        n = apply_app(bid)
        total += n
        data = json.load(open(path, encoding="utf-8"))
        for cat in data["categories"]:
            for item in cat["items"]:
                glossary[item["title"]["en"].strip()] = item["title"]["zh-Hans"]
        print(f"{bid}: updated {n} entries")
    json.dump(glossary, open(GLOSSARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    subprocess.run(["python3", os.path.join(REPO, "scripts", "build_review_table.py")], check=True)
    # stats
    import csv
    rows = [r for r in csv.DictReader(open(os.path.join(REPO, "review", "review.csv"), encoding="utf-8-sig"))
            if r["bundle_id"] in APPS]
    long = sum(1 for r in rows if len(r["action_zh_final"]) > 16)
    mx = max((len(r["action_zh_final"]), r["action_en"], r["action_zh_final"]) for r in rows)
    print(f"total updated: {total} | rows>16chars: {long} | longest: {mx[0]} '{mx[2]}'")


if __name__ == "__main__":
    main()
