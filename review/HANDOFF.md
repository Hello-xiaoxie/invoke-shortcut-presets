# 交接说明（给接手的模型，如 composer-2.5-fast）

你正在接手 `invoke-shortcut-presets` 的快捷键预设整理工作。**先读 `review/SCHEMA.md` 了解数据结构**，再按本文件干活。
数据源永远是 `presets/*.json`；你的产出写进两个覆盖文件，再跑脚本生成 CSV 供人审查。

---

## 核心任务

逐个应用处理，每个应用做两件事：
1. **翻译** zh-Hans 中"待翻译"的功能名（中英混杂或纯英文）。
2. **挑选 4-6 个默认快捷键**（is_default_suggested）。

### 翻译的第一原则（最重要）
**优先联网查官方术语，不要凭空直译。** 顺序：
1. 先查该应用的**官方中文界面 / 官方中文文档 / 官方帮助中心**，用它的标准译名。
   - 例：Rive 的 `Translate Tool` 官方叫"平移工具"（不是"翻译工具"）；查到来源 rive.org.cn。
2. 查不到官方中文，再查权威中文教程/社区通用译法。
3. 实在没有，才按语义准确翻译（注意上下文：design 软件里 translate=平移、stroke=描边、fill=填充等）。
4. 专有名词保留英文（见 `scripts/translation_whitelist.json`）：Figma/Notion/AI/URL/PDF/Git 等。

---

## 工作流（命令）

```bash
# 1. 看某个应用要翻什么 + 默认候选（已按 App 过滤+打分排序）
python3 scripts/app_worksheet.py <bundle_id>            # 可一次多个

# 2. 联网查官方术语后，把翻译写进 glossary（英文→中文，全局复用），把默认写进 defaults
python3 - <<'PY'
import json
g=json.load(open("review/glossary.json",encoding="utf-8"))
g.update({ "English action": "中文译名", ... })
json.dump(g,open("review/glossary.json","w",encoding="utf-8"),ensure_ascii=False,indent=2,sort_keys=True)
d=json.load(open("review/defaults.json",encoding="utf-8"))
d["<bundle_id>"]=["<item_id1>", ...]   # 4-6 个，从 app_worksheet 的"默认候选"里挑
json.dump(d,open("review/defaults.json","w",encoding="utf-8"),ensure_ascii=False,indent=2,sort_keys=True)
PY

# 3. 重新生成 CSV
python3 scripts/build_review_table.py
```

> glossary 的 key 是**英文功能名原文**（去掉首尾空格），同一英文在所有应用里复用同一中文。

---

## 默认 4-6 个的挑选规则（已确立）
- 只从 `app_worksheet` 打印的"默认候选"里挑（这些已通过 App 过滤：有 ⌘/⌃ 等标准修饰键、非单键）。
- **尽量跨分类**，覆盖该应用最核心高频的功能。
- 优先：新建/打开/查找/搜索/切换面板/导航等实用项；避开纯复制粘贴撤销。
- 数量 4-6，能 6 就 6。

---

## 已确立的术语规范（保持一致）
- Tool → 工具；Tab → 标签页；Block → 块；Thread/Chat → 会话/对话；Window → 窗口
- Toggle → 切换；Sidebar → 侧边栏；Terminal → 终端；Bookmark → 书签
- Selection/selected → 所选；Duplicate → 创建副本；Rename → 重命名
- 设计软件：Translate → 平移；Rotate → 旋转；Scale → 缩放；Artboard → 画板；
  Group → 编组；Vertices → 顶点；State Machine → 状态机；playhead → 播放头
- 不加句号；占位符/符号原样保留。

---

## 进度（截至 batch 1 完成）
- 已完成 **21** 个应用（含默认 4-6 个）：此前 12 个 + 本批 9 个（Figma, Word, Excel, Xcode, Luki, Keynote, Numbers, Pages, iMovie）
- **腾讯会议** 翻译已完整，但快捷键全是 ⌥ 单修饰键 → App 无法选为默认（`is_default_suggested` 为空，属预期）
- glossary 术语 **~618** 条；`待翻译` 从 7626 降至 **7176**
- 下一批建议：PowerPoint, Outlook, Blender, Android Studio, GarageBand, VS Code, Figma 已完成…
- 大户（先有心理准备）：Adobe After Effects 235、Lightroom 214、Photoshop 175、RStudio 159、Outlook 137…
  这些都有官方中文界面，**务必查 Adobe/Microsoft 官方中文菜单术语**。

## 建议顺序
1. 用户本机已装的剩余应用（Office: Word/Excel/PPT/Outlook、Xcode、Blender、Figma、Android Studio、iWork: Keynote/Numbers/Pages、Luki、Tencent Meeting、WeWork、GarageBand、iMovie）
2. 设计/创意大户（Adobe 全家桶、Sketch、Affinity）
3. 其余按 remaining_apps.md 顺序

## 收尾
全部做完后跑 `python3 scripts/build_review_table.py`，确认 `待翻译` 计数为 0（或仅剩白名单专名），交用户在 `review/review.csv` 审查。
其它遗留问题见 `review/BUNDLE_ID_AUDIT.md`（Cursor/Dia/企业微信 的 bundle id 需在 Menu_Product 的 Swift 别名表补充；Codex 的 displayKey "30" 等数据 bug）。
