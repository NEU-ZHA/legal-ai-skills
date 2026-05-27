---
name: pkulaw-mcp-opinion-citation-check
description: >
  法律意见书、法律备忘与合规结论出具前的引用核验工作流，用于把草稿中的法规引用整理成一份可签发前复核的核验底稿，覆盖一致性核验与关键条文回源。Use when：律师或法务在正式出具意见、备忘或合规结论前，需要检查法条引用是否准确、完整、可追溯。NOT for：仅做法规主题检索、案例研究，或不需要交付级引用核验的轻量场景。要求所有核验结论必须来自当次 MCP 返回；未通过核验的引用不得写为确定依据。
license: MIT
metadata:
  pkulaw:
    workflow_type: composed
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    composed_skills:
      - pkulaw-mcp-citation-validator
      - pkulaw-mcp-fatiao-precise
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：Opinion Citation Check（法律意见书出具前核验）

这个 Skill 是**正式交付前的引用质检层**。
它只负责把草稿中的法条引用核对干净、标出风险，不替代承办律师的实体判断和签发责任。

## 使用边界

- 本 Skill 产出为引用核对与技术一致性辅助，不构成已签署的法律意见书、律师法律意见或对外法律责任判断。
- “通过”仅表示当次 MCP 返回与法宝数据结果一致，不替代事务所内部质量控制与承办律师最终签发。
- 对外正式依据与文书效力，仅以承办律师审阅、签章及事务所流程为准。

## 这个 Skill 真正要完成的动作

把草稿中的引用整理成：

- 哪些与当次返回一致
- 哪些仍需复核
- 哪些需要修正
- 哪些关键条文已完成回源确认

## 缺信息先追问

以下信息缺失时，先补充：

- 文档类型：法律意见书、备忘、合规结论、回复函
- 哪些段落或结论属于重点核验范围
- 是否有必须优先核的关键条文
- 交付用途：内部底稿、签发前复核、客户前置审查

若无法拿到全文，至少要求提供引用密集段落或引用清单。

## 推荐工作流

1. 收集材料：拿到草稿全文、引用段落或引用清单。
2. 锁定重点：先标出会影响结论的核心条文和高风险表述。
3. 核验一致性：调用 `citation-validator`，输出“通过 / 待复核 / 需修正”三类结果。
4. 关键条文回源：对关键或争议条款调用 `fatiao` 回源条文原文。
5. 形成底稿：生成核验表，列明“与当次返回一致（仍须签发前复核）”与“须修正后再引用”的条目。

## 输出纪律

- 重点不是证明草稿正确，而是把风险暴露出来。
- “通过”只表示与当次返回一致，不得等同于“已完成法律审查”。
- 对影响结论的条文，尽量至少完成一次 `fatiao` 回源。
- 如果引用本身模糊、简称不清、条号不稳，优先标“待复核”。

## 质量门槛

- 每条“通过”必须有当次工具返回依据。
- 关键条款至少完成一次 `fatiao` 回源确认。
- 不得使用“可能正确”替代核验结论。

## 失败与降级

- `citation-validator` 不可用：明确标注“引用未核验”，禁止出具确定性意见。
- `fatiao` 命中失败：提示核对法规名称、别名与条号格式后重试。

## 配套文件

- 核验底稿模板：[template.md](./template.md)
- 真实业务示例：[examples.md](./examples.md)

## 关联 Skill

- 引用核验：[pkulaw-mcp-citation-validator](../pkulaw-mcp-citation-validator/SKILL.md)
- 精准法条：[pkulaw-mcp-fatiao-precise](../pkulaw-mcp-fatiao-precise/SKILL.md)
