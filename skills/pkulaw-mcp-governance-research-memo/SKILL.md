---
name: pkulaw-mcp-governance-research-memo
description: >
  公司治理研究备忘工作流，用于把股权、决议、董事责任、控制权、关联交易等问题整理成可讨论、可继续深挖、可流转的研究备忘。Use when：律师、法务、董办、投融资或研究同学面对的问题跨规则与实践、需要先综合召回再分流研究。NOT for：单条法条原文查询、单案深度诉讼策略、以及只需单一路径检索的简单问题。要求先界定研究问题与范围，再综合召回与分流；未核验的具体法条不得写成确定依据。
license: MIT
metadata:
  pkulaw:
    workflow_type: composed
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    composed_skills:
      - pkulaw-mcp-semantic-nlsql
      - pkulaw-mcp-law-retrieval
      - pkulaw-mcp-case-retrieval
      - pkulaw-mcp-citation-validator
      - pkulaw-mcp-doc-link
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：Governance Research Memo（公司治理研究备忘）

这个 Skill 是**研究备忘层**，适合处理股权、决议、控制权、董监高责任、关联交易等跨规则与实践的问题。

它的特点不是“直接回答”，而是**先综合召回，再把法规线与案例线拆开写成研究备忘**。

## 这个 Skill 真正要完成的动作

把公司治理问题压缩成：

- 研究问题与范围
- 主要规则线索
- 主要案例线索
- 初步倾向与反向风险
- 待进一步研究的问题

## 主对象与辅助对象

### 主对象

- 公司治理问题本身：股权转让、股东会/董事会决议、公司控制权、董监高责任、关联交易等
- 当次综合召回到的法规、案例、法条、研究资料

### 辅助对象

- 客户背景材料
- 历史备忘
- 内部讨论纪要

辅助对象只用于帮助限定研究范围，不替代当次检索依据。

## 缺信息先追问

以下信息缺失时，先补充：

- 研究问题一句话定义
- 公司类型或交易场景
- 是否限定法域、地区、时间范围
- 更关注规则依据、裁判实践还是综合研究
- 最终用途：内部研讨、客户沟通、项目论证、进一步写正式意见

若问题本身很宽，先把研究问题缩成 1-2 个明确子问题。

## 推荐工作流

1. 界定问题：把宽泛问题缩成可检索的研究问题。
2. 综合召回：优先用 `semantic-nlsql` 做第一轮候选召回。
3. 分流补检：法规线索再做法规检索，案例线索再做案例检索。
4. 形成备忘：规则、案例、初步倾向、反向风险、待研究问题分开写。
5. 核验引用：明确法条或司法解释时，用 `citation-validator` 核验。
6. 链接增强：需要流转或沉淀时，用 `doc-link` 做增强。

## 输出纪律

- 不把综合召回结果直接写成最终法律结论。
- 不把有限样本概括成“公司治理的一般规则”或“司法一贯观点”。
- 对研究范围、样本局限、资料混杂要单独提示。
- 若问题仍过宽，要把“下一步研究问题”单列出来。

## 质量门槛

- 每条主要结论都能回到当次检索依据。
- 规则与案例线索分开写，避免混同。
- 重要法条引用经过 `citation-validator` 或明确标注未核验。
- 综合召回结果已进一步分流，不直接原样堆砌。

## 失败与降级

- `semantic-nlsql` 未配置或不可用：拆成法规检索 + 案例检索多轮处理。
- 样本过多且分散：先聚焦 1-2 个子问题，不要一次覆盖全部治理议题。
- 类案不足：明确写“当前案例样本有限，不能据此概括稳定裁判倾向”。

## 配套文件

- 研究备忘模板：[template.md](./template.md)
- 真实业务示例：[examples.md](./examples.md)

## 关联 Skill

- 综合召回：[pkulaw-mcp-semantic-nlsql](../pkulaw-mcp-semantic-nlsql/SKILL.md)
- 法规检索：[pkulaw-mcp-law-retrieval](../pkulaw-mcp-law-retrieval/SKILL.md)
- 案例检索：[pkulaw-mcp-case-retrieval](../pkulaw-mcp-case-retrieval/SKILL.md)
- 引用核验：[pkulaw-mcp-citation-validator](../pkulaw-mcp-citation-validator/SKILL.md)
- 法宝超链：[pkulaw-mcp-doc-link](../pkulaw-mcp-doc-link/SKILL.md)
