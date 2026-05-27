---
name: pkulaw-mcp-law-retrieval
description: >
  北大法宝原生 MCP 的法规/精准法条检索 Skill。当前本机已配置 `law-keyword`（检索法律法规-关键词）和 `fatiao`（精准查找法条-关键词），不得假定 `law-semantic`、`law-recognition` 等旧 MCP 可用。Use when：用户明确要找法规、规范性文件、司法解释、配套依据，或希望围绕一个法律问题先找相关法规材料；若已知法规名加条号，需要优先走精准法条。NOT for：案例检索、案号识别、网页端登录、网页详情页点击、复制网页 URL；网页兜底应转用户自建的 `pkulaw-legal-search`。须已配置并订阅法宝 MCP；禁止无检索依据编造法规名称、文号、条号或效力状态。
license: MIT
metadata:
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    product_lines:
      - 检索法律法规-关键词
      - 精准查找法条-关键词
    server_ids:
      - law-keyword
      - fatiao
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：法律法规检索

这个 Skill 只负责一件事：**把法规资料找出来，并按可复核的方式交给后续分析或答复环节。**

它和 `pkulaw-legal-search` 不重复：本 Skill 只走原生 MCP 的法规/法条能力；MCP 不通、当前会话没加载对应工具、返回 401/403/超时/无结果、结果不足、需要网页详情页、登录态或 Computer Use 时，立即转 `pkulaw-legal-search`。

当前覆盖两个已配置的原生 MCP 服务：

| 路径 | serverId | 什么时候优先用 |
|------|----------|----------------|
| 关键词检索 | `law-keyword` | 用户已给出法规标题词、正文关键词、概念词，希望返回列表 |
| 精准法条 | `fatiao` | 用户已给出法规名 + 条号，或需要核对条文原文 |

如果任务已经明确是“只查案例”，请转到 [pkulaw-mcp-case-retrieval](../pkulaw-mcp-case-retrieval/SKILL.md)。如果任务是“已知法规名 + 条号取全文”，优先走 `fatiao`；如果当前会话尚未暴露该 MCP，再用 `law-keyword` 找法规线索并转网页端详情页核对条号和原文。

## 先看边界

- 本 Skill 的目标是**找依据**，不是直接形成最终法律意见。
- 返回到的法规材料，仍需结合时效、层级、适用范围、特别法与一般法关系继续判断。
- 若用户要求形成可交付答复，应把检索结果继续交给组合型 Skill，而不是在这里直接扩写结论。

## 必须遵守的规则

1. 未成功拿到 MCP 返回前，不得写出具体法规名称、文号、条号或效力判断。
2. 只允许基于当次返回内容做摘要，不得用模型记忆补齐缺失依据。
3. 关键词路径下，`title` 与 `fulltext` 至少有一项；具体参数名仍以 `tools` 输出为准。
4. 出现 `401/403`、无结果、超时或工具不存在时，只能说明失败原因与下一步建议，不能空答。
5. 不得调用或建议调用未订阅的 `law-semantic`、`law-recognition`、`citation-validator`、`doc-link`、`semantic-nlsql`。
6. MCP 路由失败或结果不足时，默认转 `pkulaw-legal-search` 的网页/Computer Use 流程继续核查。

## 默认路由

按下面顺序判断：

1. 用户给的是明确词组、法规标题、正文关键词：
   - 先走 `law-keyword`
2. 用户给的是明确法规名 + 条号：
   - 先走 `fatiao`，当前实测工具名为 `get_law_item_content`，参数为 `title` 和 `tiao_num`
3. 用户给的是案情描述、业务问题、咨询问题：
   - 先提炼 1-3 个关键词，再走 `law-keyword`
4. 关键词结果太少、过窄：
   - 换法律全称/简称、制度名、核心行为、责任类型或相关主体再检索

默认不要假设语义检索可用；本机当前只跑关键词路径。

## 推荐工作流

1. 先把用户需求收敛成“要找哪一类法规依据”。
2. 选择 `law-keyword`。
3. 用 `tools` 确认真实 `<toolName>` 与参数名。
4. 完成一次检索。
5. 只整理当次返回里的标题、摘要、时效、链接等信息。
6. 若结果不足，再做一次有理由的补检索，而不是盲目多工具并发。

## 失败与降级

### 允许的失败输出

只允许类似下面的结构：

```markdown
当前未拿到法宝法规检索结果。

失败原因：
- [未认证 / Token 失效 / 无订阅 / 无结果 / 工具不存在 / 命令报错]

建议动作：
- 检查 `pkulaw-mcp` 配置与 Token
- 检查对应服务是否已订阅
- 将问题改写得更具体后重试
```

### 允许的降级方式

- `law-keyword` 结果过宽 -> 增加标题词、正文词或限定法律部门
- `law-keyword` 结果过窄 -> 换同义词、法律全称/简称、核心制度词后重试
- 仍无结果 -> 停止继续生成法律结论，只说明未检索到足够依据

## 终端复现与排障

如需在终端复现，请先安装 `@pkulaw/mcp-cli`；安装后命令为 `pkulaw-mcp`。

```bash
pkulaw-mcp tools law-keyword
pkulaw-mcp law-keyword <toolName> --title "劳动合同"
```

说明：

- `<toolName>` 必须以 `pkulaw-mcp tools <serverId>` 的输出为准
- 当前实测工具名为 `get_law_list`，但正式环境中仍应以 `tools/list` 返回为准

## 输出结构

按下面结构输出最稳：

1. 问题重述
2. 检索路径（关键词或语义，为什么这样选）
3. 关键结果片段
4. 初步观察
5. 待复核点

## 补充材料

- 示例见 [examples.md](examples.md)
- 总路由见 [pkulaw-mcp-legal-research](../pkulaw-mcp-legal-research/SKILL.md)
- npm CLI 包 `@pkulaw/mcp-cli`：<https://gitee.com/pkulaw/pkulaw-mcp-cli> · [npm](https://www.npmjs.com/package/@pkulaw/mcp-cli)
