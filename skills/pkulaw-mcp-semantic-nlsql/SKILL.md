---
name: pkulaw-mcp-semantic-nlsql
description: >
  使用约 125 积分的 `semantic-nlsql` 做跨库语义检索。Use when：复杂问题无法可靠拆成法规和案例关键词路径，或约 25 积分的定向检索后仍有关键缺口。NOT for：普通综合研究的默认首轮、单一法规/案例或已知法条查询。必须确认工具可用，不得伪造结果。
license: MIT
metadata:
  version: "1.2.0"
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    product_lines:
      - 法宝语义检索（NL-SQL）
    server_ids:
      - semantic-nlsql
    mcp_cli: "@pkulaw/mcp-cli"
---

# 北大法宝 MCP：语义检索（semantic-nlsql）

这个 Skill 只负责一件事：**用一次自然语言检索，先把跨库候选材料召回出来。**

它适合做经济型检索后的升级路径，不替代法规检索、案例检索、精准法条回源或引用核验。默认先尝试拆分问题，分别调用 `law-keyword` 和 `case-keyword`；只有无法可靠拆分或仍有关键缺口时才使用本 Skill。

## 使用前必须检查

1. 已配置 `serverPaths.semantic-nlsql`
2. `pkulaw-mcp tools semantic-nlsql` 能正常返回
3. 控制台已开启对应服务、Token 可用

如果上面任何一点不成立，必须停止继续使用本 Skill，并提示用户先配置或改走其他 Skill。

## 先看边界

- 本 Skill 的长处是综合召回，不是最终结论生成器。
- 召回结果必须继续做分流、核验、收窄，不得直接包装成确定法律意见。
- 如果问题本来就只是查法规或只是查案例，优先用更窄的 Skill，而不是为了“高级”强行走 NL-SQL。

## 默认路由

符合下面条件时才用 `semantic-nlsql`：

- 问题同时跨法规、案例、法条或多类材料，而且无法可靠拆成定向关键词路径
- 已用 `law-keyword` / `case-keyword` 做过有理由的检索，仍有影响结论的关键缺口

不符合时，直接改走：

- 法规问题 -> [pkulaw-mcp-law-retrieval](../pkulaw-mcp-law-retrieval/SKILL.md)
- 案例问题 -> [pkulaw-mcp-case-retrieval](../pkulaw-mcp-case-retrieval/SKILL.md)

## 推荐工作流

1. 先确认经济型定向检索不足，并写明尚缺什么。
2. 确认配置与工具可用。
3. 用自然语言完整表达问题，完成一次综合检索。
4. 按返回内容分成法规、案例、法条或其他候选。
5. 明确告诉用户：这是“综合召回结果”，不是最终定论。
6. 必要时把候选继续转交给更窄的 Skill 做二次检索。

## 失败与降级

### 配置缺失

只允许输出类似下面的结构：

```markdown
当前无法使用 `semantic-nlsql`，因为实例路径尚未完成配置。

建议动作：
- 先配置 `serverPaths.semantic-nlsql`
- 执行 `pkulaw-mcp tools semantic-nlsql` 验证
- 如暂不配置，可改用法规语义检索与案例语义检索分别完成
```

### 401/403 或无结果

```markdown
当前未拿到 semantic-nlsql 的有效检索结果。

失败原因：
- [未认证 / 无订阅 / 无结果 / 命令报错]

建议动作：
- 检查 Token 与订阅状态
- 调整自然语言问题表述
- 改走法规或案例的窄路径检索
```

## 终端复现与排障

如需在终端复现，请先安装 `@pkulaw/mcp-cli`；安装后命令为 `pkulaw-mcp`。

```bash
pkulaw-mcp tools semantic-nlsql
pkulaw-mcp semantic-nlsql <toolName> --json
```

说明：

- `<toolName>` 必须以 `tools` 输出为准
- 不要在文档中写死 `ai_pkulaw_search` 等工具名

## 输出结构

按下面结构输出最稳：

1. 问题重述
2. 前置检查结果
3. 综合召回摘要
4. 建议的下一步分流
5. 局限说明

## 补充材料

- 示例见 [examples.md](examples.md)
- 法规检索见 [pkulaw-mcp-law-retrieval](../pkulaw-mcp-law-retrieval/SKILL.md)
- 案例检索见 [pkulaw-mcp-case-retrieval](../pkulaw-mcp-case-retrieval/SKILL.md)
