#!/usr/bin/env python3
"""Print a per-app worksheet: untranslated strings + default-eligible items.

Usage: python3 scripts/app_worksheet.py <bundle_id> [<bundle_id> ...]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from build_review_table import (  # noqa: E402
    display_string, is_usable, default_score, needs_translation,
)

glossary = {}
gp = os.path.join(REPO, "review", "glossary.json")
if os.path.exists(gp):
    glossary = json.load(open(gp, encoding="utf-8"))


def main():
    for bid in sys.argv[1:]:
        path = os.path.join(REPO, "presets", bid + ".json")
        if not os.path.exists(path):
            print(f"!! missing {path}")
            continue
        data = json.load(open(path, encoding="utf-8"))
        print(f"\n===== {bid} =====")
        print("--- 需翻译的唯一英文串(未在glossary中) ---")
        seen = set()
        for c in data["categories"]:
            for it in c["items"]:
                en = it["title"]["en"].strip()
                zh = it["title"]["zh-Hans"]
                if needs_translation(en, zh) and en not in glossary and en not in seen:
                    seen.add(en)
                    print(f'  "{en}": "",   # 原: {zh}')
        print("--- 默认候选(default_eligible, 按分数排序, 选4-6个跨分类) ---")
        for c in data["categories"]:
            elig = [it for it in c["items"] if is_usable(it["shortcutConfiguration"])]
            elig.sort(key=default_score, reverse=True)
            if not elig:
                continue
            print(f'  [{c["title"].get("en","")}]')
            for it in elig[:8]:
                print(f'    {default_score(it):2}  {display_string(it["shortcutConfiguration"]):7} '
                      f'{it["title"]["en"][:34]:34} {it["id"]}')


if __name__ == "__main__":
    main()
