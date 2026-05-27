---
name: pkulaw-mcp-regulatory-reply-check
description: >
  监管回复函与说明材料的依据核查工作流，用于把回复函、问询答复、说明材料中的法规引用整理成可复核、可回源、可流转的核查底稿。Use when：律师、法务、合规、董办或监管回复支持团队需要在对外或审批前检查引用是否准确、完整、可追溯。NOT for：纯法规主题研究、完整专项法律意见书撰写、以及不需要交付级引用把关的轻量场景。要求先锁定核查范围，再逐条回源与核验；未核验的引用不得写为确定依据。
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
      - pkulaw-mcp-doc-link
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：Regulatory Reply Check（监管/回复函依据核查）

这个 Skill 是**交付前引用把关层**。
它不负责重新研究整个法律问题，而是专门检查回复函、说明材料、问询答复里的法规引用是否足够稳、足够可追溯。

## 这个 Skill 真正要完成的动作

把回复材料中的引用整理成：

- 哪些引用与当次返回一致
- 哪些引用仍需复核
- 哪些表述需要修正
- 哪些关键条文已完成回源

## 主对象与辅助对象

### 主对象

- 回复函、说明材料、问询答复中的引用段落
- 影响核心结论的法规、规范性文件、监管规则

### 辅助对象

- 内部沟通纪要
- 历史版本草稿
- 业务部门提供的说明文字

内部口径和草稿只能帮助理解背景，不能替代当次核验依据。

## 缺信息先追问

以下信息缺失时，先补充：

- 文档类型：监管回复函、客户回复函、说明材料、审批说明
- 核查范围：全文、重点段落、脚注、引用清单
- 哪些结论或段落属于高风险重点核查部分
- 是否存在明确法域、行业或监管口径限制

若拿不到全文，至少要求提供重点结论段落或引用清单。

## 推荐工作流

1. 锁定范围：先确认只核哪些段落、哪些结论。
2. 识别引用：用 `law-recognition` 找出文中法规名、条号与潜在线索。
3. 关键条文回源：对影响核心结论的条文，用 `fatiao` 回源原文。
4. 一致性核验：用 `citation-validator` 检查引用表述与当次返回是否一致。
5. 形成底稿：按“与当次返回一致 / 待复核 / 需修正”整理核查表。
6. 链接增强：需要流转审核或沉淀时，用 `doc-link` 生成可追溯版本。

## 输出纪律

- 重点不是证明草稿正确，而是暴露风险引用。
- “与当次返回一致”不等于已完成实体法律审查。
- 简称不清、条号不稳、新旧法衔接不明时，优先标“待复核”。
- 对影响核心结论的条文，尽量至少完成一次回源。

## 质量门槛

- 每条“与当次返回一致”都必须有当次依据。
- 关键条文至少完成一次 `fatiao` 回源。
- 未命中或歧义项必须标“待复核”。
- 需要流转时，优先提供 `doc-link` 增强版本。

## 失败与降级

- `law-recognition` 命中不足：先按已有明确引用逐条核，不扩写成全面法规研究。
- `fatiao` 命中失败：保留法规名和条号线索，标记“待回源”。
- `citation-validator` 不可用：只能写“引用待核验”，不能写“引用准确”。

## 配套文件

- 核查底稿模板：[template.md](./template.md)
- 真实业务示例：[examples.md](./examples.md)

## 关联 Skill

- 法条识别：[pkulaw-mcp-law-recognition](../pkulaw-mcp-law-recognition/SKILL.md)
- 精准法条：[pkulaw-mcp-fatiao-precise](../pkulaw-mcp-fatiao-precise/SKILL.md)
- 引用核验：[pkulaw-mcp-citation-validator](../pkulaw-mcp-citation-validator/SKILL.md)
- 法宝超链：[pkulaw-mcp-doc-link](../pkulaw-mcp-doc-link/SKILL.md)
