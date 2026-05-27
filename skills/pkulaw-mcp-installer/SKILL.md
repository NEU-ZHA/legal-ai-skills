---
name: pkulaw-mcp-installer
description: 一键安装/配置北大法宝（pkulaw.com）MCP 服务。当用户需要安装北大法宝 MCP、配置 pkulaw MCP、给新设备/新用户配置北大法宝法律检索工具时使用此技能。必须保护用户 Token，不在聊天、日志或公开仓库中写入真实凭证。触发词：安装北大法宝MCP、配置pkulaw、北大法宝一键安装、pkulaw setup、MCP安装。
---

# 北大法宝 MCP 一键安装技能

## 概述

此技能用于一键将北大法宝 MCP 服务配置写入目标 MCP 配置文件，免去手动逐个添加的繁琐操作。适用于团队内部推广、新设备配置、给同事/朋友安装北大法宝法律检索能力等场景。

## 服务选择逻辑

安装前先问用户已经购买/开通了哪些北大法宝 MCP 服务。用户不一定知道准确英文服务名，可以让用户提供：

- 服务名称或购买清单文字；
- 订单页、服务页、token 页面截图；
- 北大法宝后台里显示的已开通服务列表。

根据用户提供的信息，把已购买服务映射成脚本里的 `--services` 参数。不要替用户假定已经购买高级 MCP。用户完全不知道怎么选时，再建议从三项基础 MCP 开始：法规关键词检索、精准法条查找、司法案例关键词检索。

## 常见基础 MCP 服务

| 服务名 | 对应能力 | URL |
|--------|----------|-----|
| pkulaw-law-keyword | 法规关键词检索 | mcp-law |
| pkulaw-fatiao | 精准法条查找 | mcp-fatiao |
| pkulaw-case | 司法案例关键词检索 | mcp-case |

## 高级可选 MCP 服务

以下服务只有在用户已经确认购买/开通对应订阅时才建议启用。不要让新手误以为必须一次性购买全部服务。

| 服务名 | 对应能力 | URL |
|--------|----------|-----|
| pkulaw-law-search | 法规语义检索 | mcp-law-search-service |
| pkulaw-case-search | 案例语义检索 | mcp-case-search-service |
| pkulaw-citation | 引注/引用校验 | pku_citation_validator |
| pkulaw-hyperlink | 文档链接添加 | add-doc-link |
| pkulaw-recognition | 法律识别 | law_recognition |
| pkulaw-nl-sql | 自然语言/跨库检索 | assistant/mcp-pkulaw-search |
| pkulaw-case-number | 案号识别 | case_number_recognition |

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
- 用户没有 Token → 引导用户在浏览器搜索“北大法宝 MCP”，进入北大法宝 MCP 服务页面，按需购买/开通服务。不会选时，建议先从法规关键词检索、精准法条查找、司法案例关键词检索三项开始。页面生成 Token 后，再回到本机用本 skill 配置。

### 步骤二：确认已购买服务

询问用户：

```text
你购买/开通了哪些北大法宝 MCP 服务？可以直接发服务名称、购买页面文字、服务列表截图或 token 页面截图。我会根据这些信息选择要安装的 MCP。
```

映射规则：

- 如果用户说“法规关键词检索”或页面显示 `mcp-law`，安装 `pkulaw-law-keyword`。
- 如果用户说“精准法条查找/法条检索”或页面显示 `mcp-fatiao`，安装 `pkulaw-fatiao`。
- 如果用户说“司法案例关键词检索/案例检索”或页面显示 `mcp-case`，安装 `pkulaw-case`。
- 如果用户提供高级服务名称，再按高级可选 MCP 表映射。
- 如果无法从截图/文字判断，先问清楚，不要乱装高级服务。

### 步骤三：执行安装脚本

根据已确认服务运行安装脚本。示例：只安装基础三项时：

```bash
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --mcp-path ~/.workbuddy/mcp.json
```

安装用户已购买的指定服务时：

```bash
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --services pkulaw-citation,pkulaw-hyperlink --mcp-path ~/.workbuddy/mcp.json
```

只有用户确认已购买全部高级 MCP 时，才使用：

```bash
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --services all --mcp-path ~/.workbuddy/mcp.json
```

脚本会：
1. 读取指定的 MCP 配置文件（不存在则创建）
2. 将所选北大法宝 MCP 配置合并进去（不覆盖其他已有配置）
3. 输出新增/更新的服务列表

**可选参数**：

- `--mcp-path <path>` 指定自定义配置路径。常见目标包括 WorkBuddy 的 `~/.workbuddy/mcp.json`，或其他运行时自己的 MCP 配置文件。
- `--services basic` 只安装基础三项；用户未提供购买信息时可作为保守默认值。
- `--services all` 或 `--include-advanced` 安装全部服务，仅适合已经确认全部订阅的用户。
- `--services 服务名1,服务名2` 只安装用户已购买的指定服务。

### 步骤四：确认安装结果

检查脚本输出，确认服务均已成功配置。提醒用户重启对应运行时以加载新配置。

### 步骤五（可选）：验证 MCP 可用性

重启目标运行时后，可引导用户测试任一 MCP 服务是否正常响应，例如：
- 尝试使用 pkulaw-law-keyword 检索一条法规
- 尝试使用 pkulaw-fatiao 获取一个已知法条
- 尝试使用 pkulaw-case 搜索一个案例

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
5. **订阅要求**：先按用户购买信息安装；高级 MCP 只有在用户确认已购买/开通时才启用
6. **网络要求**：所有 MCP 服务需要访问 `apim-gateway.pkulaw.com`，确保网络可达
