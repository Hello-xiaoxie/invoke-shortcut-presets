#!/usr/bin/env python3
"""
Second-pass translation: fix mixed zh-en entries and translate remaining items
using comprehensive word-level dictionary.

Usage:
    python scripts/fix_mixed_translations.py [presets_dir]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Word-level English -> Chinese dictionary for in-context replacement
WORD_ZH: dict[str, str] = {
    # Nouns - UI elements
    "sidebar": "侧边栏", "toolbar": "工具栏", "panel": "面板",
    "window": "窗口", "dialog": "对话框", "menu": "菜单",
    "tab": "标签页", "tabs": "标签页", "button": "按钮",
    "icon": "图标", "cursor": "光标", "caret": "光标",
    "tooltip": "工具提示", "popover": "弹出框", "dropdown": "下拉菜单",
    "modal": "模态框", "overlay": "覆盖层", "badge": "徽标",
    "breadcrumb": "面包屑", "header": "页头", "footer": "页脚",
    "pane": "窗格", "drawer": "抽屉", "palette": "面板",
    "minimap": "迷你地图", "statusbar": "状态栏",
    "scrollbar": "滚动条",

    # Nouns - content/data
    "file": "文件", "files": "文件", "folder": "文件夹",
    "folders": "文件夹", "document": "文档", "documents": "文档",
    "image": "图片", "images": "图片", "photo": "照片",
    "video": "视频", "audio": "音频", "media": "媒体",
    "layer": "图层", "layers": "图层", "track": "轨道",
    "tracks": "轨道", "channel": "频道", "channels": "频道",
    "page": "页面", "pages": "页面", "sheet": "工作表",
    "cell": "单元格", "cells": "单元格", "row": "行", "rows": "行",
    "column": "列", "columns": "列", "table": "表格",
    "text": "文本", "paragraph": "段落", "line": "行",
    "word": "单词", "character": "字符", "string": "字符串",
    "link": "链接", "url": "URL", "path": "路径",
    "bookmark": "书签", "bookmarks": "书签",
    "note": "笔记", "notes": "笔记", "tag": "标签", "tags": "标签",
    "comment": "评论", "comments": "评论",
    "snippet": "代码片段", "snippets": "代码片段",
    "template": "模板", "templates": "模板",
    "project": "项目", "workspace": "工作区",
    "repository": "仓库", "branch": "分支", "commit": "提交",
    "issue": "事项", "task": "任务", "item": "项目",
    "selection": "选择", "clipboard": "剪贴板",
    "history": "历史记录", "log": "日志",
    "breakpoint": "断点", "variable": "变量",
    "function": "函数", "method": "方法", "class": "类",
    "symbol": "符号", "reference": "引用", "definition": "定义",
    "error": "错误", "warning": "警告", "problem": "问题",

    # Nouns - design/creative
    "canvas": "画布", "artboard": "画板", "frame": "画框",
    "shape": "形状", "object": "对象", "element": "元素",
    "group": "编组", "component": "组件", "instance": "实例",
    "style": "样式", "color": "颜色", "gradient": "渐变",
    "opacity": "不透明度", "blur": "模糊", "shadow": "阴影",
    "stroke": "描边", "fill": "填充", "mask": "蒙版",
    "path": "路径", "anchor": "锚点", "node": "节点",
    "grid": "网格", "guide": "参考线", "ruler": "标尺",
    "margin": "边距", "padding": "内边距", "spacing": "间距",
    "alignment": "对齐", "constraint": "约束",
    "prototype": "原型", "interaction": "交互",
    "animation": "动画", "transition": "过渡",
    "keyframe": "关键帧", "easing": "缓动",
    "effect": "效果", "filter": "滤镜",
    "font": "字体", "typography": "排版",

    # Nouns - audio/video
    "clip": "片段", "clips": "片段", "timeline": "时间线",
    "playhead": "播放头", "marker": "标记", "markers": "标记",
    "region": "区域", "loop": "循环",
    "mixer": "混音器", "fader": "推子",
    "plugin": "插件", "plugins": "插件",
    "preset": "预设", "presets": "预设",
    "tempo": "速度", "bpm": "BPM",

    # Verbs / Actions
    "edit": "编辑", "preview": "预览", "mode": "模式",
    "view": "视图", "current": "当前", "next": "下一个",
    "previous": "上一个", "selected": "所选", "all": "全部",
    "left": "左", "right": "右", "up": "上", "down": "下",
    "top": "顶部", "bottom": "底部", "center": "中心",
    "horizontal": "水平", "vertical": "垂直",
    "forward": "向前", "backward": "向后",
    "above": "上方", "below": "下方",
    "first": "第一个", "last": "最后一个",
    "start": "开始", "end": "结束", "beginning": "开头",
    "unread": "未读", "read": "已读",
    "active": "活动", "inactive": "非活动",
    "enabled": "已启用", "disabled": "已禁用",
    "visible": "可见", "hidden": "隐藏",
    "locked": "已锁定", "unlocked": "已解锁",
    "expanded": "已展开", "collapsed": "已折叠",
    "maximized": "最大化", "minimized": "最小化",
    "fullscreen": "全屏",
    "editor": "编辑器", "explorer": "资源管理器",
    "outline": "大纲", "search": "搜索",
    "terminal": "终端", "console": "控制台",
    "output": "输出", "debug": "调试", "source": "源",
    "extensions": "扩展", "settings": "设置",
    "preferences": "偏好设置",
}

# Additional exact matches for common full phrases
EXACT_PHRASES: dict[str, str] = {
    # VSCode
    "Select current line": "选择当前行",
    "Select all occurrences of current word": "选择当前单词的所有匹配项",
    "Select all occurrences of current selection": "选择当前选择的所有匹配项",
    "Insert cursor at end of each line selected": "在所选行的末尾插入光标",
    "Undo last cursor operation": "撤消上次光标操作",
    "Expand selection": "展开选择",
    "Shrink selection": "收缩选择",
    "Column (box) selection": "列（框）选择",
    "Add cursor above": "在上方添加光标",
    "Add cursor below": "在下方添加光标",
    "Go to matching bracket": "转到匹配括号",
    "Indent/outdent line": "增加/减少缩进",
    "Go to beginning of line": "转到行首",
    "Go to end of line": "转到行尾",
    "Go to beginning of file": "转到文件开头",
    "Go to end of file": "转到文件末尾",
    "Scroll line up": "向上滚动行",
    "Scroll line down": "向下滚动行",
    "Scroll page up": "向上滚动页",
    "Scroll page down": "向下滚动页",
    "Fold region": "折叠区域",
    "Unfold region": "展开区域",
    "Fold all subregions": "折叠所有子区域",
    "Unfold all subregions": "展开所有子区域",
    "Fold all regions": "折叠所有区域",
    "Unfold all regions": "展开所有区域",
    "Add line comment": "添加行注释",
    "Remove line comment": "移除行注释",
    "Toggle word wrap": "切换自动换行",
    "Show all symbols": "显示所有符号",
    "Go to symbol": "转到符号",
    "Show problems panel": "显示问题面板",
    "Go to next error or warning": "转到下一个错误或警告",
    "Go to previous error or warning": "转到上一个错误或警告",
    "Show all editors in group": "显示组中的所有编辑器",
    "Open Markdown preview": "打开 Markdown 预览",
    "Open Markdown preview to the side": "在侧边打开 Markdown 预览",
    "Zen Mode": "禅模式",
    "Toggle Zen Mode": "切换禅模式",

    # Obsidian
    "Toggle edit/preview mode": "切换编辑/预览模式",
    "Delete paragraph": "删除段落",
    "Insert link": "插入链接",
    "Toggle italics for selection": "切换所选内容斜体",
    "Toggle bold for selection": "切换所选内容粗体",
    "Toggle highlight for selection": "切换所选内容高亮",
    "Toggle strikethrough for selection": "切换所选内容删除线",
    "Toggle code for selection": "切换所选内容代码",
    "Open command palette": "打开命令面板",
    "Open quick switcher": "打开快速切换器",
    "Open graph view": "打开关系图谱",
    "Open backlinks": "打开反向链接",
    "Open search": "打开搜索",
    "Open settings": "打开设置",
    "Navigate back": "向后导航",
    "Navigate forward": "向前导航",
    "Create new note": "新建笔记",
    "Close current tab": "关闭当前标签页",
    "Toggle left sidebar": "切换左侧边栏",
    "Toggle right sidebar": "切换右侧边栏",
    "Toggle reading view": "切换阅读视图",
    "Focus on editor": "聚焦编辑器",

    # Linear
    "Logout": "退出登录",
    "Toggle list/board view": "切换列表/看板视图",
    "Open details sidebar": "打开详情侧边栏",
    "Move left": "向左移动", "Move right": "向右移动",
    "Move up": "向上移动", "Move down": "向下移动",
    "Open issue": "打开事项", "Close issue": "关闭事项",
    "Create issue": "创建事项", "Create sub-issue": "创建子事项",
    "Add label": "添加标签", "Remove label": "移除标签",
    "Set priority": "设置优先级", "Set status": "设置状态",
    "Assign to me": "分配给我", "Assign to...": "分配给…",
    "Copy issue URL": "复制事项 URL",
    "Copy issue ID": "复制事项 ID",
    "Archive issue": "归档事项",
    "Go to inbox": "转到收件箱",
    "Go to my issues": "转到我的事项",
    "Filter": "筛选", "Sort": "排序",

    # Browser common
    "Open new tab": "打开新标签页",
    "Close current tab": "关闭当前标签页",
    "Reopen last closed tab": "重新打开上次关闭的标签页",
    "Switch to next tab": "切换到下一个标签页",
    "Switch to previous tab": "切换到上一个标签页",
    "Open new window": "打开新窗口",
    "Open new private window": "打开新隐私窗口",
    "Open new incognito window": "打开新无痕窗口",
    "Open developer tools": "打开开发者工具",
    "Toggle bookmarks bar": "切换书签栏",
    "Show downloads": "显示下载",
    "Show history": "显示历史记录",
    "Clear browsing data": "清除浏览数据",
    "Focus address bar": "聚焦地址栏",
    "Scroll to top": "滚动到顶部",
    "Scroll to bottom": "滚动到底部",
    "Page source": "页面源代码",
    "Print page": "打印页面",
    "Save page": "保存页面",

    # Finder
    "New Finder Window": "新建 Finder 窗口",
    "New Folder": "新建文件夹",
    "Get Info": "显示简介",
    "Quick Look": "快速查看",
    "Move to Trash": "移到废纸篓",
    "Empty Trash": "清倒废纸篓",
    "Go to Folder": "前往文件夹",
    "Connect to Server": "连接服务器",
    "Show View Options": "显示视图选项",
    "Show Path Bar": "显示路径栏",
    "Show Status Bar": "显示状态栏",

    # Communication
    "Toggle mute": "切换静音", "Toggle video": "切换视频",
    "Share screen": "共享屏幕", "Raise hand": "举手",
    "Leave meeting": "离开会议", "End meeting": "结束会议",
    "Send message": "发送消息", "New message": "新消息",
    "Reply to message": "回复消息", "Forward message": "转发消息",
    "Mark as read": "标记为已读", "Mark as unread": "标记为未读",
    "Pin message": "固定消息", "Star message": "收藏消息",

    # Generic actions
    "Save as": "另存为", "Save As": "另存为",
    "Export as": "导出为", "Export As": "导出为",
    "Open file": "打开文件", "New file": "新建文件",
    "Close file": "关闭文件", "Save file": "保存文件",
    "Close all": "全部关闭", "Save all": "全部保存",
    "Undo last action": "撤消上一操作",
    "Redo last action": "恢复上一操作",
}


def translate_full(en: str, current_zh: str) -> str:
    """Full translation attempt using exact phrases + word-level replacement."""
    # 1. Exact phrase match
    if en in EXACT_PHRASES:
        return EXACT_PHRASES[en]

    # 2. If already has good translation (all Chinese, no latin mix)
    has_cjk = any(ord(c) > 0x4E00 for c in current_zh)
    has_latin = bool(re.search(r'[a-zA-Z]{2,}', current_zh))
    if has_cjk and not has_latin:
        return current_zh  # already good

    # 3. Word-level replacement in current_zh (fix mixed entries)
    result = current_zh
    for eng_word, zh_word in sorted(WORD_ZH.items(), key=lambda x: -len(x[0])):
        # Case-insensitive word boundary replacement
        pattern = r'\b' + re.escape(eng_word) + r'\b'
        result = re.sub(pattern, zh_word, result, flags=re.IGNORECASE)

    # 4. If result is still largely English, try translating from scratch
    remaining_latin = re.findall(r'[a-zA-Z]{3,}', result)
    if remaining_latin and len(remaining_latin) > 2:
        # Too many untranslated words, keep original zh (which might be better)
        # But only if the original already had some Chinese
        if has_cjk:
            return current_zh
        return result

    return result


def process_file(filepath: Path) -> tuple[int, int]:
    data = json.loads(filepath.read_text("utf-8"))
    total = 0
    improved = 0

    for cat in data.get("categories", []):
        for item in cat.get("items", []):
            total += 1
            en = item["title"]["en"]
            zh = item["title"].get("zh-Hans", en)

            new_zh = translate_full(en, zh)
            if new_zh != zh:
                item["title"]["zh-Hans"] = new_zh
                improved += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return total, improved


def main():
    presets_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "presets"
    files = sorted(presets_dir.glob("*.json"))
    print(f"[INFO] Second-pass translation for {len(files)} files...", file=sys.stderr)

    total_items = 0
    total_improved = 0

    for f in files:
        try:
            t, i = process_file(f)
            total_items += t
            total_improved += i
            if i > 0:
                print(f"  {f.name}: {i}/{t} improved", file=sys.stderr)
        except Exception as e:
            print(f"  ERROR {f.name}: {e}", file=sys.stderr)

    print(f"\n[DONE] Total: {total_items}, Fixed: {total_improved}", file=sys.stderr)


if __name__ == "__main__":
    main()
