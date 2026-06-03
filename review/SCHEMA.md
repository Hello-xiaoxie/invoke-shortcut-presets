# invoke-shortcut-presets — 数据结构与审查说明

本文件供人（审查时）和 AI（后续维护时）理解数据结构。**真正的数据源永远是 `presets/*.json`**，
`review/review.csv` 与各 MD 文件都是由 `scripts/build_review_table.py` 从 JSON 生成的派生产物。
流程：在 CSV/MD 上批注 → 改 `presets/*.json` → 重新跑脚本生成 CSV。

---

## 1. 目录与产物

| 路径 | 说明 |
|------|------|
| `presets/<bundleId>.json` | **数据源**。每个 macOS 应用一个文件，文件名 = 应用 bundle id |
| `scripts/app_names.json` | bundleId → 应用展示名 的映射 |
| `scripts/build_review_table.py` | 从 JSON 生成 `review/review.csv` |
| `scripts/translate_presets.py` | LLM 批量重译 zh-Hans（写回 JSON），需要 API key |
| `review/review.csv` | **审查主表**（用 Excel / Numbers 打开，可筛选/排序） |
| `review/BUNDLE_ID_AUDIT.md` | bundle id 不匹配问题（导致应用不显示快捷键） |

---

## 2. 单个预设 JSON 的字段类型（供 AI 理解）

```jsonc
{
  "bundleIdentifier": "string",        // 必须 = macOS 应用真实 bundle id，否则应用查不到
  "i18n": {
    "defaultLocale": "string",         // 固定 "en"
    "locales": ["en", "zh-Hans"]       // string[]
  },
  "categories": [                       // 分类数组
    {
      "id": "string",                   // 稳定唯一 id，如 "remote.figma.tools"
      "title": { "en": "string", "zh-Hans": "string" },   // 始终是双语对象
      "items": [
        {
          "id": "string",               // 稳定唯一 id（哈希后缀）
          "title": { "en": "string", "zh-Hans": "string" },// 始终双语对象
          "shortcutConfiguration": {
            "keyCode": 0,               // number, macOS 虚拟键码 (Carbon kVK_*)
            "carbonModifiers": 0,       // number, 位掩码: ⌘256 ⇧512 ⌥2048 ⌃4096 fn(1<<24)
            "displayKey": "string"      // 人读键名: "S" "↩" "Space" "⎋" 等
          },
          "shortcutDisplayTokens": ["string"],  // 可选, 仅展示用的多键/按住型 token (全库 8 条)
          "searchKeywords": ["string"]          // 可选, 双语搜索别名 (全库 19 条)
        }
      ]
    }
  ]
}
```

数据现状（共 172 应用 / 11363 条快捷键）：
- 所有 `title` 都是 `{en, zh-Hans}` 对象，无纯字符串。
- 全库 **没有** `additionalKeyCodes`（多键序列）字段。
- `carbonModifiers` 位掩码：`⌘=256, ⇧=512, ⌥=2048, ⌃=4096, fn=16777216`。组合相加，如 `⌘⇧=768`、`⌘⌥=2304`。

---

## 3. review.csv 列含义

| 列 | 含义 |
|----|------|
| `app_name` | 应用展示名（来自 `scripts/app_names.json`） |
| `bundle_id` | 应用 bundle id |
| `category_zh` / `category_en` | 分类中/英文名 |
| `action_en` | 功能英文名 |
| `action_zh_original` | 功能中文名（**当前 JSON 里的原值**，仅供对照） |
| `action_zh_final` | **最终会用的中文**（重译过的用新译，否则用原值）。**审查主要看这一列** |
| `status` | `原本已是中文`（无需处理）/ `已重译`（本次修过）/ `待翻译`（仍是英文或混杂，待处理） |
| `key` | 键位展示串，如 `⌘⇧A`、`S` |
| `is_default_suggested` | ✓ = **策划的默认 4-6 个**（你审查这一列的打勾） |
| `is_default_current_algo` | ✓ = 当前 App 启发式算法会自动选的（仅供对比参考） |
| `default_eligible` | ✓ = 通过 App 过滤（有标准修饰键、非弱修饰纯字符），才有资格成为默认 |
| `single_key` | ✓ = 单键（无 ⌘/⌃/⌥/⇧）；当前 App 会过滤掉，不参与默认 |
| `dup_group` | 同一应用内英文名归一化后重复的功能，标同一组号（如 G1），供"一功能多快捷键"人工保留一个 |
| `item_id` | 条目唯一 id（回写 JSON 用） |

> **怎么看**：只看 `action_zh_final` 列即可，它永远是当前最好的中文；按 `status = 待翻译`
> 筛选就能看到所有还没处理的。空白困惑已消除。

### 当前数据统计
- 翻译状态：`原本已是中文` **3046**、`已重译` **691**、`待翻译` **7626**
- 单键 `single_key`：**2306**（不改，仅标记）
- 有资格做默认 `default_eligible`：**8005**
- 疑似重复功能组 `dup_group`：**245** 组

---

## 4. 应用清单（172）

见 `scripts/app_names.json`（bundleId → 名称）。在 `review.csv` 中按 `app_name` 列筛选即可逐应用审查。
