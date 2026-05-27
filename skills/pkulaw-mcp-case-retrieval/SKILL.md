---
name: pkulaw-mcp-case-retrieval
description: >
  检索司法案例与裁判文书资料。当前本机只订阅 `case-keyword`（检索司法案例-关键词），不得假定 `case-semantic`、`case-number` 等旧 MCP 可用。Use when：用户明确要找类案、裁判样本、裁判文书线索，或希望围绕一个争议问题先看法院如何处理。NOT for：法规检索、已知法条的精准全文查询、案号识别溯源、以及未经过检索就直接概括“法院通常怎么判”的任务。须已配置并订阅法宝 MCP；禁止无检索依据编造案号、法院名称、裁判日期或裁判要旨。
license: MIT
metadata:
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    product_lines:
      - 检索司法案例-关键词
    server_ids:
      - case-keyword
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：司法案例检索

这个 Skill 只负责一件事：**把类案样本与裁判线索找出来，并按可复核的方式交给后续分析或备忘环节。**

当前只覆盖一个已订阅并实测可用的原生 MCP 服务：

| 路径 | serverId | 什么时候优先用 |
|------|----------|----------------|
| 关键词检索 | `case-keyword` | 用户已给出案由词、争点词、标题词，想返回案例列表 |

如果任务已经明确是“只查法规”，请转到 [pkulaw-mcp-law-retrieval](../pkulaw-mcp-law-retrieval/SKILL.md)。如果任务是“识别案号并溯源”，本机当前没有案号识别 MCP 订阅；可把案号作为关键词用 `case-keyword` 检索，必要时转网页端详情页核对。

## 先看边界

- 本 Skill 的目标是**找样本、看裁判线索**，不是直接替用户做胜诉承诺或给出确定裁判结论。
- 检索到的少量样本不能直接概括成“法院一定怎么判”。
- 若用户要形成正式类案备忘或办案备忘，建议把结果继续交给组合型 Skill。

## 必须遵守的规则

1. 未成功拿到 MCP 返回前，不得写出具体案号、法院名称、裁判日期或裁判要旨。
2. 只允许基于当次返回内容做摘要，不得用模型记忆补齐案例细节。
3. 关键词路径下，`title` 与 `fulltext` 至少有一项；具体参数名仍以 `tools` 输出为准。
4. 出现 `401/403`、无结果、超时或工具不存在时，只能说明失败原因与下一步建议。
5. 不得调用或建议调用未订阅的 `case-semantic`、`case-number`、`semantic-nlsql`、`doc-link`。

## 默认路由

按下面顺序判断：

1. 用户给了明确关键词、案由词、争点词：
   - 先走 `case-keyword`
2. 用户给的是一整段争议描述，希望找类似案子：
   - 先提炼案由、争点、核心事实、法律关系等关键词，再走 `case-keyword`
3. 关键词结果太少：
   - 换案由词、争点词、合同类型、法院层级或核心事实词后重试

默认不要假设语义检索可用；本机当前只跑关键词路径。

## 推荐工作流

1. 先把用户问题收敛成“想看哪类案例样本”。
2. 选择 `case-keyword`。
3. 用 `tools` 确认真实 `<toolName>` 与参数名。
4. 完成一次检索。
5. 只整理当次返回里的案号、法院、裁判日期、摘要、链接等信息。
6. 若结果不足，再做一次有理由的补检索。

## 失败与降级

### 允许的失败输出

```markdown
当前未拿到法宝案例检索结果。

失败原因：
- [未认证 / Token 失效 / 无订阅 / 无结果 / 工具不存在 / 命令报错]

建议动作：
- 检查 `pkulaw-mcp` 配置与 Token
- 检查对应服务是否已订阅
- 将争议点改写得更具体后重试
```

### 允许的降级方式

- `case-keyword` 结果太宽 -> 增加案由词、争点词、法院层级或核心事实词
- `case-keyword` 结果太少 -> 换同义词、案由词、法律关系词后重试
- 仍无结果 -> 停止继续概括裁判倾向，只说明未检索到足够样本

## 终端复现与排障

如需在终端复现，请先安装 `@pkulaw/mcp-cli`；安装后命令为 `pkulaw-mcp`。

```bash
pkulaw-mcp tools case-keyword
pkulaw-mcp case-keyword <toolName> --title "房屋租赁"
```

说明：

- `<toolName>` 必须以 `pkulaw-mcp tools <serverId>` 的输出为准
- 当前实测工具名为 `get_case_list`，但正式环境中仍应以 `tools/list` 返回为准

## 输出结构

按下面结构输出最稳：

1. 问题重述
2. 检索路径（关键词或语义，为什么这样选）
3. 关键案例片段
4. 样本观察
5. 待复核点

## 补充材料

- 示例见 [examples.md](examples.md)
- 法规检索见 [pkulaw-mcp-law-retrieval](../pkulaw-mcp-law-retrieval/SKILL.md)
- 总路由见 [pkulaw-mcp-legal-research](../pkulaw-mcp-legal-research/SKILL.md)
- npm CLI 包 `@pkulaw/mcp-cli`：<https://gitee.com/pkulaw/pkulaw-mcp-cli> · [npm](https://www.npmjs.com/package/@pkulaw/mcp-cli)
