---
name: pkulaw-mcp-doc-link
description: >
  法宝超链增强，用于把法律文书、答复、备忘或研究材料中的法规、案例引用转成可追溯链接。Use when：用户已经有现成文本，希望增强可点击、可追溯的交付版本。NOT for：检索新法规、检索新案例、法条精确查询、法条引用核验。要求链接与引用实体必须来自当次工具返回，不得手工拼接伪链接。
license: MIT
metadata:
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    product_lines:
      - 法宝超链
    server_ids:
      - doc-link
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：法宝超链（doc-link）

这个 Skill 只负责一件事：**把现有内容中的法律引用链接化。**

它提升的是可追溯性和阅读体验，不等于自动完成真实性判断。
如果引用本身是否准确还没核验，应先考虑 `citation-validator` 或人工复核。

## 先看边界

- 生成了链接，不表示引用语义上一定准确。
- 未命中链接时，不得手工拼接近似链接冒充结果。
- 如果用户还没有现成文本，而只是想“先找法规/案例”，应先走检索 Skill。

## 默认路由

- 用户要“给内容加法宝链接”：
  - 走 `doc-link`
- 用户要“先找法规/案例再输出”：
  - 先用检索 Skill，再按需接入本 Skill

## 推荐工作流

1. 确认输入是已有正文，而不是检索需求。
2. 用 `tools` 确认真实 `<toolName>` 与参数名。
3. 提交待处理文本。
4. 输出增强后的链接化内容。
5. 单列链接命中摘要与未命中项。

## 失败与降级

### 允许的失败输出

```markdown
当前未拿到法宝超链增强结果。

失败原因：
- [未认证 / 无订阅 / 无结果 / 工具不存在 / 命令报错]

建议动作：
- 检查 `pkulaw-mcp` 配置
- 检查文本中的法规或案例引用是否足够标准
- 如需先找依据，请先走检索路径
```

### 允许的保守输出

- 只交付原始纯文本并声明“链接待补”
- 对未命中引用给出“可改写建议”，但不手工伪造链接

## 输出结构

1. 增强后正文
2. 链接命中摘要
3. 未命中项
4. 改写建议（如有）

## 终端复现与排障

如需在终端复现，请先安装 `@pkulaw/mcp-cli`；安装后命令为 `pkulaw-mcp`。

```bash
pkulaw-mcp tools doc-link
pkulaw-mcp doc-link <toolName> ... --json
```

## 补充材料

- 示例见 [examples.md](examples.md)
