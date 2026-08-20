---
name: pkulaw-mcp-installer
description: 一键安装/配置北大法宝（pkulaw.com）MCP 服务。当用户需要安装北大法宝 MCP、配置 pkulaw MCP、给新设备/新用户配置北大法宝法律检索工具时使用此技能。必须保护用户 Token，不在聊天、日志或公开仓库中写入真实凭证。触发词：安装北大法宝MCP、配置pkulaw、北大法宝一键安装、pkulaw setup、MCP安装。
---

# 北大法宝 MCP 一键安装技能

## 概述

此技能用于一键将北大法宝 MCP 服务配置写入目标 MCP 配置文件，免去手动逐个添加的繁琐操作。适用于团队内部推广、新设备配置、给同事/朋友安装北大法宝法律检索能力等场景。

## 统一积分模式

北大法宝 MCP 现在使用统一积分：服务可以在控制台按需开启，真正调用时才扣积分。安装能力与调用成本是两件事：建议把控制台已经开启的服务全部配置到 AI，但执行任务时必须先选成本最低且足够完成任务的服务，不能把 10 项逐个调用一遍。

| 分类 | 服务名 | 控制台能力 | 约积分/次 | 默认策略 |
|------|--------|------------|-----------|----------|
| 法规法条 | `pkulaw-fatiao` | 精准查找法条-关键词 | 25 | 已知法规名和条号时首选 |
| 法规法条 | `pkulaw-law-keyword` | 检索法律法规-关键词 | 25 | 普通法规研究首选 |
| 法规法条 | `pkulaw-law-search` | 检索法律法规-语义 | 125 | 两轮合理关键词仍不足时升级 |
| 司法案例 | `pkulaw-case` | 检索司法案例-关键词 | 25 | 普通类案检索首选 |
| 司法案例 | `pkulaw-case-search` | 检索司法案例-语义 | 125 | 关键词难以表达事实相似性时升级 |
| 引用溯源 | `pkulaw-recognition` | 法条识别与溯源 | 125 | 仅用于从非结构化文本识别法条 |
| 引用溯源 | `pkulaw-hyperlink` | 法宝超链 | 125 | 仅在依据已经核验后补链接 |
| 引用溯源 | `pkulaw-citation` | 修正生成幻觉-法条 | 125 | 仅在任务明确要求引用核验时调用 |
| 引用溯源 | `pkulaw-case-number` | 案号识别与溯源 | 125 | 精确案号关键词检索失败或批量提取时调用 |
| 综合检索 | `pkulaw-nl-sql` | 法律智能检索 | 125 | 无法拆分的跨库复杂问题最后使用 |

成本规则：

1. 明确法规词、法条或案由时，先用 25 积分服务。
2. 先改写一次关键词再考虑升级；不要因第一次无结果立即切换 125 积分服务。
3. 引用核验、法条识别、补超链等专门任务可以直接调用对应 125 积分服务，但只调用完成任务所需的那一项。
4. 跨法规与案例的研究先拆成两次 25 积分检索；确实无法拆分或仍有关键缺口时才用综合检索。

## 触发场景

当用户提出以下需求时使用此技能：
- "帮我安装北大法宝MCP"
- "配置pkulaw MCP"
- "给新设备装北大法宝"
- "我也要用北大法宝检索"
- "怎么配置北大法宝MCP"
- "pkulaw setup"

## 工作流程

### 步骤一：获取 Authorization Token

向用户确认北大法宝 API 的 Bearer Token。该 Token 是敏感凭证。

**获取方式**：
- 用户已有 Token → 优先让用户通过环境变量 `PKULAW_AUTH_TOKEN`、终端交互或本机私有配置提供，不要让用户把真实 Token 写进仓库文件、示例、模板、截图或 Issue
- 用户没有 Token → 引导用户进入北大法宝 MCP 控制台，在“获取 Token”页面新建 Token、开启需要的服务并复制接入配置。用户可以开启全部 10 项，成本由实际调用决定。

### 步骤二：确认控制台已开启服务

询问用户：

```text
请确认“获取 Token”页面显示已开启多少项服务。可以提供服务列表文字或截图，但不要展示 Token 明文。我会按控制台已开启项配置，并使用节省积分的调用顺序。
```

映射规则：

- 如果用户说“法规关键词检索”或页面显示 `mcp-law`，安装 `pkulaw-law-keyword`。
- 如果用户说“精准法条查找/法条检索”或页面显示 `mcp-fatiao`，安装 `pkulaw-fatiao`。
- 如果用户说“司法案例关键词检索/案例检索”或页面显示 `mcp-case`，安装 `pkulaw-case`。
- 控制台显示 `10/10 已开` 时，安装全部 10 项。
- 只开启部分服务时，按上表映射为 `--services` 参数；不要配置控制台未开启的服务。
- 截图无法判断时，可以让用户直接复制服务名称，不要求用户发送 Token 明文。

### 步骤三：执行安装脚本

控制台已开启全部 10 项时，直接运行：

```bash
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --mcp-path ~/.workbuddy/mcp.json
```

脚本默认配置全部 10 项。只想配置 3 项经济型检索服务时：

```bash
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --services economy --mcp-path ~/.workbuddy/mcp.json
```

只配置控制台已开启的指定服务时：

```bash
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --services pkulaw-law-keyword,pkulaw-fatiao,pkulaw-case,pkulaw-citation --mcp-path ~/.workbuddy/mcp.json
```

脚本会：
1. 读取指定的 MCP 配置文件（不存在则创建）
2. 将所选北大法宝 MCP 配置合并进去（不覆盖其他已有配置）
3. 输出新增/更新的服务列表

**可选参数**：

- `--mcp-path <path>` 指定自定义配置路径。常见目标包括 WorkBuddy 的 `~/.workbuddy/mcp.json`，或其他运行时自己的 MCP 配置文件。
- `--services all` 是默认值，安装全部 10 项。
- `--services economy` 或 `basic` 只安装三个 25 积分检索服务。
- `--services 服务名1,服务名2` 只安装控制台已开启的指定服务。
- `--include-advanced` 是兼容旧版的参数，等同于 `--services all`。

### 步骤四：确认安装结果

检查脚本输出，确认服务均已成功配置。提醒用户重启对应运行时以加载新配置。

### 步骤五（可选）：验证 MCP 可用性

重启目标运行时后，可引导用户测试任一 MCP 服务是否正常响应，例如：
- 尝试使用 pkulaw-law-keyword 检索一条法规
- 尝试使用 pkulaw-fatiao 获取一个已知法条
- 尝试使用 pkulaw-case 搜索一个案例

安装完成后的研究任务应交给 `pkulaw-mcp-legal-research` 总路由。需要确定性检查路由时，可运行：

```bash
python3 ../pkulaw-mcp-legal-research/scripts/recommend_route.py --intent law-topic
python3 ../pkulaw-mcp-legal-research/scripts/recommend_route.py --intent case-topic
```

## 卸载

如需移除北大法宝 MCP 配置：

```bash
python3 scripts/uninstall_pkulaw_mcp.py --mcp-path ~/.workbuddy/mcp.json
```

同样支持 `--mcp-path <path>` 参数指定自定义路径。

## 注意事项

1. **Token 安全**：Authorization Token 是敏感信息，只放在本机环境变量、MCP 配置或私有文件里
2. **增量合并**：安装脚本采用合并策略，不会删除用户已有的其他 MCP 配置
3. **重复安装**：如果已安装过，再次运行会更新 Token（适用于 Token 过期后更换）
4. **重启生效**：修改 MCP 配置后通常必须重启目标运行时才能加载新配置
5. **积分控制**：安装全部服务不等于每次全部调用；先用 25 积分服务，必要时再升级到 125 积分服务
6. **控制台开关**：配置项应与“获取 Token”页面当前已开启服务一致
7. **网络要求**：所有 MCP 服务需要访问 `apim-gateway.pkulaw.com`，确保网络可达
