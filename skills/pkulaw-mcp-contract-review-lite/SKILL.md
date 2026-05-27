---
name: pkulaw-mcp-contract-review-lite
description: >
  单份合同条款合规初筛工作流，用于把一份合同快速整理成可执行的风险台账，覆盖法条识别、条文回源和引用核验。Use when：律师或法务需要对单份合同做首轮审查、审批前风险识别或模板迭代前初筛。NOT for：批量合同统一筛查、完整法律尽调、正式法律意见书、诉讼策略建议。要求明确标注“初筛结果”，高风险与不确定项必须人工复核。
license: MIT
metadata:
  pkulaw:
    workflow_type: composed
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    composed_skills:
      - pkulaw-mcp-law-recognition
      - pkulaw-mcp-fatiao-precise
      - pkulaw-mcp-citation-validator
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：Contract Review Lite（单份合同初筛）

这个 Skill 只处理**单份合同**。
如果用户要同时筛很多份同模板或同类型合同，请转到 `pkulaw-mcp-batch-contract-screening`，不要在这里硬做批量处理。

## 这个 Skill 真正要完成的动作

把单份合同压缩成：

- 风险分级
- 条款位置
- 对应依据
- 建议动作
- 待人工复核项

## 缺信息先追问

以下信息缺失时，先补充，不要直接打标签：

- 合同类型（采购、销售、服务、技术、数据、劳动等）
- 审查目的（签约前、模板迭代、审批前、存量排查）
- 审查重点（付款、违约、解除、保密、知识产权、争议解决等）
- 是否有明确适用地域或行业监管要求

如用户只给全文、不说明重点，可先按付款、违约、解除、争议解决、引用依据等高频模块初筛。

## 推荐工作流

1. 条款分段：按章节或条款号拆分输入文本。
2. 锁定重点：优先检查付款、违约、解除、保密、争议解决、法律依据引用。
3. 法条识别：对重点条款调用 `law-recognition`，提取法规名与条款线索。
4. 精准回源：对已识别条款用 `fatiao` 查原文。
5. 一致性核验：用 `citation-validator` 检查合同表述与检索/回源结果是否一致。
6. 形成台账：按高、中、低风险输出问题、依据、建议动作、复核要求。

## 风险分级规则

- 高风险：引用法条错误、关键义务条款与法条冲突。
- 中风险：引用不完整、表述歧义、缺少适用条件。
- 低风险：表达基本规范，但建议补充解释或证据链。

## 输出纪律

- “高风险”只用于已有明确依据支持的问题。
- “低风险”不等于“可以直接签”，仍需结合交易背景复核。
- 没命中依据或存在歧义时，标为“待人工复核”，不要硬分级。
- 输出时优先使用“问题 + 依据 + 建议动作”的台账结构。

## 质量门槛

- 每个高风险项必须有可追溯依据。
- 未命中或歧义项必须标注“待人工复核”。
- 禁止输出超出检索证据范围的确定性判断。

## 失败与降级

- 合同太长：先按重点模块拆分，不要一次给出全篇确定性结论。
- `fatiao` 命中失败：先保留法规名和条号线索，标记“待回源”。
- `citation-validator` 不可用：只能写“引用待核验”，不能写“条款引用准确”。

## 配套文件

- 风险台账模板：[template.md](./template.md)
- 真实业务示例：[examples.md](./examples.md)

## 关联 Skill

- 法条识别：[pkulaw-mcp-law-recognition](../pkulaw-mcp-law-recognition/SKILL.md)
- 精准法条：[pkulaw-mcp-fatiao-precise](../pkulaw-mcp-fatiao-precise/SKILL.md)
- 引用核验：[pkulaw-mcp-citation-validator](../pkulaw-mcp-citation-validator/SKILL.md)
