---
name: pkulaw-mcp-legal-research
description: >
  北大法宝原生 MCP 的总路由法律研究 Skill。当前本机已配置三个 MCP：`law-keyword`（检索法律法规-关键词）、`fatiao`（精准查找法条-关键词）和 `case-keyword`（检索司法案例-关键词）；不得假定案号识别、引用核验、超链、语义检索等旧 MCP 可用。Use when：用户只说“帮我查法律依据/案例”，但尚未明确该走法规关键词、精准法条还是案例关键词；或你需要在原生 MCP 能力之间分流。NOT for：网页端登录、网页详情页点击、复制详情页 URL、机构/IP 登录核验；这些应转用户自建的 `pkulaw-legal-search` 网页/Computer Use 流程。须已配置并订阅北大法宝 MCP；禁止无检索依据编造法条、案号、裁判要点或引用结论。
license: MIT
metadata:
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    mcp_cli: "@pkulaw/mcp-cli"
    command: "pkulaw-mcp"
    config: "~/.pkulaw/mcp/config.json"
    servers_config: "工程维护时可对照 pkulaw-mcp-cli 仓库 src/config/servers.json"
version: "1.1.0"
---

# 北大法宝 MCP：有据法律研究（总路由）

这个 Skill 不负责把所有事情都做完，它主要负责一件事：**先把用户问题正确分流到合适的法宝原生 MCP 能力或更窄的 Skill。**

它和 `pkulaw-legal-search` 不重复：本 Skill 管原生 MCP 路由；`pkulaw-legal-search` 管网页/Computer Use 兜底、详情页核验和登录态操作。

如果用户已经明确是“只查法规”或“只查案例”，不要继续停留在总路由层，直接转到更窄的 Skill：

- 法规检索 -> [pkulaw-mcp-law-retrieval](../pkulaw-mcp-law-retrieval/SKILL.md)
- 案例检索 -> [pkulaw-mcp-case-retrieval](../pkulaw-mcp-case-retrieval/SKILL.md)

## 先看边界

- 这是总路由 Skill，不是最终交付 Skill。
- 默认任务是“判断走哪条能力链”，不是“自己把所有能力都跑一遍”。
- 如果某个窄 Skill 已经足够，就应立即转交，不要在这里继续泛化处理。
- 如果 MCP 不通、当前会话没加载对应工具、返回 401/403/超时/无结果、结果不足、需要详情页链接或需要网页登录态，不要在这里硬撑，立即转 `pkulaw-legal-search` 的网页/Computer Use 流程。

## 必须遵守的规则

1. 未成功拿到法宝 MCP 返回前，不得写出具体法规名称、条号、案号、法院名称或裁判要点。
2. 工具名 `<toolName>` 必须以 `pkulaw-mcp tools` 或 MCP `tools/list` 为准，不得在正文中写死。
3. 出现 `401/403`、无结果、工具不存在或配置缺失时，只能说明失败原因与建议动作。
4. 当前只允许把 MCP 路由到 `law-keyword`、`fatiao` 或 `case-keyword`；其他法宝能力只能转网页端或说明未订阅。
5. 这是研究辅助与能力路由，不构成正式法律意见。
6. MCP 路由失败时，默认后备不是空答，而是转 `pkulaw-legal-search` 用网页/Computer Use 继续查。

## 总路由表

| 用户真正要做的事 | 推荐走向 |
|------------------|----------|
| 只查法规依据 | `pkulaw-mcp-law-retrieval` |
| 只查类案样本 | `pkulaw-mcp-case-retrieval` |
| 已知法规名 + 条号取全文 | 优先走 `fatiao` 精准法条；若当前会话未暴露该 MCP，再用 `law-keyword` 找法规线索并转网页详情页核条文 |
| 已知案号找案例 | 先把案号作为关键词走 `case-keyword`，再转网页详情页核对 |
| 核验已有问答或文稿里的法条引用 | 当前无引用核验 MCP；用 `law-keyword` 找线索后人工/网页核验 |
| 给文稿中的法规表述补法宝链接 | 当前无超链 MCP；转网页端取得详情页 URL |
| 问题同时跨法规、案例等多类材料 | 分别跑 `law-keyword`、必要时 `fatiao`、以及 `case-keyword`，不要调用语义综合检索 |

## 默认分流步骤

1. 先判断用户是要“找法规”还是“找案例”；若两者都要，就拆成两次关键词检索。
2. 如果已经足够明确，立即转交到法规或案例窄 Skill。
3. 如果用户要精准条文，优先走 `fatiao`；如果用户要案号识别、引用核验、自动加链接或语义综合检索，先说明当前 MCP 未订阅该能力，再选择网页端补查。
4. 拿到返回后，只做基于结果的下一步建议，不在总路由层强行扩写长答案。

## 允许的失败输出

```markdown
当前未拿到法宝 MCP 的有效检索结果。

失败原因：
- [未认证 / 无订阅 / 无结果 / 配置缺失 / 工具不存在 / 命令报错]

建议动作：
- 检查 `pkulaw-mcp` 配置与 Token
- 检查对应服务是否已订阅
- 把任务改写成更明确的法规检索、案例检索或精准查询问题
```

## 终端复现与排障

如需在终端复现，请先安装 `@pkulaw/mcp-cli`；安装后命令为 `pkulaw-mcp`。

```bash
pkulaw-mcp tools
pkulaw-mcp tools law-keyword
pkulaw-mcp tools case-keyword
pkulaw-mcp <serverId> <toolName> ... --json
pkulaw-mcp check
pkulaw-mcp docs
```

## 输出结构

总路由层最稳的输出结构是：

1. 任务类型判断
2. 推荐走向
3. 当前是否已完成检索
4. 下一步建议

## 补充材料

- 法规检索：[pkulaw-mcp-law-retrieval](../pkulaw-mcp-law-retrieval/SKILL.md)
- 案例检索：[pkulaw-mcp-case-retrieval](../pkulaw-mcp-case-retrieval/SKILL.md)
- npm CLI 包 `@pkulaw/mcp-cli`：<https://gitee.com/pkulaw/pkulaw-mcp-cli> · [npm](https://www.npmjs.com/package/@pkulaw/mcp-cli)
