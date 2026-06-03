#!/usr/bin/env python3
"""Apply batch 3: 10 apps — merge glossary + defaults, regenerate review.csv."""
import csv
import json
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY_PATH = os.path.join(REPO, "review", "glossary.json")
DEFAULTS_PATH = os.path.join(REPO, "review", "defaults.json")
BATCH_GLOSSARY = os.path.join(REPO, "review", "_work", "batch3_glossary.json")

BATCH_DEFAULTS = {
    "com.adobe.AfterEffects": [
        "remote.adobe-after-effects.projects.ff4d559836",
        "remote.adobe-after-effects.projects.2d95d9e8fb",
        "remote.adobe-after-effects.projects.bd3853cf8b",
        "remote.adobe-after-effects.compositions-and-work-area.aa2c0f670a",
        "remote.adobe-after-effects.panels-viewers-workspaces-and-windows.c02626dfa8",
        "remote.adobe-after-effects.basics.82365755bc",
    ],
    "com.adobe.Photoshop": [
        "remote.adobe-photoshop.basic-shortcuts-for-photoshop-cc-2015.d6a6bca433",
        "remote.adobe-photoshop.basic-shortcuts-for-photoshop-cc-2015.03badedde4",
        "remote.adobe-photoshop.liquify-window.89b95040ca",
        "remote.adobe-photoshop.curves-dialog-box.4dd7e83cf3",
        "remote.adobe-photoshop.manage-panels.d4353f4b26",
        "remote.adobe-photoshop.manage-views.84fdf38252",
    ],
    "com.adobe.InDesign": [
        "remote.adobe-indesign.file-menu-shortcuts.0b78e0dc5a",
        "remote.adobe-indesign.file-menu-shortcuts.c7879f2087",
        "remote.adobe-indesign.edit-menu-shortcuts.d851f7f269",
        "remote.adobe-indesign.file-menu-shortcuts.b59d332d1b",
        "remote.adobe-indesign.file-menu-shortcuts.57b5c5f63f",
        "remote.adobe-indesign.layout-menu-shortcuts.8ec1d7804e",
    ],
    "com.adobe.illustrator": [
        "remote.adobe-illustrator.function-keys.df219a4301",
        "remote.adobe-illustrator.function-keys.4048ee48fd",
        "remote.adobe-illustrator.function-keys.e78dbbfa80",
        "remote.adobe-illustrator.viewing-artwork.be68858bbf",
        "remote.adobe-illustrator.function-keys.c4f6943285",
        "remote.adobe-illustrator.function-keys.fac91bf462",
    ],
    "com.apple.logic10": [
        "remote.logic-pro.general-controls.8297440c2b",
        "remote.logic-pro.general-controls.90b15e00eb",
        "remote.logic-pro.general-controls.18354d435c",
        "remote.logic-pro.main-window.61c437598b",
        "remote.logic-pro.general-controls.521ddc4163",
        "remote.logic-pro.general-controls.83f44969ce",
    ],
    "com.jetbrains.PyCharm": [
        "remote.pycharm.search.eb76dc0b06",
        "remote.pycharm.search.f3971cf25f",
        "remote.pycharm.refactoring.5de98fb942",
        "remote.pycharm.show-tool-windows.a63ed298a0",
        "remote.pycharm.views-and-windows.2ccc71bc2c",
        "remote.pycharm.search.9ae1ab857c",
    ],
    "com.jetbrains.intellij": [
        "remote.intellij-idea.find-and-replace-shortcuts.f3971cf25f",
        "remote.intellij-idea.general-shortcuts.eb76dc0b06",
        "remote.intellij-idea.editing-shortcuts.bb6da74a59",
        "remote.intellij-idea.navigation-shortcuts.dd7430f511",
        "remote.intellij-idea.general-shortcuts.69b4726738",
        "remote.intellij-idea.usage-shortcuts.9889099428",
    ],
    "com.operasoftware.Opera": [
        "remote.opera.sitemap-navigation.44a0713861",
        "remote.opera.system.2de243e436",
        "remote.opera.find.aa8f0dc111",
        "remote.opera.email.0679fe604b",
        "remote.opera.system.677be11650",
        "remote.opera.email.4e44ddeacf",
    ],
    "com.seriflabs.affinityphoto2": [
        "remote.affinity-photo-2.file.e4384ca1a4",
        "remote.affinity-photo-2.file.452e58aeb5",
        "remote.affinity-photo-2.file.dea3c23383",
        "remote.affinity-photo-2.miscellaneous.5709351db9",
        "remote.affinity-photo-2.miscellaneous.8a8c464221",
        "remote.affinity-photo-2.workspace.c23bdadfee",
    ],
    "org.inkscape.Inkscape": [
        "remote.inkscape.file.be7b88d97e",
        "remote.inkscape.file.16b3603761",
        "remote.inkscape.dialogs.397793d8a8",
        "remote.inkscape.dialogs.bb3828daaa",
        "remote.inkscape.dialogs.bc849685e9",
        "remote.inkscape.dialogs.9471f0e213",
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

    subprocess.run(["python3", os.path.join(REPO, "scripts", "cleanup_zh_labels.py")], check=True)

    rows = list(csv.DictReader(open(os.path.join(REPO, "review", "review.csv"), encoding="utf-8-sig")))
    print(f"glossary total: {len(g)} | defaults apps: {len(d)}")
    for bid in BATCH_DEFAULTS:
        sub = [r for r in rows if r["bundle_id"] == bid]
        if not sub:
            continue
        todo = sum(1 for r in sub if r["status"] == "待翻译")
        done = sum(1 for r in sub if r["status"] == "已重译")
        ok = sum(1 for r in sub if r["status"] == "原本已是中文")
        qual = sum(1 for r in sub if r["status"] == "需优化")
        defs = sum(1 for r in sub if r["is_default_suggested"])
        print(f"  {sub[0]['app_name']:22} todo={todo:3} 已重译={done:3} 原本中文={ok:3} 需优化={qual:2} 默认={defs}")


if __name__ == "__main__":
    main()
