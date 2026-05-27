---
name: pkulaw-mcp-installer
description: 一键安装/配置北大法宝（pkulaw.com）MCP 服务。当用户需要安装北大法宝 MCP、配置 pkulaw MCP、给新设备/新用户配置北大法宝法律检索工具时使用此技能。必须保护用户 Token，不在聊天、日志或公开仓库中写入真实凭证。触发词：安装北大法宝MCP、配置pkulaw、北大法宝一键安装、pkulaw setup、MCP安装。
---

# 北大法宝 MCP 一键安装技能

## 概述

此技能用于一键将北大法宝 MCP 服务配置写入目标 MCP 配置文件，免去手动逐个添加的繁琐操作。适用于团队内部推广、新设备配置、给同事/朋友安装北大法宝法律检索能力等场景。

## 包含的10个 MCP 服务

| 服务名 | 功能 | URL |
|--------|------|-----|
| pkulaw-law-search | 法律检索 | mcp-law-search-service |
| pkulaw-citation | 引注校验 | pku_citation_validator |
| pkulaw-hyperlink | 文档链接添加 | add-doc-link |
| pkulaw-recognition | 法律识别 | law_recognition |
| pkulaw-nl-sql | 自然语言检索 | assistant/mcp-pkulaw-search |
| pkulaw-law-keyword | 关键词法律检索 | mcp-law |
| pkulaw-fatiao | 法条检索 | mcp-fatiao |
| pkulaw-case | 案例检索 | mcp-case |
| pkulaw-case-search | 案例搜索 | mcp-case-search-service |
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
- 用户已有 Token → 优先让用户通过环境变量 `PKULAW_AUTH_TOKEN` 或终端交互输入提供，不要让用户把真实 Token 粘贴到公开聊天或文档里
- 用户没有 Token → 引导用户联系北大法宝获取 API 访问权限

### 步骤二：执行安装脚本

运行安装脚本，将10个 MCP 服务配置合并写入 `mcp.json`：

```bash
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --mcp-path ~/.workbuddy/mcp.json
```

脚本会：
1. 读取指定的 MCP 配置文件（不存在则创建）
2. 将10个北大法宝 MCP 配置合并进去（不覆盖其他已有配置）
3. 输出新增/更新的服务列表

**可选参数**：`--mcp-path <path>` 指定自定义配置路径。常见目标包括 WorkBuddy 的 `~/.workbuddy/mcp.json`，或其他运行时自己的 MCP 配置文件。

### 步骤三：确认安装结果

检查脚本输出，确认服务均已成功配置。提醒用户重启对应运行时以加载新配置。

### 步骤四（可选）：验证 MCP 可用性

重启目标运行时后，可引导用户测试任一 MCP 服务是否正常响应，例如：
- 尝试使用 pkulaw-law-search 检索一条法律
- 尝试使用 pkulaw-case 搜索一个案例

## 卸载

如需移除北大法宝 MCP 配置：

```bash
python3 scripts/uninstall_pkulaw_mcp.py --mcp-path ~/.workbuddy/mcp.json
```

同样支持 `--mcp-path <path>` 参数指定自定义路径。

## 注意事项

1. **Token 安全**：Authorization Token 是敏感信息，安装完成后不要在聊天记录中明文保留
2. **增量合并**：安装脚本采用合并策略，不会删除用户已有的其他 MCP 配置
3. **重复安装**：如果已安装过，再次运行会更新 Token（适用于 Token 过期后更换）
4. **重启生效**：修改 MCP 配置后通常必须重启目标运行时才能加载新配置
5. **网络要求**：所有 MCP 服务需要访问 `apim-gateway.pkulaw.com`，确保网络可达
