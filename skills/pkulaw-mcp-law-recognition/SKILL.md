---
name: pkulaw-mcp-law-recognition
description: >
  法条识别与溯源，用于从合同、函件、答复、备忘或其他长文本里识别潜在法规引用，并给出可继续核查的来源线索。Use when：用户已经有一段文本，想自动识别其中提到的法规名、条号或引用表达。NOT for：法规主题检索、已知法规名加条号的精准全文查询、案例检索。要求禁止编造法规名、条号与溯源链接，识别结果必须以当次 MCP 返回为准。
license: MIT
metadata:
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    product_lines:
      - 法条识别与溯源
    server_ids:
      - law-recognition
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：法条识别与溯源（law-recognition）

这个 Skill 只负责一件事：**从现有文本里识别潜在法规引用，并给出可继续核查的线索。**

识别结果本身不是最终正式引用。
如果需要条文原文，应继续转到精准法条 Skill；如果只是想找某个主题相关法规，应转到法规检索 Skill。

## 先看边界

- 识别出来的法规名、条号、线索，只能视为候选结果或核查起点。
- 对低置信、歧义命中、简称匹配、旧法名称映射等情况，必须标记人工复核。
- 不能把“识别到了某条法规”直接写成“该条法规当然适用”。

## 默认路由

- 输入是一段已有文本，里面可能包含法规引用：
  - 走 `law-recognition`
- 输入是“帮我找某主题法规”：
  - 转 `pkulaw-mcp-law-retrieval`
- 输入是“已知法规名 + 条号，要看原文”：
  - 转 `pkulaw-mcp-fatiao-precise`

## 推荐工作流

1. 确认输入是待识别文本，而不是纯检索问题。
2. 用 `tools` 确认真实 `<toolName>` 与参数名。
3. 提交待识别文本。
4. 输出识别到的法规名、条款信息与溯源线索。
5. 对低置信或歧义命中单列“需人工复核”。

## 失败与降级

### 允许的失败输出

```markdown
当前未拿到法条识别结果。

失败原因：
- [未认证 / 无订阅 / 无结果 / 工具不存在 / 命令报错]

建议动作：
- 检查 `pkulaw-mcp` 配置
- 检查输入文本是否包含明确法规表达
- 如需先找法规主题，请转到法规检索路径
```

### 允许的保守输出

- 低置信或歧义命中 -> 标记“需人工复核”
- 不得把候选线索写成已确认引用

## 输出结构

1. 识别结果
2. 溯源线索
3. 置信提示
4. 待人工复核项

## 终端复现与排障

如需在终端复现，请先安装 `@pkulaw/mcp-cli`；安装后命令为 `pkulaw-mcp`。

```bash
pkulaw-mcp tools law-recognition
pkulaw-mcp law-recognition <toolName> ... --json
```

## 补充材料

- 示例见 [examples.md](examples.md)
