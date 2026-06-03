#!/usr/bin/env python3
"""Build review.csv from presets/*.json for human review.

Source of truth is always the JSON files under presets/. This script only
*reads* them and emits a flat CSV with review/flag columns. It re-implements
the macOS app's shortcut filter + default-selection logic (see
ShortcutPresetCatalog.swift / KeyboardShortcutConfiguration.swift) so the
table reflects exactly what the app would show / auto-pick today.

Columns:
  app_name, bundle_id, category_zh, category_en, action_en, action_zh,
  action_zh_new, key, is_default_suggested, is_default_current_algo,
  default_eligible, single_key, needs_translation, dup_group, item_id

  - action_zh_new       : left blank, to be filled by the LLM re-translation pass
  - is_default_suggested: left blank (✓), curated 4-6 defaults to be filled by LLM
  - is_default_current_algo: ✓ = what the app's current heuristic would auto-pick
"""
import csv
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PRESETS_DIR = os.path.join(REPO, "presets")
OUT_CSV = os.path.join(REPO, "review", "review.csv")
# Review overlays (proposed changes shown in CSV before committing to JSON):
#   glossary.json  : { "<English action>": "<proposed zh-Hans>" }  global term memory
#   defaults.json  : { "<bundle_id>": ["<item_id>", ...] }         curated 4-6 defaults
GLOSSARY_PATH = os.path.join(REPO, "review", "glossary.json")
DEFAULTS_PATH = os.path.join(REPO, "review", "defaults.json")

# Carbon modifier bit masks (match KeyboardShortcutConfiguration.swift)
CMD = 256
SHIFT = 512
OPTION = 2048
CONTROL = 4096
FN = 1 << 24

GLYPH = [(CONTROL, "\u2303"), (OPTION, "\u2325"), (SHIFT, "\u21e7"), (CMD, "\u2318")]

with open(os.path.join(HERE, "app_names.json"), encoding="utf-8") as f:
    APP_NAMES = json.load(f)


def standard_modifiers(mods: int) -> int:
    return mods & ~FN


def display_string(sc: dict) -> str:
    key = sc.get("displayKey", "")
    if key == "" or sc.get("keyCode", 0xFFFF) == 0xFFFF:
        return ""
    glyphs = "".join(g for bit, g in GLYPH if sc.get("carbonModifiers", 0) & bit)
    if sc.get("carbonModifiers", 0) & FN:
        glyphs += "fn"
    return glyphs + key


def is_single_key(sc: dict) -> bool:
    """No standard modifier keys (Cmd/Ctrl/Opt/Shift)."""
    return standard_modifiers(sc.get("carbonModifiers", 0)) == 0


def is_plain_character(sc: dict) -> bool:
    key = sc.get("displayKey", "")
    return len(key) == 1 and bool(re.match(r"[A-Za-z0-9]", key))


def uses_only_weak_modifiers(sc: dict) -> bool:
    mods = standard_modifiers(sc.get("carbonModifiers", 0))
    if mods == 0:
        return False
    return (mods & ~(SHIFT | OPTION)) == 0


def is_usable(sc: dict) -> bool:
    """Re-implements ShortcutPresetDefaultBuilder.isUsableShortcutPreset."""
    if sc.get("keyCode", 0xFFFF) == 0xFFFF or sc.get("displayKey", "") == "":
        return False
    if display_string(sc) == "":
        return False
    if standard_modifiers(sc.get("carbonModifiers", 0)) == 0:  # hasStandardModifierKeys == false
        return False
    if uses_only_weak_modifiers(sc) and is_plain_character(sc):
        return False
    return True


HIGH_VALUE = [
    "find", "search", "open", "show", "hide", "toggle", "switch",
    "create", "new", "export", "import", "format", "rename", "run",
    "reply", "send", "preview", "command", "focus",
    "\u67e5\u627e", "\u641c\u7d22", "\u6253\u5f00", "\u663e\u793a", "\u9690\u85cf", "\u5207\u6362", "\u65b0\u5efa",
    "\u521b\u5efa", "\u5bfc\u51fa", "\u5bfc\u5165", "\u683c\u5f0f", "\u91cd\u547d\u540d", "\u8fd0\u884c", "\u56de\u590d",
    "\u53d1\u9001", "\u9884\u89c8", "\u547d\u4ee4", "\u805a\u7126",
]
LOW_VALUE = [
    "copy", "paste", "cut", "undo", "redo", "select all",
    "\u590d\u5236", "\u7c98\u8d34", "\u526a\u5207", "\u64a4\u9500", "\u91cd\u505a", "\u5168\u9009",
]


def default_score(item: dict) -> int:
    sc = item["shortcutConfiguration"]
    mods = sc.get("carbonModifiers", 0)
    title = (item["title"].get("en", "") or "").lower()
    score = 0
    if mods & CMD:
        score += 5
    if mods & OPTION:
        score += 3
    if mods & SHIFT:
        score += 2
    if mods & CONTROL:
        score += 2
    # additionalKeyCodes never present in current data
    if any(t in title for t in HIGH_VALUE):
        score += 4
    if any(t in title for t in LOW_VALUE):
        score -= 3
    return score


def current_algo_picks(categories: list) -> set:
    """Re-implements ShortcutPresetDefaultBuilder.defaultSlots selection -> item ids."""
    target, minimum = 6, 4
    cand = []
    for c in categories:
        items = [it for it in c["items"] if is_usable(it["shortcutConfiguration"])]
        items.sort(key=default_score, reverse=True)
        if items:
            cand.append(items)
    if not cand:
        return set()
    selected, used = [], set()
    offsets = [0] * len(cand)
    while len(selected) < target:
        before = len(selected)
        for i in range(len(cand)):
            if len(selected) >= target:
                break
            items = cand[i]
            off = offsets[i]
            while off < len(items):
                it = items[off]
                off += 1
                if it["id"] not in used:
                    used.add(it["id"])
                    selected.append(it)
                    break
            offsets[i] = off
        if len(selected) == before:
            break
    if len(selected) < minimum:
        flat = [it for cat in cand for it in cat]
        selected = flat[:target]
    return {it["id"] for it in selected[:target]}


def normalize_title(en: str) -> str:
    s = en.lower().strip()
    s = re.sub(r"\(.*?\)", "", s)        # drop parenthetical notes
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", s)
    return s.strip()


def needs_translation(en: str, zh: str) -> bool:
    if zh.strip() == "" or zh.strip() == en.strip():
        return True
    # zh still contains latin letters -> mixed / untranslated
    return bool(re.search(r"[A-Za-z]", zh))


def zh_needs_quality_fix(zh: str) -> bool:
    """Spaced CJK glue translations or menu labels that are too long."""
    if not zh.strip():
        return False
    if re.search(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", zh):
        return True
    return len(zh) > 14


def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    glossary = load_json(GLOSSARY_PATH)
    defaults = load_json(DEFAULTS_PATH)
    rows = []
    for path in sorted(glob.glob(os.path.join(PRESETS_DIR, "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        bid = data.get("bundleIdentifier", os.path.basename(path)[:-5])
        app = APP_NAMES.get(bid, bid)
        picks = current_algo_picks(data.get("categories", []))
        suggested = set(defaults.get(bid, []))

        # duplicate-function grouping within this app (by normalized en title)
        norm_counts = {}
        for c in data.get("categories", []):
            for it in c["items"]:
                n = normalize_title(it["title"].get("en", ""))
                norm_counts[n] = norm_counts.get(n, 0) + 1
        group_label = {}
        gi = 0
        for n, cnt in norm_counts.items():
            if cnt > 1 and n:
                gi += 1
                group_label[n] = f"G{gi}"

        for c in data.get("categories", []):
            cat = c.get("title", {})
            cat_en = cat.get("en", "") if isinstance(cat, dict) else str(cat)
            cat_zh = cat.get("zh-Hans", "") if isinstance(cat, dict) else ""
            for it in c["items"]:
                sc = it["shortcutConfiguration"]
                en = it["title"].get("en", "")
                zh = it["title"].get("zh-Hans", "")
                n = normalize_title(en)
                new_zh = glossary.get(en.strip(), "")
                # final Chinese that would actually be used
                final_zh = new_zh if new_zh else zh
                if new_zh:
                    status = "\u5df2\u91cd\u8bd1"          # 已重译 (fixed via glossary)
                elif needs_translation(en, zh):
                    status = "\u5f85\u7ffb\u8bd1"          # 待翻译 (still English/mixed)
                elif zh_needs_quality_fix(final_zh):
                    status = "\u9700\u4f18\u5316"          # 需优化 (Chinese but spaced/too long)
                else:
                    status = "\u539f\u672c\u5df2\u662f\u4e2d\u6587"  # 原本已是中文 (no action needed)
                rows.append({
                    "app_name": app,
                    "bundle_id": bid,
                    "category_zh": cat_zh,
                    "category_en": cat_en,
                    "action_en": en,
                    "action_zh_original": zh,
                    "action_zh_final": final_zh,
                    "status": status,
                    "key": display_string(sc),
                    "is_default_suggested": "\u2713" if it["id"] in suggested else "",
                    "is_default_current_algo": "\u2713" if it["id"] in picks else "",
                    "default_eligible": "\u2713" if is_usable(sc) else "",
                    "single_key": "\u2713" if is_single_key(sc) else "",
                    "dup_group": group_label.get(n, ""),
                    "item_id": it["id"],
                })

    fields = ["app_name", "bundle_id", "category_zh", "category_en",
              "action_en", "action_zh_original", "action_zh_final", "status",
              "key", "is_default_suggested", "is_default_current_algo",
              "default_eligible", "single_key", "dup_group", "item_id"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # summary
    apps = len({r["bundle_id"] for r in rows})
    already = sum(1 for r in rows if r["status"] == "\u539f\u672c\u5df2\u662f\u4e2d\u6587")
    retrans = sum(1 for r in rows if r["status"] == "\u5df2\u91cd\u8bd1")
    todo = sum(1 for r in rows if r["status"] == "\u5f85\u7ffb\u8bd1")
    quality = sum(1 for r in rows if r["status"] == "\u9700\u4f18\u5316")
    sk = sum(1 for r in rows if r["single_key"])
    de = sum(1 for r in rows if r["default_eligible"])
    dg = len({(r["bundle_id"], r["dup_group"]) for r in rows if r["dup_group"]})
    print(f"wrote {OUT_CSV}")
    print(f"apps={apps} rows={len(rows)} | \u539f\u672c\u5df2\u4e2d\u6587={already} "
          f"\u5df2\u91cd\u8bd1={retrans} \u5f85\u7ffb\u8bd1={todo} \u9700\u4f18\u5316={quality} | "
          f"single_key={sk} default_eligible={de} dup_groups={dg}")


if __name__ == "__main__":
    main()
