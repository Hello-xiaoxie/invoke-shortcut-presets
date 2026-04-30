#!/usr/bin/env python3
"""
Enhance zh-Hans translations for all preset JSON files.
Uses a comprehensive domain-specific dictionary to improve translations.

Usage:
    python scripts/enhance_translations.py [presets_dir]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Domain-specific translations (app-category keyed)
# ---------------------------------------------------------------------------

# Adobe family common terms
ADOBE_ZH: dict[str, str] = {
    "Hand tool": "抓手工具", "Zoom tool": "缩放工具", "Move tool": "移动工具",
    "Brush tool": "画笔工具", "Eraser tool": "橡皮擦工具", "Pen tool": "钢笔工具",
    "Type tool": "文字工具", "Gradient tool": "渐变工具", "Eyedropper tool": "吸管工具",
    "Paint Bucket tool": "油漆桶工具", "Crop tool": "裁剪工具",
    "Lasso tool": "套索工具", "Magic Wand tool": "魔棒工具",
    "Rectangular Marquee tool": "矩形选框工具", "Elliptical Marquee tool": "椭圆选框工具",
    "Clone Stamp tool": "仿制图章工具", "Healing Brush tool": "修复画笔工具",
    "Patch tool": "修补工具", "Spot Healing Brush tool": "污点修复画笔工具",
    "Blur tool": "模糊工具", "Sharpen tool": "锐化工具", "Smudge tool": "涂抹工具",
    "Dodge tool": "减淡工具", "Burn tool": "加深工具", "Sponge tool": "海绵工具",
    "Selection tool": "选择工具", "Direct Selection tool": "直接选择工具",
    "Path Selection tool": "路径选择工具", "Slice tool": "切片工具",
    "Shape tool": "形状工具", "Rectangle tool": "矩形工具",
    "Ellipse tool": "椭圆工具", "Line tool": "直线工具",
    "Custom Shape tool": "自定义形状工具", "Artboard tool": "画板工具",
    "Frame tool": "框架工具", "Content-Aware Fill": "内容识别填充",
    "Free Transform": "自由变换", "Puppet Warp": "操控变形",
    "Perspective Warp": "透视变形", "Content-Aware Scale": "内容识别缩放",
    "Color Balance": "色彩平衡", "Hue/Saturation": "色相/饱和度",
    "Brightness/Contrast": "亮度/对比度", "Levels": "色阶", "Curves": "曲线",
    "Vibrance": "自然饱和度", "Photo Filter": "照片滤镜",
    "Channel Mixer": "通道混合器", "Color Lookup": "颜色查找",
    "Invert": "反相", "Posterize": "色调分离", "Threshold": "阈值",
    "Gradient Map": "渐变映射", "Selective Color": "可选颜色",
    "Black & White": "黑白", "Shadow/Highlight": "阴影/高光",
    "Gaussian Blur": "高斯模糊", "Motion Blur": "动感模糊",
    "Radial Blur": "径向模糊", "Unsharp Mask": "USM 锐化",
    "Smart Sharpen": "智能锐化", "Liquify": "液化",
    "Vanishing Point": "消失点", "Lens Correction": "镜头校正",
    "Adaptive Wide Angle": "自适应广角", "Camera Raw Filter": "Camera Raw 滤镜",
    "New Layer": "新建图层", "Merge Layers": "合并图层",
    "Flatten Image": "拼合图像", "Layer via Copy": "通过拷贝的图层",
    "Layer via Cut": "通过剪切的图层", "Group Layers": "编组图层",
    "Ungroup Layers": "取消编组图层", "Lock Layer": "锁定图层",
    "Clipping Mask": "创建剪贴蒙版", "Layer Mask": "图层蒙版",
    "Deselect": "取消选择", "Reselect": "重新选择", "Inverse": "反选",
    "Select All": "全选", "Feather": "羽化", "Refine Edge": "调整边缘",
    "Quick Mask Mode": "快速蒙版模式", "Color Range": "色彩范围",
    "Step Backward": "后退一步", "Step Forward": "前进一步",
    "Fill": "填充", "Stroke": "描边", "Fit on Screen": "适合屏幕",
    "Actual Pixels": "实际像素", "Toggle grid": "切换网格",
    "Show/Hide Rulers": "显示/隐藏标尺",
    # Illustrator specific
    "Pencil tool": "铅笔工具", "Smooth tool": "平滑工具",
    "Curvature tool": "曲率工具", "Anchor Point tool": "锚点工具",
    "Scissors tool": "剪刀工具", "Knife tool": "美工刀工具",
    "Rotate tool": "旋转工具", "Reflect tool": "镜像工具",
    "Scale tool": "缩放工具", "Shear tool": "倾斜工具",
    "Reshape tool": "改变形状工具", "Width tool": "宽度工具",
    "Warp tool": "变形工具", "Twirl tool": "旋转扭曲工具",
    "Pucker tool": "缩拢工具", "Bloat tool": "膨胀工具",
    "Mesh tool": "网格工具", "Symbol Sprayer tool": "符号喷枪工具",
    "Column Graph tool": "柱形图工具", "Blend tool": "混合工具",
    "Live Paint Bucket tool": "实时上色油漆桶工具",
    "Outline mode": "轮廓模式", "Preview mode": "预览模式",
    "Isolation mode": "隔离模式",
    "Pathfinder": "路径查找器", "Align": "对齐", "Transform": "变换",
    "Make Compound Path": "建立复合路径",
    "Release Compound Path": "释放复合路径",
    "Make Clipping Mask": "建立剪切蒙版",
    "Release Clipping Mask": "释放剪切蒙版",
    "Expand": "扩展", "Expand Appearance": "扩展外观",
    "Join": "连接", "Average": "平均",
    "Outline Stroke": "轮廓化描边",
    "Offset Path": "偏移路径",
    # Premiere / After Effects
    "Razor tool": "剃刀工具", "Ripple Edit tool": "波纹编辑工具",
    "Rolling Edit tool": "滚动编辑工具", "Rate Stretch tool": "比率拉伸工具",
    "Slip tool": "滑动工具", "Slide tool": "滑移工具",
    "Track Select Forward tool": "向前轨道选择工具",
    "Track Select Backward tool": "向后轨道选择工具",
    "Add Edit": "添加编辑点", "Lift": "提升", "Extract": "提取",
    "Mark In": "标记入点", "Mark Out": "标记出点",
    "Clear In": "清除入点", "Clear Out": "清除出点",
    "Go to In": "转到入点", "Go to Out": "转到出点",
    "Render": "渲染", "RAM Preview": "RAM 预览",
    "Set Work Area In": "设置工作区域入点",
    "Set Work Area Out": "设置工作区域出点",
    "Composition": "合成", "Pre-compose": "预合成",
    "Add Keyframe": "添加关键帧", "Easy Ease": "缓动",
    "Easy Ease In": "缓入", "Easy Ease Out": "缓出",
    "Time Stretch": "时间伸缩", "Time Reverse": "时间反转",
    "Freeze Frame": "冻结帧", "Split Layer": "拆分图层",
    "Trim to Work Area": "修剪到工作区域",
}

# VSCode / Development
DEV_ZH: dict[str, str] = {
    "Select current line": "选择当前行",
    "Insert cursor above": "在上方插入光标",
    "Insert cursor below": "在下方插入光标",
    "Add selection to next find match": "将选择添加到下一个查找匹配项",
    "Move line up": "向上移动行", "Move line down": "向下移动行",
    "Copy line up": "向上复制行", "Copy line down": "向下复制行",
    "Delete line": "删除行", "Insert line below": "在下方插入行",
    "Insert line above": "在上方插入行",
    "Toggle line comment": "切换行注释",
    "Toggle block comment": "切换块注释",
    "Toggle word wrap": "切换自动换行",
    "Go to definition": "转到定义",
    "Peek definition": "速览定义",
    "Go to references": "转到引用",
    "Go to symbol": "转到符号",
    "Go to symbol in workspace": "转到工作区中的符号",
    "Show problems panel": "显示问题面板",
    "Open next error": "打开下一个错误",
    "Open previous error": "打开上一个错误",
    "Quick fix": "快速修复", "Rename symbol": "重命名符号",
    "Format document": "格式化文档", "Format selection": "格式化选择",
    "Trigger suggestion": "触发建议",
    "Trigger parameter hints": "触发参数提示",
    "Focus breadcrumbs": "聚焦面包屑导航",
    "Open keyboard shortcuts": "打开键盘快捷键",
    "Open settings": "打开设置", "Open user settings": "打开用户设置",
    "Toggle sidebar visibility": "切换侧边栏可见性",
    "Show explorer": "显示资源管理器",
    "Show search": "显示搜索", "Show source control": "显示源代码管理",
    "Show extensions": "显示扩展", "Show output panel": "显示输出面板",
    "Toggle integrated terminal": "切换集成终端",
    "New terminal": "新建终端",
    "Split terminal": "拆分终端",
    "Start debugging": "开始调试", "Stop debugging": "停止调试",
    "Step over": "单步跳过", "Step into": "单步调试",
    "Step out": "单步跳出", "Continue": "继续",
    "Toggle breakpoint": "切换断点",
    "Find in files": "在文件中查找",
    "Replace in files": "在文件中替换",
    "Open file": "打开文件", "New file": "新建文件",
    "Save all": "全部保存", "Close all": "全部关闭",
    "Close editor": "关闭编辑器",
    "Reopen closed editor": "重新打开已关闭的编辑器",
    "Split editor right": "向右拆分编辑器",
    "Focus into first editor group": "聚焦到第一个编辑器组",
    "Focus into next editor group": "聚焦到下一个编辑器组",
    "Toggle Zen Mode": "切换禅模式",
}

# Obsidian / PKM tools
PKM_ZH: dict[str, str] = {
    "Editor: save file": "编辑器：保存文件",
    "Editor: toggle bold": "编辑器：切换粗体",
    "Editor: toggle italic": "编辑器：切换斜体",
    "Editor: toggle highlight": "编辑器：切换高亮",
    "Editor: toggle strikethrough": "编辑器：切换删除线",
    "Editor: toggle code": "编辑器：切换代码",
    "Editor: toggle blockquote": "编辑器：切换引用块",
    "Editor: toggle bullet list": "编辑器：切换无序列表",
    "Editor: toggle numbered list": "编辑器：切换有序列表",
    "Editor: toggle checklist status": "编辑器：切换清单状态",
    "Editor: insert link": "编辑器：插入链接",
    "Editor: insert callout": "编辑器：插入标注",
    "Open quick switcher": "打开快速切换器",
    "Open command palette": "打开命令面板",
    "Open settings": "打开设置",
    "Open graph view": "打开关系图谱",
    "Create new note": "新建笔记",
    "Navigate back": "向后导航",
    "Navigate forward": "向前导航",
    "Search in all files": "在所有文件中搜索",
    "Toggle left sidebar": "切换左侧边栏",
    "Toggle right sidebar": "切换右侧边栏",
    "Close current tab": "关闭当前标签页",
}

# Blender
BLENDER_ZH: dict[str, str] = {
    "Grab/Move": "移动", "Rotate": "旋转", "Scale": "缩放",
    "Extrude": "挤出", "Extrude Region": "挤出区域",
    "Inset Faces": "内插面", "Loop Cut": "循环切割",
    "Knife": "切刀", "Bevel": "倒角", "Subdivide": "细分",
    "Merge": "合并", "Separate": "分离",
    "Toggle Edit Mode": "切换编辑模式",
    "Toggle Object Mode": "切换物体模式",
    "Toggle Sculpt Mode": "切换雕刻模式",
    "Set Origin": "设置原点", "Apply Transformation": "应用变换",
    "Shade Smooth": "平滑着色", "Shade Flat": "平直着色",
    "Add Mesh": "添加网格", "Add Curve": "添加曲线",
    "Add Surface": "添加曲面", "Add Light": "添加灯光",
    "Add Camera": "添加相机", "Render Image": "渲染图像",
    "Render Animation": "渲染动画",
    "Set Keyframe": "设置关键帧", "Delete Keyframe": "删除关键帧",
    "Play Animation": "播放动画", "Toggle Sidebar": "切换侧边栏",
    "Toggle Properties": "切换属性面板",
    "Toggle Full Screen Area": "切换全屏区域",
    "Numpad View": "小键盘视图", "Camera View": "摄像机视图",
    "Focus Object": "聚焦物体", "Hide Selected": "隐藏所选",
    "Unhide All": "全部取消隐藏",
}

# Communication apps (Discord, Telegram, WhatsApp, Zoom, etc.)
COMM_ZH: dict[str, str] = {
    "Toggle Mute": "切换静音", "Toggle Deafen": "切换全部静音",
    "Mute/Unmute": "静音/取消静音",
    "Start/Stop Video": "开始/停止视频",
    "Share Screen": "共享屏幕", "Start Screen Share": "开始共享屏幕",
    "Stop Screen Share": "停止共享屏幕",
    "Leave Call": "离开通话", "End Meeting": "结束会议",
    "Raise Hand": "举手", "Toggle Chat": "切换聊天",
    "Toggle Participants": "切换参会者列表",
    "Push to Talk": "按键通话",
    "Mark as Read": "标记为已读", "Mark as Unread": "标记为未读",
    "Pin Message": "固定消息", "Delete Message": "删除消息",
    "Edit Message": "编辑消息", "Reply": "回复",
    "React": "添加反应", "Upload File": "上传文件",
    "Create Thread": "创建话题", "Search": "搜索",
    "Toggle Member List": "切换成员列表",
    "Scroll to Oldest Unread": "滚动到最早未读",
    "Create DM": "创建私信", "Emoji Picker": "表情选择器",
    "GIF Picker": "GIF 选择器",
    "Navigate to Home": "导航到主页",
    "Navigate to DMs": "导航到私信",
}

# Productivity (Things, Todoist, Linear, etc.)
PRODUCTIVITY_ZH: dict[str, str] = {
    "New To-Do": "新建待办", "New Todo": "新建待办",
    "New Project": "新建项目", "Quick Entry": "快速录入",
    "Quick Add": "快速添加", "Quick Find": "快速查找",
    "Show Inbox": "显示收件箱", "Show Today": "显示今天",
    "Show Upcoming": "显示即将到来", "Show Anytime": "显示随时",
    "Show Someday": "显示将来某天", "Show Logbook": "显示日志",
    "Show Trash": "显示回收站", "Complete": "完成",
    "Cancel": "取消", "Move to...": "移动到…",
    "Schedule": "计划", "Add Deadline": "添加截止日期",
    "Add Tag": "添加标签", "Move to Inbox": "移动到收件箱",
    "Show/Hide Sidebar": "显示/隐藏侧边栏",
    "Archive": "归档", "Snooze": "稍后提醒",
    "Set Priority": "设置优先级",
    "Set Status": "设置状态",
    "Assign to me": "分配给我",
    "Add sub-issue": "添加子事项",
    "Copy issue URL": "复制事项 URL",
    "Copy issue ID": "复制事项 ID",
}

# Finder & macOS system apps
MACOS_ZH: dict[str, str] = {
    "New Finder Window": "新建 Finder 窗口",
    "New Folder": "新建文件夹", "New Smart Folder": "新建智能文件夹",
    "Get Info": "显示简介", "Show Original": "显示原身",
    "Add to Sidebar": "添加到侧边栏",
    "Quick Look": "快速查看", "Show Path Bar": "显示路径栏",
    "Show Status Bar": "显示状态栏",
    "Show View Options": "显示视图选项",
    "Show/Hide Sidebar": "显示/隐藏侧边栏",
    "Empty Trash": "清倒废纸篓",
    "Move to Trash": "移到废纸篓",
    "Connect to Server": "连接服务器",
    "Show Desktop": "显示桌面",
    "Go to Folder": "前往文件夹",
    "Go to Home": "前往个人目录",
    "Computer": "电脑", "AirDrop": "隔空投送",
    "iCloud Drive": "iCloud 云盘",
    "Applications": "应用程序",
    "Downloads": "下载", "Documents": "文稿",
    "Column View": "分栏视图", "Icon View": "图标视图",
    "List View": "列表视图", "Gallery View": "画廊视图",
    "Eject": "推出",
}

# Music / DAW terms (Logic Pro, Ableton, GarageBand, etc.)
MUSIC_ZH: dict[str, str] = {
    "Play/Stop": "播放/停止", "Play/Pause": "播放/暂停",
    "Record": "录制", "Stop": "停止", "Rewind": "快退",
    "Fast Forward": "快进", "Go to Beginning": "转到开头",
    "Go to End": "转到结尾", "Go to Position": "转到位置",
    "Cycle Mode": "循环模式", "Toggle Cycle": "切换循环",
    "Toggle Metronome": "切换节拍器",
    "Count-in": "预备拍",
    "Create Track": "新建轨道",
    "Delete Track": "删除轨道",
    "Duplicate Track": "复制轨道",
    "Mute Track": "静音轨道",
    "Solo Track": "独奏轨道",
    "Arm Track": "启用录制轨道",
    "Bounce": "混缩导出", "Bounce in Place": "就地混缩",
    "Normalize": "标准化", "Fade In": "淡入", "Fade Out": "淡出",
    "Crossfade": "交叉淡化",
    "Quantize": "量化", "Transpose": "移调",
    "Automation": "自动化",
    "Show/Hide Mixer": "显示/隐藏混音器",
    "Show/Hide Inspector": "显示/隐藏检查器",
    "Show/Hide Library": "显示/隐藏资源库",
    "Show/Hide Loop Browser": "显示/隐藏循环浏览器",
    "Snap to Grid": "吸附到网格",
}


# ---------------------------------------------------------------------------
# General pattern-based translations
# ---------------------------------------------------------------------------
GENERAL_PATTERNS: list[tuple[str, str]] = [
    (r"^Toggle (.+)$", r"切换\1"),
    (r"^Show/Hide (.+)$", r"显示/隐藏\1"),
    (r"^Show (.+)$", r"显示\1"),
    (r"^Hide (.+)$", r"隐藏\1"),
    (r"^Open (.+)$", r"打开\1"),
    (r"^Close (.+)$", r"关闭\1"),
    (r"^New (.+)$", r"新建\1"),
    (r"^Add (.+)$", r"添加\1"),
    (r"^Remove (.+)$", r"移除\1"),
    (r"^Delete (.+)$", r"删除\1"),
    (r"^Insert (.+)$", r"插入\1"),
    (r"^Select (.+)$", r"选择\1"),
    (r"^Go to (.+)$", r"转到\1"),
    (r"^Jump to (.+)$", r"跳转到\1"),
    (r"^Move (.+)$", r"移动\1"),
    (r"^Resize (.+)$", r"调整大小\1"),
    (r"^Rename (.+)$", r"重命名\1"),
    (r"^Switch to (.+)$", r"切换到\1"),
    (r"^Navigate to (.+)$", r"导航到\1"),
    (r"^Scroll (.+)$", r"滚动\1"),
    (r"^Focus (.+)$", r"聚焦\1"),
    (r"^Reset (.+)$", r"重置\1"),
    (r"^Clear (.+)$", r"清除\1"),
    (r"^Enable (.+)$", r"启用\1"),
    (r"^Disable (.+)$", r"禁用\1"),
    (r"^Expand (.+)$", r"展开\1"),
    (r"^Collapse (.+)$", r"折叠\1"),
]


# Merge all domain dictionaries
ALL_EXACT: dict[str, str] = {}
for d in [ADOBE_ZH, DEV_ZH, PKM_ZH, BLENDER_ZH, COMM_ZH, PRODUCTIVITY_ZH, MACOS_ZH, MUSIC_ZH]:
    ALL_EXACT.update(d)


def is_untranslated(en: str, zh: str) -> bool:
    """Check if zh-Hans is essentially the same as en (untranslated)."""
    if not zh:
        return True
    # If zh contains mostly ASCII/latin chars, it's likely untranslated
    non_ascii = sum(1 for c in zh if ord(c) > 127)
    if non_ascii == 0:
        return True
    # If zh == en exactly
    if zh == en:
        return True
    return False


def translate_item(en: str, current_zh: str, bundle_id: str) -> str:
    """Try to find a better translation for an item title."""
    # 1. Exact match in domain dictionaries
    if en in ALL_EXACT:
        return ALL_EXACT[en]

    # 2. If already has good Chinese translation, keep it
    if not is_untranslated(en, current_zh):
        return current_zh

    # 3. Try pattern-based translation (only if fully untranslated)
    for pat, repl in GENERAL_PATTERNS:
        m = re.match(pat, en)
        if m:
            # Only apply if the captured group is short enough
            rest = m.group(1) if m.lastindex else ""
            if len(rest) < 40:
                result = re.sub(pat, repl, en)
                return result

    # 4. Return current (even if untranslated — better than nothing)
    return current_zh


# ---------------------------------------------------------------------------
# Process files
# ---------------------------------------------------------------------------
def process_file(filepath: Path) -> tuple[int, int]:
    """Process a single preset JSON file. Returns (total_items, improved_items)."""
    data = json.loads(filepath.read_text("utf-8"))
    bundle_id = data.get("bundleIdentifier", "")
    total = 0
    improved = 0

    for cat in data.get("categories", []):
        # Try to improve category title zh-Hans
        cat_en = cat["title"]["en"]
        cat_zh = cat["title"].get("zh-Hans", cat_en)
        if is_untranslated(cat_en, cat_zh):
            # Try common category translations
            from batch_fetch_new_apps import CATEGORY_ZH as CAT_MAP
            if cat_en in CAT_MAP:
                cat["title"]["zh-Hans"] = CAT_MAP[cat_en]

        for item in cat.get("items", []):
            total += 1
            en = item["title"]["en"]
            zh = item["title"].get("zh-Hans", en)

            new_zh = translate_item(en, zh, bundle_id)
            if new_zh != zh:
                item["title"]["zh-Hans"] = new_zh
                improved += 1

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return total, improved


def main():
    presets_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "presets"

    # Add scripts dir to path for importing CATEGORY_ZH
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    files = sorted(presets_dir.glob("*.json"))
    print(f"[INFO] Processing {len(files)} preset files...", file=sys.stderr)

    total_items = 0
    total_improved = 0

    for f in files:
        try:
            t, i = process_file(f)
            total_items += t
            total_improved += i
            if i > 0:
                print(f"  {f.name}: {i}/{t} items improved", file=sys.stderr)
        except Exception as e:
            print(f"  ERROR {f.name}: {e}", file=sys.stderr)

    print(f"\n[DONE] Total items: {total_items}, Improved translations: {total_improved}", file=sys.stderr)


if __name__ == "__main__":
    main()
