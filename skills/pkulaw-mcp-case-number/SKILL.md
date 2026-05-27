---
name: pkulaw-mcp-case-number
description: >
  案号识别与溯源，用于从文书、备忘、聊天记录或其他长文本中提取案号并回源案件线索。Use when：用户已经有一段文本，想识别其中的案号、批量抽取案号，或核查案号对应案件信息。NOT for：按争议主题检索案例、法条识别、法规主题检索。要求不得编造案号、法院名称与日期，全部基于当次 MCP 返回。
license: MIT
metadata:
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    product_lines:
      - 案号识别与溯源
    server_ids:
      - case-number
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：案号识别与溯源（case-number）

这个 Skill 只负责一件事：**从现有文本里识别案号，并给出可核查的案件线索。**

它不负责替代案例实体分析。
如果用户真正要的是“找类似案例怎么判”，应转到案例检索或类案备忘 Skill。

## 先看边界

- 输出应理解为案号线索，而不是已经完成实体分析。
- 对格式不完整、年份缺失、法院简称缺失、OCR 噪声、批量文本混杂等情况，只能标成待核查线索。
- 不能把疑似案号写成已确认案件信息。

## 默认路由

- 文本里疑似包含案号：
  - 走 `case-number`
- 用户只描述争议点，想找类案：
  - 转 `pkulaw-mcp-case-retrieval`

## 推荐工作流

1. 确认输入是待识别文本，而不是案例检索需求。
2. 用 `tools` 确认真实 `<toolName>` 与参数名。
3. 提交文本进行案号识别。
4. 输出识别到的案号列表和溯源命中情况。
5. 对格式异常或歧义项标记“待人工确认”。

## 失败与降级

### 允许的失败输出

```markdown
当前未拿到案号识别结果。

失败原因：
- [未认证 / 无订阅 / 无结果 / 工具不存在 / 命令报错]

建议动作：
- 检查 `pkulaw-mcp` 配置
- 检查文本中的案号格式和完整度
- 如真正需求是找类案，请改走案例检索路径
```

### 允许的保守输出

- 对歧义项标记“待人工确认”
- 不得把疑似案号写成已确认事实

## 输出结构

1. 识别到的案号列表
2. 溯源命中情况
3. 待人工确认项

## 终端复现与排障

如需在终端复现，请先安装 `@pkulaw/mcp-cli`；安装后命令为 `pkulaw-mcp`。

```bash
pkulaw-mcp tools case-number
pkulaw-mcp case-number <toolName> ... --json
```

## 补充材料

- 示例见 [examples.md](examples.md)
