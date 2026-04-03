#!/usr/bin/env python3
"""Add SF Symbol icons to Figma preset items that have no icon (keeps existing SVG)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "presets" / "com.figma.Desktop.json"

# Reasonable SF Symbols for macOS 13+; Figma.com does not ship per-shortcut assets in a scrapeable table.
SF_BY_ID: dict[str, str] = {
    "remote.figma.detach-instance": "link.badge.minus",
    "remote.figma.create-component": "cube.fill",
    "remote.figma.team-library": "books.vertical.fill",
    "remote.figma.show-assets": "photo.on.rectangle.angled",
    "remote.figma.remove-auto-layout": "rectangle.slash",
    "remote.figma.add-auto-layout": "rectangle.3.group",
    "remote.figma.tidy-up": "square.grid.3x3.square.badge.ellipsis",
    "remote.figma.send-to-back": "arrow.down.to.line",
    "remote.figma.bring-to-front": "arrow.up.to.line",
    "remote.figma.send-backward": "arrow.down.circle",
    "remote.figma.bring-forward": "arrow.up.circle",
    "remote.figma.set-opacity-to-100": "circle.fill",
    "remote.figma.set-opacity-to-50": "circle.lefthalf.filled",
    "remote.figma.set-opacity-to-10": "circle.dotted",
    "remote.figma.place-image": "photo",
    "remote.figma.use-as-mask": "theatermasks.fill",
    "remote.figma.flip-vertical": "arrow.up.and.down",
    "remote.figma.flip-horizontal": "arrow.left.and.right",
    "remote.figma.paste-properties": "doc.text.image",
    "remote.figma.copy-properties": "doc.on.doc.fill",
    "remote.figma.export": "square.and.arrow.up",
    "remote.figma.rename-selection": "pencil.line",
    "remote.figma.duplicate": "plus.square.on.square",
    "remote.figma.paste-over-selection": "doc.on.clipboard.fill",
    "remote.figma.paste": "doc.on.clipboard",
    "remote.figma.cut": "scissors",
    "remote.figma.copy": "doc.on.doc",
    "remote.figma.lock-unlock-selection": "lock.open.fill",
    "remote.figma.show-hide-selection": "eye.slash.fill",
    "remote.figma.frame-selection": "rectangle.dashed",
    "remote.figma.ungroup-selection": "rectangle.3.group",
    "remote.figma.group-selection": "square.grid.3x1",
    "remote.figma.select-previous-sibling": "arrow.left.to.line",
    "remote.figma.select-next-sibling": "arrow.right.to.line",
    "remote.figma.select-parents": "arrow.up.left",
    "remote.figma.select-child": "arrow.down.right",
    "remote.figma.select-none": "xmark.circle",
    "remote.figma.select-inverse": "arrow.triangle.2.circlepath",
    "remote.figma.select-all": "square.dashed.inset.filled",
    "remote.figma.smooth-join-selection-after-selecting-points": "point.3.connected.trianglepath.dotted",
    "remote.figma.join-selection-after-selecting-points": "link",
    "remote.figma.flatten-selection": "square.stack.3d.down.right",
    "remote.figma.outline-stroke": "circle.dashed",
    "remote.figma.swap-fill-stroke": "arrow.left.arrow.right",
    "remote.figma.remove-stroke": "circle.slash",
    "remote.figma.remove-fill": "square.slash",
    "remote.figma.bend-tool": "arrow.uturn.left",
    "remote.figma.paint-bucket-while-editing-a-shape": "drop.fill",
    "remote.figma.pencil": "pencil",
    "remote.figma.pen": "pen.tip",
    "remote.figma.adjust-line-height": "line.3.horizontal",
    "remote.figma.adjust-letter-spacing": "character.textbox",
    "remote.figma.adjust-font-weight": "bold",
    "remote.figma.adjust-font-size": "textformat.size",
    "remote.figma.text-align-justified": "text.justify.leading",
    "remote.figma.text-align-right": "text.alignright",
    "remote.figma.text-align-center": "text.aligncenter",
    "remote.figma.text-align-left": "text.alignleft",
    "remote.figma.create-link": "link",
    "remote.figma.paste-match-style": "paintbrush.pointed.fill",
    "remote.figma.underline": "underline",
    "remote.figma.italic": "italic",
    "remote.figma.bold": "bold",
    "remote.figma.find-next-frame": "arrow.down.doc",
    "remote.figma.find-previous-frame": "arrow.up.doc",
    "remote.figma.next-page": "doc.append",
    "remote.figma.previous-page": "doc.text",
    "remote.figma.zoom-to-next-frame": "viewfinder",
    "remote.figma.zoom-to-previous-frame": "viewfinder.circle",
    "remote.figma.zoom-to-selection": "magnifyingglass.circle",
    "remote.figma.zoom-to-fit": "arrow.down.right.and.arrow.up.left",
    "remote.figma.zoom-to-100": "percent",
    "remote.figma.zoom-out": "minus.magnifyingglass",
    "remote.figma.zoom-in": "plus.magnifyingglass",
    "remote.figma.open-code-panel": "chevron.left.forwardslash.chevron.right",
    "remote.figma.open-prototype-panel": "play.rectangle",
    "remote.figma.open-design-panel": "paintpalette.fill",
    "remote.figma.open-assets-panel": "square.grid.2x2",
    "remote.figma.open-layers-panel": "rectangle.stack",
    "remote.figma.pixel-grid": "grid",
    "remote.figma.layout-grids": "grid.circle",
    "remote.figma.pixel-preview": "circle.grid.cross",
    "remote.figma.outlines": "square.on.square.dashed",
    "remote.figma.rulers": "ruler",
    "remote.figma.multiplayer-cursors": "person.2.fill",
    "remote.figma.search": "magnifyingglass",
    "remote.figma.pick-color": "eyedropper",
    "remote.figma.show-hide-ui": "sidebar.leading",
}


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    added = 0
    for cat in data.get("categories", []):
        for item in cat.get("items", []):
            if item.get("icon"):
                continue
            sym = SF_BY_ID.get(item["id"])
            if not sym:
                continue
            item["icon"] = {"type": "sfSymbol", "name": sym}
            added += 1
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Patched {added} items with sfSymbol icons.")


if __name__ == "__main__":
    main()
