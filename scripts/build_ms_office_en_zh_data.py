#!/usr/bin/env python3
"""
Build ms_word_en_to_zh.json and ms_excel_en_zh.json from Microsoft Support
markdown exports in data/support/*.txt (zh-cn + en-us pairs).

Sources (human-exported / fetched markdown):
  - Word: keyboard shortcuts article (same structure EN/ZH).
  - Excel: pair rows from "## Frequently used shortcuts" onward where both
    sides register a shortcut line (order preserved).

Run from repo root:
  python3 scripts/build_ms_office_en_zh_data.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORT = ROOT / "data" / "support"


def action_before_shortcut(lines: list[str], si: int) -> str:
    j = si - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    return lines[j].strip() if j >= 0 else ""


def is_shortcut_line(s: str) -> bool:
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


def pair_word(en_path: Path, zh_path: Path) -> dict[str, str]:
    en = en_path.read_text(encoding="utf-8").splitlines()
    zh = zh_path.read_text(encoding="utf-8").splitlines()
    out: dict[str, str] = {}
    for i in range(min(len(en), len(zh))):
        if not is_shortcut_line(en[i]):
            continue
        if en[i].strip() != zh[i].strip():
            continue
        ae = action_before_shortcut(en, i)
        az = action_before_shortcut(zh, i)
        if not ae or not az or ae.startswith("##"):
            continue
        for k in (ae, ae.rstrip(".")):
            out[k] = az
    return out


def pair_excel(en_path: Path, zh_path: Path, start_line_1_indexed: int = 77) -> dict[str, str]:
    en = en_path.read_text(encoding="utf-8").splitlines()
    zh = zh_path.read_text(encoding="utf-8").splitlines()
    start = start_line_1_indexed - 1
    out: dict[str, str] = {}
    for i in range(start, min(len(en), len(zh))):
        if not is_shortcut_line(en[i]) or not is_shortcut_line(zh[i]):
            continue
        ae = action_before_shortcut(en, i)
        az = action_before_shortcut(zh, i)
        if not ae or not az or ae.startswith("##"):
            continue
        for k in (ae, ae.rstrip(".")):
            out[k] = az
    return out


def main() -> None:
    w_en = SUPPORT / "word_en.txt"
    w_zh = SUPPORT / "word_zh.txt"
    e_en = SUPPORT / "excel_en.txt"
    e_zh = SUPPORT / "excel_zh.txt"
    for p in (w_en, w_zh, e_en, e_zh):
        if not p.is_file():
            print("missing", p, file=sys.stderr)
            sys.exit(1)
    word_map = pair_word(w_en, w_zh)
    excel_map = pair_excel(e_en, e_zh)
    data_dir = ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "ms_word_en_to_zh.json").write_text(
        json.dumps(word_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (data_dir / "ms_excel_en_to_zh.json").write_text(
        json.dumps(excel_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("word entries", len(word_map), file=sys.stderr)
    print("excel entries", len(excel_map), file=sys.stderr)


if __name__ == "__main__":
    main()
