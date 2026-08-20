---
name: pkulaw-mcp-legal-research
description: >
  北大法宝 10 项原生 MCP 的成本感知总路由。Use when：用户要查法规、法条、案例、核验引用、识别法条/案号、补法宝链接或做跨库法律研究。统一积分模式下优先调用约 25 积分的关键词/精准检索，只有结果不足或任务明确需要专门能力时才调用约 125 积分服务；禁止无检索依据编造法条、案号、裁判要点或引用结论。
license: MIT
metadata:
  version: "1.2.0"
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    mcp_cli: "@pkulaw/mcp-cli"
    command: "pkulaw-mcp"
    config: "~/.pkulaw/mcp/config.json"
    servers_config: "工程维护时可对照 pkulaw-mcp-cli 仓库 src/config/servers.json"
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
4. 每次先选择完成任务所需的最少服务；禁止为了“全面”而并发或顺序调用全部 10 项。
5. 这是研究辅助与能力路由，不构成正式法律意见。
6. MCP 路由失败时，默认后备不是空答，而是转 `pkulaw-legal-search` 用网页/Computer Use 继续查。
7. 控制台显示的积分是约数，调用前应以用户当时的控制台为准；本 Skill 的关键约束是相对成本顺序。

## 10 项服务分层

| 层级 | serverId | 任务 | 约积分/次 |
|------|----------|------|-----------|
| 经济型 | `fatiao` | 已知法规名和条号，精准取法条 | 25 |
| 经济型 | `law-keyword` | 按标题词/正文词检索法规 | 25 |
| 经济型 | `case-keyword` | 按案由词/争点词检索案例 | 25 |
| 升级型 | `law-semantic` | 自然语言法规语义检索 | 125 |
| 升级型 | `case-semantic` | 案情相似性案例语义检索 | 125 |
| 专门型 | `law-recognition` | 从非结构化文本识别并溯源法条 | 125 |
| 专门型 | `citation-validator` | 核验和纠正法条引用 | 125 |
| 专门型 | `doc-link` | 给已核验依据补法宝链接 | 125 |
| 专门型 | `case-number` | 从文本识别案号并溯源 | 125 |
| 综合型 | `semantic-nlsql` | 无法可靠拆分的跨库综合检索 | 125 |

## 成本感知总路由

| 用户真正要做的事 | 首次调用 | 何时升级 |
|------------------|----------|----------|
| 只查法规依据 | 转 `pkulaw-mcp-law-retrieval`，先 `law-keyword` | 两轮有理由的关键词仍漏掉相关规范时，用一次 `law-semantic` |
| 已知法规名 + 条号取全文 | `fatiao` | 不自动升级；先核对法规名和条号 |
| 只查类案样本 | 转 `pkulaw-mcp-case-retrieval`，先 `case-keyword` | 两轮关键词仍找不到事实相似样本时，用一次 `case-semantic` |
| 已知完整案号找案例 | 先将完整案号交给 `case-keyword` | 没有精确匹配或要从长文本批量识别时，用 `case-number` |
| 核验文稿里的法条引用 | 引用已结构化时直接 `citation-validator` | 不额外调用其他 125 积分服务，除非需要先从长文本抽取引用 |
| 从长文本提取法条 | `law-recognition` | 提取后只有用户要求核验时，才继续 `citation-validator` |
| 给已核验引用补链接 | `doc-link` | 不用它做法规发现或引用核验 |
| 同时研究法规和案例 | 分别用 `law-keyword` + `case-keyword`，预计 50 积分 | 任务无法可靠拆分或仍有关键缺口时，才用一次 `semantic-nlsql` |

## 默认分流步骤

1. 先识别任务意图，只选择一条首选路径。
2. 明确法规词、法条、案由或完整案号时，优先 25 积分服务。
3. 首次关键词无结果时，先换一次有理由的关键词；第二次仍不足，才考虑相应语义服务。
4. 任务本身就是引用核验、法条识别、案号识别或补链接时，可直接使用对应专门服务，但不要附带调用其他服务。
5. 拿到返回后，只根据实际结果决定是否升级；每次升级都要能说明尚缺什么。

需要确定性路由时运行：

```bash
python3 scripts/recommend_route.py --intent law-topic
python3 scripts/recommend_route.py --intent article
python3 scripts/recommend_route.py --intent case-topic
python3 scripts/recommend_route.py --intent citation-check
```

可选意图还包括 `exact-case-number`、`law-recognition`、`add-links`、`cross-domain`。

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
