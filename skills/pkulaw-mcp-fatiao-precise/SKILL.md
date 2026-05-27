---
name: pkulaw-mcp-fatiao-precise
description: >
  精准查找法条，用于在已知法规名称与条号的前提下取回条文原文或可回源的条文内容。Use when：用户已经明确给出法规名称和条号，希望核对条文原文、脚注引用或文书引注。NOT for：模糊主题检索、从长文本自动识别法条、案例检索。要求必须基于当次 MCP 返回作答，禁止编造条文、条号或补写未返回内容。
license: MIT
metadata:
  pkulaw:
    protocol: MCP
    service_source: "北大法宝原生 MCP 服务"
    cli_debug_entry: "@pkulaw/mcp-cli"
    product_lines:
      - 精准查找法条-关键词
    server_ids:
      - fatiao
    mcp_cli: "@pkulaw/mcp-cli"
version: "1.1.0"
---

# 北大法宝 MCP：精准查找法条（fatiao）

这个 Skill 只负责一件事：**在已知法规名 + 条号的情况下，把条文原文取回来。**

它不负责模糊主题检索，也不负责自动识别文本中的法条引用。
如果用户只给了主题词，应该转法规检索；如果用户给的是长文本，应该转法条识别。

## 先看边界

- 本 Skill 用来取回条文内容，不自动判断该条是否当然适用于案件或项目。
- 返回结果仍需结合时效、修订版本、适用范围、地域、上位法/特别法关系继续判断。
- 法规名称、别名、条号格式存在歧义时，应先澄清，不要把模糊命中写成确定依据。

## 默认路由

- 输入中同时出现“法规名 + 第X条 / 条号”：
  - 直接走 `fatiao`
- 只有主题词：
  - 转 `pkulaw-mcp-law-retrieval`
- 输入是一段长文本，里面可能有法条：
  - 转 `pkulaw-mcp-law-recognition`

## 推荐工作流

1. 先确认用户已经给了法规名和条号。
2. 用 `tools` 确认真实 `<toolName>` 与参数名。
3. 调用目标工具，传入法规名关键词与条号。
4. 只整理返回字段，不补写未返回的条文内容。
5. 明确提示仍需复核时效与适用前提。

## 失败与降级

### 允许的失败输出

```markdown
当前未拿到精准法条查询结果。

失败原因：
- [未认证 / 无订阅 / 无结果 / 工具不存在 / 命令报错]

建议动作：
- 检查 `pkulaw-mcp` 配置
- 确认法规全称、别名与条号格式
- 如仅有主题词，请改走法规检索路径
```

### 允许的保守输出

- 只能返回命中法规、条号与条文正文（如有）
- 不得补写未返回的原文

## 输出结构

1. 命中法规
2. 条号
3. 条文正文
4. 复核提醒

## 终端复现与排障

如需在终端复现，请先安装 `@pkulaw/mcp-cli`；安装后命令为 `pkulaw-mcp`。

```bash
pkulaw-mcp tools fatiao
pkulaw-mcp fatiao <toolName> ... --json
```

## 补充材料

- 示例见 [examples.md](examples.md)
