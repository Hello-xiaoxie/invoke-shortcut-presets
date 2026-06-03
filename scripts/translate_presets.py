#!/usr/bin/env python3
"""LLM batch re-translation of zh-Hans titles in presets/*.json.

Finds every item whose zh-Hans is empty, equals English, or still contains
Latin letters (中英混杂 / 未翻), sends them to an LLM in batches, and writes the
cleaned Simplified Chinese back into the JSON (source of truth). Idempotent and
re-runnable; honors a term whitelist so brand / proper nouns stay in English.

Usage:
  export OPENAI_API_KEY=...      # or ANTHROPIC_API_KEY=...
  python3 scripts/translate_presets.py                # all apps
  python3 scripts/translate_presets.py --apps com.figma.Desktop com.google.Chrome
  python3 scripts/translate_presets.py --dry-run      # only list what would change

After running, regenerate the review table:
  python3 scripts/build_review_table.py
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PRESETS_DIR = os.path.join(REPO, "presets")
WHITELIST_PATH = os.path.join(HERE, "translation_whitelist.json")
BATCH = 40

SYSTEM_PROMPT = (
    "你是 macOS 软件本地化专家。把应用功能名（菜单项/快捷键动作）翻译成简体中文。"
    "要求：1) 用中文软件界面里习惯的术语；2) 不要中英混杂，除非是必须保留的专有名词；"
    "3) 简洁，不加句号；4) 保留占位符与符号原样；5) 下列词保留英文原文不翻："
)


def load_whitelist():
    if os.path.exists(WHITELIST_PATH):
        return json.load(open(WHITELIST_PATH, encoding="utf-8"))
    return []


def needs_translation(en: str, zh: str) -> bool:
    if zh.strip() == "" or zh.strip() == en.strip():
        return True
    return bool(re.search(r"[A-Za-z]", zh))


def collect(apps):
    tasks = []  # (path, data, cat_idx, item_idx, en, zh)
    files = sorted(glob.glob(os.path.join(PRESETS_DIR, "*.json")))
    for path in files:
        bid = os.path.basename(path)[:-5]
        if apps and bid not in apps:
            continue
        data = json.load(open(path, encoding="utf-8"))
        for ci, c in enumerate(data.get("categories", [])):
            for ii, it in enumerate(c["items"]):
                en = it["title"].get("en", "")
                zh = it["title"].get("zh-Hans", "")
                if needs_translation(en, zh):
                    tasks.append([path, data, ci, ii, en, zh])
    return tasks


def call_llm(prompt: str) -> str:
    if os.environ.get("OPENAI_API_KEY"):
        from openai import OpenAI
        client = OpenAI()
        r = client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return r.choices[0].message.content
    if os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic
        client = anthropic.Anthropic()
        r = client.messages.create(
            model=os.environ.get("LLM_MODEL", "claude-3-5-haiku-latest"),
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.content[0].text
    sys.exit("未检测到 OPENAI_API_KEY 或 ANTHROPIC_API_KEY，无法调用 LLM。")


def translate_batch(items, whitelist):
    numbered = "\n".join(f"{i}. {en}" for i, (en, _) in enumerate(items))
    prompt = (
        SYSTEM_PROMPT + "、".join(whitelist) + "\n\n"
        "把下面每一行翻译成简体中文，按相同编号原样返回 JSON 数组，"
        '格式 [{"i":0,"zh":"..."}]，只返回 JSON：\n' + numbered
    )
    raw = call_llm(prompt)
    m = re.search(r"\[.*\]", raw, re.S)
    arr = json.loads(m.group(0)) if m else []
    out = {int(o["i"]): o["zh"].strip() for o in arr if "i" in o and "zh" in o}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apps", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    whitelist = load_whitelist()
    tasks = collect(set(args.apps) if args.apps else None)
    print(f"需要翻译的条目: {len(tasks)}")
    if args.dry_run:
        for t in tasks[:40]:
            print(f"  [{os.path.basename(t[0])[:-5]}] {t[4]}  ←  {t[5]!r}")
        print("... (dry-run, 未调用 LLM, 未写入)")
        return

    changed_files = set()
    for start in range(0, len(tasks), BATCH):
        chunk = tasks[start:start + BATCH]
        pairs = [(t[4], t[5]) for t in chunk]
        result = translate_batch(pairs, whitelist)
        for i, t in enumerate(chunk):
            if i in result and result[i]:
                path, data, ci, ii = t[0], t[1], t[2], t[3]
                data["categories"][ci]["items"][ii]["title"]["zh-Hans"] = result[i]
                changed_files.add(path)
        print(f"  进度 {min(start + BATCH, len(tasks))}/{len(tasks)}")

    for path in changed_files:
        data = next(t[1] for t in tasks if t[0] == path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print(f"写回 {len(changed_files)} 个文件。记得重跑 build_review_table.py")


if __name__ == "__main__":
    main()
