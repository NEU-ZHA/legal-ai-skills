---
name: pkulaw-mcp-labor-employment-answer
description: >
  劳动用工回复草稿工作流，用于把劳动法律与用工管理问题整理成可复核、可追溯、可转发的简短答复文本。Use when：律师、法务、HRBP 或合规同学需要回复业务、管理层或客户的劳动用工问题，并希望输出“结论 + 依据 + 风险提示 + 待复核点”。NOT for：完整劳动专项尽调、仲裁诉讼全案策略设计、以及其他更适合通用法律答复或非劳动领域处理的问题。要求先补事实前提，再检索后结论；未核验的具体法条不得写成确定依据。
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

# 北大法宝 MCP：Labor Employment Answer（劳动用工回复草稿）

这个 Skill 是**劳动用工垂直交付层**。
如果问题明显是招聘、试用期、调岗、绩效、解除、竞业限制、工时休假、社保等劳动用工问题，优先使用本 Skill，而不是回到通用 `pkulaw-mcp-grounded-answer`。

## 这个 Skill 真正要完成的动作

把劳动用工问题压缩成一份可直接发给业务、管理层、HR 或客户初看的答复草稿，通常包括：

- 当前适用前提
- 简短结论
- 主要依据
- 风险提示
- 待复核点

## 主对象与辅助对象

### 主对象

- 用户提出的劳动用工问题
- 当前已知事实前提
- 当次检索到的法规、司法解释、典型类案

### 辅助对象

- 业务同事拟好的回复草稿
- 客户过往沟通口径
- 内部制度摘要

辅助对象只用于理解场景，不当然等于外部法律依据。

## 缺信息先追问

以下信息缺失时，先补 1-2 个最关键问题：

- 用工地区
- 问题类型：招聘、试用期、调岗、绩效、解除、竞业限制、加班、社保等
- 关键事实前提：是否有书面制度、是否已通知、是否有证据留痕
- 交付对象：内部业务、管理层、客户、HR
- 是否需要类案支撑

如用户暂时无法补齐，只能按“有限事实前提下的初步答复草稿”输出。

## 推荐工作流

1. 界定问题：确认这是劳动用工答复草稿，而不是诉讼策略分析。
2. 补足前提：先问地区、事实、制度基础、交付对象。
3. 规则检索：优先检索劳动合同法、工时休假、社保、竞业限制等规则依据。
4. 类案补充：需要裁判倾向或风险对比时，再补案例检索。
5. 草稿成形：先写“结论 + 前提 + 依据 + 风险提示”。
6. 引用核验：出现具体法条或司法解释时，用 `citation-validator` 核验。
7. 链接增强：需要转发时，再用 `doc-link` 做增强。

## 输出纪律

- 不写“公司一定可以解除”“员工一定胜诉”等绝对化措辞。
- 事实前提不足时，把“仍需补充的信息”单列出来。
- 若地区差异、裁判分歧明显，要单独提醒。
- 面向业务或 HR 时，优先输出“简要结论 + 主要依据 + 风险提示 + 待复核点”。

## 质量门槛

- 每个关键结论至少对应一条当次检索依据。
- 重要引用经过 `citation-validator`，或明确写明未核验。
- 事实不足处已单列，不与结论混写。
- 需要转发时，优先提供 `doc-link` 增强版本。

## 失败与降级

- 检索为空：明确写“未检索到足够依据”，并提示换关键词、补地区或补事实。
- `citation-validator` 不可用：只能标注“引用未核验”，不得写“已确认”。
- 类案不足：只能写“当前样本有限，不能据此概括稳定裁判倾向”。
- 若问题明显已超出劳动用工回复范围，应提示转入更深层专项分析，而不是硬写。

## 配套文件

- 输出模板：[template.md](./template.md)
- 真实业务示例：[examples.md](./examples.md)

## 关联 Skill

- 法规检索：[pkulaw-mcp-law-retrieval](../pkulaw-mcp-law-retrieval/SKILL.md)
- 案例检索：[pkulaw-mcp-case-retrieval](../pkulaw-mcp-case-retrieval/SKILL.md)
- 引用核验：[pkulaw-mcp-citation-validator](../pkulaw-mcp-citation-validator/SKILL.md)
- 法宝超链：[pkulaw-mcp-doc-link](../pkulaw-mcp-doc-link/SKILL.md)
