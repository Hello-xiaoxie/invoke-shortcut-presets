#!/usr/bin/env python3
"""Enterprise WeChat (Mac) presets — filtered: no single-key, no mouse/wheel, one shortcut per row, red-box removals. Run: python3 scripts/build_wework_mac_preset.py"""

from __future__ import annotations

import json
from pathlib import Path

CMD, SHIFT, OPT, CTRL = 256, 512, 2048, 4096

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "presets" / "com.tencent.weworkmac.json"


def sc(key_code: int, mods: int, display_key: str) -> dict:
    return {"keyCode": key_code, "carbonModifiers": mods, "displayKey": display_key}


def loc(en: str, zh: str) -> dict:
    return {"en": en, "zh-Hans": zh}


def item(
    iid: str,
    en: str,
    zh: str,
    conf: dict,
    *,
    kw: list[str] | None = None,
    tokens: list[str] | None = None,
) -> dict:
    o: dict = {"id": iid, "title": loc(en, zh), "shortcutConfiguration": conf}
    if kw:
        o["searchKeywords"] = kw
    if tokens:
        o["shortcutDisplayTokens"] = tokens
    return o


def category(cid: str, en: str, zh: str, items: list[dict]) -> dict:
    return {"id": cid, "title": loc(en, zh), "items": items}


def main() -> None:
    cats: list[dict] = []

    # —— [聊天] ——
    cats.append(
        category(
            "remote.wework.chat.main-menu",
            "[Chat] Main Menu",
            "[聊天] 主菜单",
            [
                item(
                    "remote.wework.chat.main.toggle-panel",
                    "Open / Hide Main Panel",
                    "打开/隐藏主面板",
                    sc(13, CMD | SHIFT, "W"),
                ),
                item("remote.wework.chat.main.close-window", "Close Window", "关闭窗口", sc(13, CMD, "W")),
                item("remote.wework.chat.main.new-group", "Create Group Chat", "创建群聊", sc(45, CMD, "N")),
                item("remote.wework.chat.main.search", "Activate Search Box", "激活搜索框", sc(3, CMD, "F")),
                item(
                    "remote.wework.chat.main.global-search",
                    "Open / Close Global Search",
                    "打开/关闭全局搜索",
                    sc(3, CMD | SHIFT, "F"),
                ),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.chat.message-list",
            "[Chat] Message List",
            "[聊天] 消息列表",
            [
                item(
                    "remote.wework.chat.list.next-unread",
                    "Next Unread Chat",
                    "下一个未读聊天",
                    sc(125, CMD | OPT, "↓"),
                ),
                item(
                    "remote.wework.chat.list.prev-unread",
                    "Previous Unread Chat",
                    "上一个未读聊天",
                    sc(126, CMD | OPT, "↑"),
                ),
                item(
                    "remote.wework.chat.list.read-unread",
                    "Mark Current Chat Read / Unread",
                    "将当前聊天标记为已读/未读",
                    sc(32, CMD, "U"),
                ),
                item(
                    "remote.wework.chat.list.flag",
                    "Flag / Unflag Current Chat",
                    "标记/取消标记当前聊天",
                    sc(17, CMD, "T"),
                ),
                item(
                    "remote.wework.chat.list.mute-notify",
                    "Mute / Unmute Notifications (Current Chat)",
                    "免打扰/新消息提醒当前聊天",
                    sc(15, CMD | SHIFT, "R"),
                ),
                item(
                    "remote.wework.chat.list.hide-chat",
                    "Hide Current Chat",
                    "不显示当前聊天",
                    sc(2, CMD | SHIFT, "D"),
                ),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.chat.input",
            "[Chat] Input Box",
            "[聊天] 输入框",
            [
                item("remote.wework.chat.input.screenshot", "Screenshot", "截屏", sc(0, CMD | SHIFT, "A")),
                item(
                    "remote.wework.chat.input.history",
                    "Open / Close Message History",
                    "打开/关闭“消息记录”",
                    sc(4, SHIFT | CTRL, "H"),
                ),
            ],
        )
    )

    # —— [邮件] ——
    cats.append(
        category(
            "remote.wework.mail.home",
            "[Mail] Main Page",
            "[邮件] 主页面",
            [
                item("remote.wework.mail.home.compose", "Compose New Email", "写新邮件", sc(45, CTRL, "N")),
                item(
                    "remote.wework.mail.home.focus-search",
                    "Focus Top Search",
                    "定位到顶部搜索",
                    sc(3, CMD | OPT, "F"),
                ),
                item(
                    "remote.wework.mail.home.find-body",
                    "Find in Body",
                    "在正文查找关键词",
                    sc(3, CMD, "F"),
                ),
                item("remote.wework.mail.home.reply", "Reply", "回复", sc(15, CMD, "R")),
                item("remote.wework.mail.home.reply-all", "Reply All", "回复全部", sc(15, CMD | SHIFT, "R")),
                item("remote.wework.mail.home.forward", "Forward", "转发", sc(13, SHIFT, "W")),
                item("remote.wework.mail.home.delete-opt", "Delete Email", "删除邮件", sc(2, OPT, "D")),
                item("remote.wework.mail.home.delete-hard", "Permanently Delete", "彻底删除", sc(2, CMD, "D")),
                item("remote.wework.mail.home.read", "Mark as Read", "标为已读", sc(14, CMD, "E")),
                item("remote.wework.mail.home.unread", "Mark as Unread", "标为未读", sc(32, CMD, "U")),
                item(
                    "remote.wework.mail.home.star",
                    "Add / Remove Star",
                    "添加/取消星标",
                    sc(28, SHIFT, "8"),
                ),
                item("remote.wework.mail.home.reject", "Reject", "拒收", sc(18, SHIFT, "!")),
                item("remote.wework.mail.home.print", "Print", "打印", sc(35, CTRL, "P")),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.mail.list",
            "[Mail] Email List",
            "[邮件] 邮件列表",
            [
                item(
                    "remote.wework.mail.list.next-unread",
                    "Next Unread Email",
                    "下一个未读邮件",
                    sc(125, CMD | OPT, "↓"),
                ),
                item(
                    "remote.wework.mail.list.prev-unread",
                    "Previous Unread Email",
                    "上一个未读邮件",
                    sc(126, CMD | OPT, "↑"),
                ),
                item(
                    "remote.wework.mail.list.edit-again",
                    "Edit Again",
                    "再次编辑",
                    sc(2, CMD | SHIFT, "D"),
                ),
            ],
        )
    )

    # —— [文档]（原幻灯片，与文档合并为一组）——
    cats.append(
        category(
            "remote.wework.doc.ops",
            "[Document] Operations",
            "[文档] 操作",
            [
                item("remote.wework.doc.ops.undo", "Undo", "撤销", sc(6, CMD, "Z")),
                item("remote.wework.doc.ops.redo", "Redo", "重做", sc(16, CMD, "Y")),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.doc.format",
            "[Document] Format",
            "[文档] 格式",
            [
                item("remote.wework.doc.fmt.bold", "Bold", "加粗", sc(11, CMD, "B")),
                item("remote.wework.doc.fmt.italic", "Italic", "斜体", sc(34, CMD, "I")),
                item("remote.wework.doc.fmt.underline", "Underline", "下划线", sc(32, CMD, "U")),
                item("remote.wework.doc.fmt.strike", "Strikethrough", "删除线", sc(2, CMD, "D")),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.doc.navigate",
            "[Document] Navigation",
            "[文档] 导航",
            [
                item(
                    "remote.wework.doc.nav.para-start",
                    "Move to Paragraph Start",
                    "移至段首",
                    sc(126, OPT, "↑"),
                ),
                item(
                    "remote.wework.doc.nav.para-end",
                    "Move to Paragraph End",
                    "移至段尾",
                    sc(125, OPT, "↓"),
                ),
                item(
                    "remote.wework.doc.nav.line-start",
                    "Move to Line Start",
                    "移至行首",
                    sc(123, CMD, "←"),
                ),
                item(
                    "remote.wework.doc.nav.line-end",
                    "Move to Line End",
                    "移至行尾",
                    sc(124, CMD, "→"),
                ),
                item(
                    "remote.wework.doc.nav.obj-start",
                    "Move to Object Start",
                    "移至编辑对象的首",
                    sc(126, CMD, "↑"),
                ),
                item(
                    "remote.wework.doc.nav.obj-end",
                    "Move to Object End",
                    "移至编辑对象的尾",
                    sc(125, CMD, "↓"),
                ),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.doc.view",
            "[Document] View",
            "[文档] 查看",
            [
                item("remote.wework.doc.view.zoom-100", "Reset Zoom to 100%", "回到100%", sc(29, CMD, "0")),
                item("remote.wework.doc.view.play", "Start Presentation", "开始播放", sc(36, CMD, "↩")),
                item("remote.wework.doc.view.find", "Find", "查找", sc(3, CMD, "F")),
                item(
                    "remote.wework.doc.view.shortcut-panel",
                    "Toggle Shortcuts Panel",
                    "打开/关闭快捷键面板",
                    sc(44, CMD, "/"),
                ),
            ],
        )
    )

    # —— [表格]（按最新截图：⌃ 对齐/筛选/填充等）——
    cats.append(
        category(
            "remote.wework.sheet.ops",
            "[Sheet] Operations",
            "[表格] 操作",
            [
                item("remote.wework.sheet.ops.undo", "Undo", "撤销", sc(6, CMD, "Z")),
                item("remote.wework.sheet.ops.redo", "Redo", "重做", sc(16, CMD, "Y")),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.sheet.insert",
            "[Sheet] Insert",
            "[表格] 插入",
            [
                item(
                    "remote.wework.sheet.insert.comment",
                    "Insert Comment",
                    "插入批注",
                    sc(120, SHIFT, "F2"),
                ),
                item(
                    "remote.wework.sheet.insert.date",
                    "Insert Current Date",
                    "插入当前日期",
                    sc(41, CTRL, ";"),
                ),
                item(
                    "remote.wework.sheet.insert.time",
                    "Insert Current Time",
                    "插入当前时间",
                    sc(41, CMD | SHIFT, ";"),
                ),
                item(
                    "remote.wework.sheet.insert.datetime",
                    "Insert Date & Time",
                    "插入当前日期+时间",
                    sc(41, CMD | OPT, ";"),
                ),
                item("remote.wework.sheet.insert.link", "Insert Link", "插入链接", sc(40, CMD, "K")),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.sheet.functions",
            "[Sheet] Functions",
            "[表格] 功能",
            [
                item(
                    "remote.wework.sheet.fn.filter",
                    "Filter",
                    "筛选",
                    sc(37, CTRL | SHIFT, "L"),
                ),
                item("remote.wework.sheet.fn.fill-down", "Fill Down", "向下填充", sc(2, CTRL, "D")),
                item(
                    "remote.wework.sheet.fn.fill-selection",
                    "Fill Selection",
                    "选区填充",
                    sc(36, CMD, "↩"),
                ),
                item("remote.wework.sheet.fn.close", "Close Window", "关闭窗口", sc(13, CMD, "W")),
                item(
                    "remote.wework.sheet.fn.merge",
                    "Merge / Unmerge Cells",
                    "合并/取消合并单元格",
                    sc(2, OPT | SHIFT, "D"),
                ),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.sheet.format",
            "[Sheet] Format",
            "[表格] 格式",
            [
                item("remote.wework.sheet.fmt.bold", "Bold", "加粗", sc(11, CMD, "B")),
                item("remote.wework.sheet.fmt.italic", "Italic", "倾斜", sc(34, CMD, "I")),
                item("remote.wework.sheet.fmt.underline", "Underline", "下划线", sc(32, CMD, "U")),
                item(
                    "remote.wework.sheet.fmt.strike",
                    "Strikethrough",
                    "删除线",
                    sc(23, CTRL, "5"),
                ),
                item("remote.wework.sheet.fmt.align-left", "Align Left", "左对齐", sc(37, CTRL, "L")),
                item("remote.wework.sheet.fmt.align-right", "Align Right", "右对齐", sc(15, CTRL, "R")),
                item("remote.wework.sheet.fmt.align-center", "Align Center", "居中对齐", sc(14, CTRL, "E")),
                item(
                    "remote.wework.sheet.fmt.font-larger",
                    "Increase Font Size",
                    "字号变大",
                    sc(47, CMD | SHIFT, "."),
                ),
                item(
                    "remote.wework.sheet.fmt.font-smaller",
                    "Decrease Font Size",
                    "字号变小",
                    sc(43, CMD | SHIFT, ","),
                ),
            ],
        )
    )

    cats.append(
        category(
            "remote.wework.sheet.view",
            "[Sheet] View",
            "[表格] 查看",
            [
                item(
                    "remote.wework.sheet.view.extend-edge",
                    "Extend Selection to Data Edge (⌘⇧+Arrow)",
                    "扩展至数据区边缘（⌘⇧+方向键）",
                    sc(125, CMD | SHIFT, "↓"),
                    tokens=["⌘⇧←", "⌘⇧→", "⌘⇧↑", "⌘⇧↓"],
                    kw=["arrow", "数据区"],
                ),
                item("remote.wework.sheet.view.zoom-100", "Zoom 100%", "100% 视图", sc(29, CMD, "0")),
                item(
                    "remote.wework.sheet.view.fullscreen",
                    "Toggle Full Screen",
                    "全屏/取消全屏",
                    sc(3, CMD | CTRL, "F"),
                ),
                item("remote.wework.sheet.view.find", "Find", "查找", sc(3, CMD, "F")),
                item(
                    "remote.wework.sheet.view.replace",
                    "Replace",
                    "替换",
                    sc(4, CMD | SHIFT, "H"),
                ),
                item(
                    "remote.wework.sheet.view.shortcut-panel",
                    "Toggle Shortcuts Panel",
                    "打开/关闭快捷键面板",
                    sc(44, CMD, "/"),
                ),
            ],
        )
    )

    root = {
        "bundleIdentifier": "com.tencent.weworkmac",
        "i18n": {"defaultLocale": "en", "locales": ["en", "zh-Hans"]},
        "categories": cats,
    }

    OUT.write_text(json.dumps(root, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n_items = sum(len(c["items"]) for c in cats)
    print(f"Wrote {OUT} ({len(cats)} categories, {n_items} items)")


if __name__ == "__main__":
    main()
