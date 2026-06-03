#!/usr/bin/env python3
"""Apply batch 2: 10 apps — merge glossary + defaults, regenerate review.csv."""
import csv
import json
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY_PATH = os.path.join(REPO, "review", "glossary.json")
DEFAULTS_PATH = os.path.join(REPO, "review", "defaults.json")
BATCH_GLOSSARY = os.path.join(REPO, "review", "_work", "batch2_glossary.json")

BATCH_DEFAULTS = {
    "com.microsoft.Powerpoint": [
        "remote.microsoft-powerpoint.presentations.aaaa17ac27",
        "remote.microsoft-powerpoint.presentations.cffbf33e0e",
        "remote.microsoft-powerpoint.presentations.e06154a4eb",
        "remote.microsoft-powerpoint.presentations.774c64c3a1",
        "remote.microsoft-powerpoint.changing-views.04243d1483",
        "remote.microsoft-powerpoint.changing-views.7bd8dcef4b",
    ],
    "com.microsoft.Outlook": [
        "remote.microsoft-outlook.the-following-table-shows-frequently-used-shortc.a80aed3b54",
        "remote.microsoft-outlook.use-search.1ee29220b5",
        "remote.microsoft-outlook.send-and-receive-mail.da5103706e",
        "remote.microsoft-outlook.send-and-receive-mail.0606e923d0",
        "remote.microsoft-outlook.use-the-calendar.6e81d70584",
        "remote.microsoft-outlook.work-in-windows-and-dialogs.afa57a7fc7",
    ],
    "com.microsoft.VSCode": [
        "remote.vscode.navigation.678a3d433d",
        "remote.vscode.search-and-replace.85176aab60",
        "remote.vscode.display.54915c2c42",
        "remote.vscode.search-and-replace.11cbf7aecd",
        "remote.vscode.display.e88fb89572",
        "remote.vscode.navigation.8bdc88fa20",
    ],
    "com.tinyspeck.slackmacgap": [
        "remote.slack.navigation.9097794105",
        "remote.slack.navigation.e7170dfa8c",
        "remote.slack.navigation.edb478cb65",
        "remote.slack.navigation.eee09a3153",
        "remote.slack.navigation.7b4ec3be36",
    ],
    "com.spotify.client": [
        "remote.spotify.basic.6e05169a5d",
        "remote.spotify.basic.5d2c9dbb06",
        "remote.spotify.basic.5617edb5ed",
        "remote.spotify.playback.cf681c8531",
        "remote.spotify.playback.6ab0044ba6",
        "remote.spotify.basic.6a8a7fe470",
    ],
    "com.tencent.weworkmac": [
        "remote.wework.chat.main.toggle-panel",
        "remote.wework.chat.main.global-search",
        "remote.wework.chat.input.screenshot",
        "remote.wework.mail.home.compose",
        "remote.wework.mail.home.reply",
        "remote.wework.chat.main.search",
    ],
    "org.blenderfoundation.blender": [
        "remote.blender.basics.df3a786d22",
        "remote.blender.basics.243c065df3",
        "remote.blender.general.b47b9808cf",
        "remote.blender.changing-modes.e33ac90e06",
        "remote.blender.armatures.9d22a2ac3c",
        "remote.blender.video-sequence-editor.6f7e2736d7",
    ],
    "com.google.android.studio": [
        "remote.android-studio.navigating-and-searching.f6370a3a00",
        "remote.android-studio.navigating-and-searching.b36717c7bb",
        "remote.android-studio.build-and-run.1358b6570e",
        "remote.android-studio.writing-code.d2085e5f54",
        "remote.android-studio.writing-code.a14e63d3db",
        "remote.android-studio.writing-code.f53274747f",
    ],
    "com.apple.garageband10": [
        "remote.garageband.general-shortcuts.f0c81d3246",
        "remote.garageband.general-shortcuts.340f68fc1b",
        "remote.garageband.display-objects.36f39c39df",
        "remote.garageband.general-shortcuts.4af740e966",
        "remote.garageband.misellaneous-shortcuts.58d5666db6",
        "remote.garageband.display-objects.6b39f518c5",
    ],
    "com.apple.FinalCut": [
        "remote.final-cut-pro.file.2de243e436",
        "remote.final-cut-pro.project.ce6109e81b",
        "remote.final-cut-pro.project.bb62ab0612",
        "remote.final-cut-pro.project.0dc5ae8596",
        "remote.final-cut-pro.finding-items.6205267520",
        "remote.final-cut-pro.application-window.a68c231fed",
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

    rows = list(csv.DictReader(open(os.path.join(REPO, "review", "review.csv"), encoding="utf-8-sig")))
    print(f"glossary total: {len(g)} | defaults apps: {len(d)}")
    for bid in BATCH_DEFAULTS:
        sub = [r for r in rows if r["bundle_id"] == bid]
        if not sub:
            continue
        todo = sum(1 for r in sub if r["status"] == "待翻译")
        done = sum(1 for r in sub if r["status"] == "已重译")
        ok = sum(1 for r in sub if r["status"] == "原本已是中文")
        defs = sum(1 for r in sub if r["is_default_suggested"])
        print(f"  {sub[0]['app_name']:22} todo={todo:3} 已重译={done:3} 原本中文={ok:3} 默认={defs}")


if __name__ == "__main__":
    main()
