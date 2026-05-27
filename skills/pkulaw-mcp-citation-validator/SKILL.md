---
name: pkulaw-mcp-citation-validator
description: >
  法条引用核验与纠偏，用于检查草稿、问答、备忘或合同审查记录里已经写出来的法条引用是否准确、一致、可追溯。Use when：用户已经有一段文本，想确认其中法规名称、条号或引用表达是否可靠。NOT for：主题检索法规、案例检索、案号识别、以及未形成引用文本前的纯资料探索。要求只依据当次核验返回给出“命中 / 不命中 / 需复核”结论，不得把未核验内容写成已确认依据。
license: MIT
metadata:
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    product_lines:
      - 修正生成幻觉-法条
    server_ids:
      - citation-validator
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：法条引用核验（citation-validator）

这个 Skill 只负责一件事：**检查已经写出来的法条引用是否需要修正。**

它不负责替代法规检索，也不负责直接判断实体结论一定成立。
如果用户还没有引用文本，只是想“先找相关法规”，应转到法规检索或精准法条 Skill。

## 先看边界

- “核验通过”只表示与当次工具返回一致，不等于已经完成正式法律审查。
- 命中不明确、存在歧义、或文本本身表述过于含混时，只能标记“需人工复核”。
- 不得把核验工具的返回扩大解释成“结论当然正确”。

## 默认路由

- 用户给你一段已有草稿、问答、摘要、审查意见，想核对法条引用：
  - 走 `citation-validator`
- 用户想先找法规依据：
  - 转 `pkulaw-mcp-law-retrieval` 或 `pkulaw-mcp-fatiao-precise`

## 推荐工作流

1. 先确认用户提供的是待核验文本，而不是单纯检索需求。
2. 用 `tools` 确认真实 `<toolName>` 与参数名。
3. 提交待核验文本。
4. 按“原引用 -> 核对状态 -> 修正建议”整理输出。
5. 把“命中”“不命中”“需复核”明确分开。

## 失败与降级

### 允许的失败输出

```markdown
当前未拿到法条引用核验结果。

失败原因：
- [未认证 / 无订阅 / 无结果 / 工具不存在 / 命令报错]

建议动作：
- 检查 `pkulaw-mcp` 配置
- 检查引用文本是否过短或过于含混
- 如需先找法规，请转到法规检索或精准法条路径
```

### 允许的保守输出

- 结果不明确 -> 标记“需人工复核”
- 不得强行写“核验通过”

## 输出结构

1. 原引用
2. 核对状态
3. 修正建议
4. 备注（如需人工复核）

## 终端复现与排障

如需在终端复现，请先安装 `@pkulaw/mcp-cli`；安装后命令为 `pkulaw-mcp`。

```bash
pkulaw-mcp tools citation-validator
pkulaw-mcp citation-validator <toolName> ... --json
```

## 补充材料

- 示例见 [examples.md](examples.md)
