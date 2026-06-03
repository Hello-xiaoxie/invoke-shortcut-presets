#!/usr/bin/env python3
"""Apply batch 1: 10 apps — merge glossary + defaults, regenerate review.csv."""
import json
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY_PATH = os.path.join(REPO, "review", "glossary.json")
DEFAULTS_PATH = os.path.join(REPO, "review", "defaults.json")
BATCH_GLOSSARY = os.path.join(REPO, "review", "_work", "batch1_glossary.json")

BATCH_DEFAULTS = {
    "com.figma.Desktop": [
        "remote.figma.create-component",
        "remote.figma.export",
        "remote.figma.rename-selection",
        "remote.figma.team-library",
        "remote.figma.place-image",
        "remote.figma.duplicate",
    ],
    "com.microsoft.Word": [
        "remote.word.frequently-used-shortcuts.0bfc68db58",
        "remote.word.frequently-used-shortcuts.da5ec3234f",
        "remote.word.frequently-used-shortcuts.ea9c06467d",
        "remote.word.frequently-used-shortcuts.727c6c872c",
        "remote.word.frequently-used-shortcuts.911a579d33",
        "remote.word.edit-text-and-graphics.0edd53b0f1",
    ],
    "com.microsoft.Excel": [
        "remote.excel.frequently-used-shortcuts.8bd109e1f4",
        "remote.excel.frequently-used-shortcuts.892e4f1aca",
        "remote.excel.frequently-used-shortcuts.5b6eceeb05",
        "remote.excel.frequently-used-shortcuts.aa00ae78d5",
    ],
    "com.apple.dt.Xcode": [
        "remote.xcode.file-navigation.0407db33e7",
        "remote.xcode.code-navigation.9a42a8bb74",
        "remote.xcode.build-and-run.586df9267f",
        "remote.xcode.build-and-run.7f6a2a6893",
        "remote.xcode.other-shortcuts.000cae775d",
        "remote.xcode.code-editing.469cf5dddd",
    ],
    "com.lukilabs.lukiapp": [
        "remote.craft.search.dd8c00e4c1",
        "remote.craft.new-document.341cd77dc9",
        "remote.craft.decorations.64cc5ff7eb",
        "remote.craft.grouping.135632afca",
        "remote.craft.editing.fffd235097",
        "remote.craft.toggles.da91d29273",
    ],
    "com.apple.iWork.Keynote": [
        "remote.apple-keynote.slideshow.fc5ed75b8c",
        "remote.apple-keynote.general-shortcuts.f31d00ae6b",
        "remote.apple-keynote.general-shortcuts.b42d98caa0",
        "remote.apple-keynote.general-shortcuts.f46e8af777",
        "remote.apple-keynote.general-shortcuts.d96fe0fc41",
        "remote.apple-keynote.chart-data-editor.bcc4edc2d0",
    ],
    "com.apple.iWork.Numbers": [
        "remote.apple-numbers.general-shortcuts.12879dc75b",
        "remote.apple-numbers.general-shortcuts.d5321ec2fa",
        "remote.apple-numbers.general-shortcuts.cf6943bb40",
        "remote.apple-numbers.general-shortcuts.2aff29f092",
        "remote.apple-numbers.general-shortcuts.ecc25eb852",
        "remote.apple-numbers.general-shortcuts.72703d7537",
    ],
    "com.apple.iWork.Pages": [
        "remote.apple-pages.formatting-text.5af181712e",
        "remote.apple-pages.general.473b77c350",
        "remote.apple-pages.general.f060013be8",
        "remote.apple-pages.formatting-text.5239212f9a",
        "remote.apple-pages.general.50086adec1",
        "remote.apple-pages.manipulating-fixed-objects.6aa7c41062",
    ],
    "com.apple.iMovieApp": [
        "remote.imovie.import-and-export-shortcuts.ed83345e87",
        "remote.imovie.manage-events-and-projects.951b06c87a",
        "remote.imovie.video-edit.b1088a8905",
        "remote.imovie.imovie-window.903b211bcb",
        "remote.imovie.import-and-export-shortcuts.d6b8343667",
        "remote.imovie.video-edit.75278b5f0e",
    ],
}


def main():
    batch = json.load(open(BATCH_GLOSSARY, encoding="utf-8"))
    g = json.load(open(GLOSSARY_PATH, encoding="utf-8"))
    g.update(batch)
    json.dump(g, open(GLOSSARY_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)

    d = json.load(open(DEFAULTS_PATH, encoding="utf-8"))
    d.update(BATCH_DEFAULTS)
    json.dump(d, open(DEFAULTS_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)

    subprocess.run(["python3", os.path.join(REPO, "scripts", "build_review_table.py")], check=True)

    # per-app stats for batch
    import csv
    rows = list(csv.DictReader(open(os.path.join(REPO, "review", "review.csv"), encoding="utf-8-sig")))
    apps = list(BATCH_DEFAULTS.keys()) + ["com.tencent.meeting"]
    print(f"glossary total: {len(g)} | defaults apps: {len(d)}")
    for bid in apps:
        sub = [r for r in rows if r["bundle_id"] == bid]
        if not sub:
            continue
        todo = sum(1 for r in sub if r["status"] == "待翻译")
        done = sum(1 for r in sub if r["status"] == "已重译")
        defs = sum(1 for r in sub if r["is_default_suggested"])
        print(f"  {sub[0]['app_name']:18} todo={todo:3} 已重译={done:3} 默认={defs}")


if __name__ == "__main__":
    main()
