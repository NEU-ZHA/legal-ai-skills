---
name: pkulaw-mcp-grounded-answer
description: >
  通用法律答复草稿工作流，用于把已检索到的法规、案例和引用核验结果整理成可复核、可转发、可继续修改的答复文本。Use when：律师、法务、合规或法律运营需要回复客户、业务、领导或内部群，且问题不明显属于某个已单独建模的垂直场景。NOT for：纯资料探索、仅需检索列表、不需要形成答复草稿的任务；以及已有更合适垂直 Skill（如劳动用工回复）时。要求先补齐关键事实，再检索后结论；未核验的具体法条不得写成确定依据。
license: MIT
metadata:
  pkulaw:
    workflow_type: composed
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    composed_skills:
      - pkulaw-mcp-law-retrieval
      - pkulaw-mcp-case-retrieval
      - pkulaw-mcp-citation-validator
      - pkulaw-mcp-doc-link
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：Grounded Answer（通用法律答复）

这个 Skill 是**通用交付层**，适合把法律问题整理成一份可复核、可继续修改、可用于沟通的答复草稿。

如果问题已经明显属于某个垂直场景，例如劳动用工、公司治理研究备忘、合同批量筛查，应优先转到更窄的组合 Skill，而不是继续停留在这里。

## 这个 Skill 真正要完成的动作

当用户说“帮我回复客户”“给我一个法律口径”“整理成可发给业务的答复”时，不要停在检索列表，而要产出：

- 简短结论
- 主要依据
- 风险提示
- 待复核点
- 可追溯版本（如需要）

## 先看边界

- 这是通用法律答复 Skill，不是垂直行业或专业场景的专用答复 Skill。
- 目标是形成“初步答复草稿”，不是正式法律意见书。
- 若已有垂直 Skill 更合适，应优先转交，而不是在这里泛化处理。

## 缺信息先追问

以下信息缺失时，先补 1-2 个最关键问题，不要直接写结论：

- 适用法域或地域
- 关键事实前提
- 时间点或版本要求
- 交付对象：内部讨论、客户回复、审批说明、对外发函
- 是否需要类案支撑

如果用户一时无法补齐，也只能按“有限事实前提下的初步答复草稿”输出。

## 推荐工作流

1. 界定任务：确认用户要的是答复草稿，而不是检索列表。
2. 补足前提：先补法域、时点、关键事实、交付对象。
3. 检索取数：规则问题优先用法规检索；需要裁判倾向时再补案例检索。
4. 草稿成形：先写“结论 + 依据 + 前提 + 风险提示”。
5. 引用核验：出现具体法条、司法解释或精确引用时，走 `citation-validator`。
6. 链接增强：需要转发、审批或沉淀时，用 `doc-link` 做增强。
7. 标注边界：把“已核验 / 待复核 / 仍缺事实”分开写。

## 输出纪律

- 只在已检索依据覆盖的范围内表达结论。
- 不写“明确合法”“一定胜诉”“可以直接执行”等绝对化措辞。
- 事实不足处要单列，不与结论混写。
- 面向客户、领导或审批流时，优先输出“短结论 + 依据列表 + 待复核点”。

## 质量门槛

- 没有无来源法条、案号或裁判要点。
- 每个关键结论至少能回到一条当次检索依据。
- 重要引用经过 `citation-validator`，或明确标注未核验。
- 需要流转时，优先提供 `doc-link` 增强版本。

## 失败与降级

- `citation-validator` 不可用：只能标注“引用未核验”，不能写“已确认”。
- `doc-link` 不可用：先交付纯文本并声明“链接待补”。
- 检索为空：返回“未检索到足够依据”，并给出下一步检索建议。
- 事实前提不足：输出“基于当前已知事实的初步答复草稿”，并列出仍需补充的信息。

## 配套文件

- 输出模板：[template.md](./template.md)
- 真实业务示例：[examples.md](./examples.md)

## 关联 Skill

- 法规检索：[pkulaw-mcp-law-retrieval](../pkulaw-mcp-law-retrieval/SKILL.md)
- 案例检索：[pkulaw-mcp-case-retrieval](../pkulaw-mcp-case-retrieval/SKILL.md)
- 引用核验：[pkulaw-mcp-citation-validator](../pkulaw-mcp-citation-validator/SKILL.md)
- 法宝超链：[pkulaw-mcp-doc-link](../pkulaw-mcp-doc-link/SKILL.md)
