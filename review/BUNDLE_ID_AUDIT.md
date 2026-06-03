# Bundle ID 校验（应用不显示快捷键的根因）

应用按 **macOS 真实 bundle id** 去拉 `presets/<bundleId>.json`。若文件名与真实 bundle id 不一致
（包括大小写不同），应用就拉不到 → **不显示快捷键**。

修复机制：Menu_Product 里的 `RemoteShortcutPresetBundleAlias.swift` 有别名表，
把"应用真实 bundle id"映射到"预设文件名"。目前只有 1 条（ChatGPT）。本次需扩充。

---

## 已确认的不匹配（本机已安装应用实测）

| 应用 | 真实 bundle id | 预设文件名 | 问题 | 建议 |
|------|----------------|------------|------|------|
| Cursor | `com.todesktop.230313mzl4w4u92` | `com.cursor.Cursor.json` | 完全不匹配（ToDesktop 打包，id 随安装变化） | 加 alias（注意此 id 可能因版本变化，需以实测为准） |
| Dia | `company.thebrowser.dia` | `com.browsercompany.dia.json` | 完全不匹配 | 加 alias |
| 企业微信 | `com.tencent.WeWorkMac` | `com.tencent.weworkmac.json` | **仅大小写不同** | 加 alias（或把文件改名为大小写一致） |
| ChatGPT | `com.openai.chat` | `com.openai.chatgpt.json` | 已有 alias | 无需改 |

### 建议补充到别名表（`menuAppToRemoteFileStem`）
```swift
"com.openai.chat": "com.openai.chatgpt",          // 已有
"com.todesktop.230313mzl4w4u92": "com.cursor.Cursor",
"company.thebrowser.dia": "com.browsercompany.dia",
"com.tencent.WeWorkMac": "com.tencent.weworkmac",
```

> 说明：以上为本机实测结果。其余 ~150 个应用未安装、无法实测真实 bundle id，
> 需要后续在更多机器上抽测，或对已知有差异的应用（社区预设常用 pie-menu.com 的 id）逐个核对。

---

## Codex 的情况（澄清）

`Codex.app` 的真实 bundle id 就是 `com.openai.codex`，**与预设文件名一致，bundle id 没问题**。
若它仍显示异常，是这些**数据质量 bug**导致，与 bundle id 无关：

- `Next thread` / `Forward`：`displayKey` 写成了 `"30"`（keyCode 30 应显示为 `]`）→ 键位显示错误。
- `Force reload skills` / `Go to skills`：`keyCode:0, carbonModifiers:0` 的单键 → 被 App 过滤，不显示。
- `Force reload skills` 的 `zh-Hans` 未翻译（等于英文）。

这些在数据侧修 `presets/com.openai.codex.json` 即可。
