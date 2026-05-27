---
name: pkulaw-mcp-batch-contract-screening
description: >
  批量合同合规初筛工作流，用于对同模板或同类型合同做快速统一筛查，输出可执行的批量风险台账。Use when：企业法务、采购合规、风控运营需要同时处理多份合同，识别高风险条款、引用错误与依据缺失。NOT for：单份合同的逐条精细审查、完整法律意见、诉讼策略分析。要求明确标注“批量初筛结果”，高风险项与系统未命中项必须人工复核。
license: MIT
metadata:
  pkulaw:
    workflow_type: composed
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    composed_skills:
      - pkulaw-mcp-law-recognition
      - pkulaw-mcp-citation-validator
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：Batch Contract Screening（批量合同初筛）

这个 Skill 只处理**同模板或同类型合同的批量筛查**。
如果用户要深挖某一份合同的具体条款，应转到 `pkulaw-mcp-contract-review-lite`，不要在批量模式里假装做精细逐条意见。

## 一句话流程

按合同批次逐份执行：`law-recognition` 识别引用 -> `citation-validator` 核验准确性 -> 聚类形成批量风险台账。

## 推荐工作流

1. 按合同类型分批（采购、销售、服务、数据等）。
2. 只抽取每份合同的关键模块，而不是对全部文本逐字深挖。
3. 对关键条款调用 `law-recognition` 提取法规引用。
4. 用 `citation-validator` 核验引用正确性与一致性。
5. 按条款类型聚类（违约责任、解除、保密、争议解决等）。
6. 输出批量风险台账与整改优先级。

## 风险分级建议

- 红色：引用错误或关键条款无法建立依据。
- 黄色：引用不完整、歧义较高、适用条件不明确。
- 绿色：引用基本准确，但仍建议保留复核意见。

## 输出纪律

- 输出重点是“批量规律”和“整改优先级”，不是单份长篇审查报告。
- 不得把少量抽样结论直接外推成全部合同都无风险。
- 对系统未命中项，只能写“待人工复核”或“系统未命中”，不能推断为“无风险”。

## 质量门槛

- 红色项必须附核验依据与整改建议。
- 无法核验项必须标注“待人工复核”。
- 不得将初筛结果表述为最终法律意见。

## 失败与降级

- 工具返回不稳定或空结果：记录为“系统未命中”，不推断为“无风险”。
- 批量过大：先按合同类型或批次分段处理，避免一次性结论失真。
- 若某一份合同需单独深挖：切换到 `pkulaw-mcp-contract-review-lite`。

## 关联 Skill

- 法条识别：[pkulaw-mcp-law-recognition](../pkulaw-mcp-law-recognition/SKILL.md)
- 引用核验：[pkulaw-mcp-citation-validator](../pkulaw-mcp-citation-validator/SKILL.md)
- 单份合同初筛：[pkulaw-mcp-contract-review-lite](../pkulaw-mcp-contract-review-lite/SKILL.md)

## 配套文件

- 输出模板：[template.md](./template.md)
- 真实业务示例：[examples.md](./examples.md)
