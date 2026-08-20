#!/usr/bin/env python3
"""
北大法宝 MCP 一键安装脚本

将北大法宝 MCP 服务配置写入目标 MCP 配置文件。
支持增量合并，不会覆盖已有配置。

用法:
  PKULAW_AUTH_TOKEN="..." python3 install_pkulaw_mcp.py [--mcp-path <path>]
  python3 install_pkulaw_mcp.py --token <authorization_token> [--mcp-path <path>]
  python3 install_pkulaw_mcp.py --services economy [--mcp-path <path>]
  python3 install_pkulaw_mcp.py --services pkulaw-citation,pkulaw-hyperlink

参数:
  --token              北大法宝 API 的 Bearer Token（不推荐写进 shell history）
  --mcp-path           MCP 配置文件路径（默认 ~/.workbuddy/mcp.json）
  --services           all（默认）、economy/basic，或逗号分隔的服务名
  --include-advanced   兼容旧参数，等同于 --services all
"""

import argparse
import getpass
import json
import os
import sys


# 北大法宝 MCP 已改为统一积分。安装全部服务不会直接消耗积分，实际调用才扣费。
# 25 积分服务应作为日常检索入口；125 积分服务只在任务确实需要时升级调用。
BASIC_MCP_SERVERS = {
    "pkulaw-law-keyword": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/mcp-law",
    },
    "pkulaw-fatiao": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/mcp-fatiao",
    },
    "pkulaw-case": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/mcp-case",
    },
}

ADVANCED_MCP_SERVERS = {
    "pkulaw-law-search": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/mcp-law-search-service",
    },
    "pkulaw-citation": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/pku_citation_validator",
    },
    "pkulaw-hyperlink": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/add-doc-link",
    },
    "pkulaw-recognition": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/law_recognition",
    },
    "pkulaw-nl-sql": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/assistant/mcp-pkulaw-search",
    },
    "pkulaw-case-search": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/mcp-case-search-service",
    },
    "pkulaw-case-number": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/case_number_recognition",
    },
}

PKULAW_MCP_SERVERS = {**BASIC_MCP_SERVERS, **ADVANCED_MCP_SERVERS}

SERVICE_COSTS = {
    "pkulaw-law-keyword": 25,
    "pkulaw-fatiao": 25,
    "pkulaw-case": 25,
    "pkulaw-law-search": 125,
    "pkulaw-citation": 125,
    "pkulaw-hyperlink": 125,
    "pkulaw-recognition": 125,
    "pkulaw-nl-sql": 125,
    "pkulaw-case-search": 125,
    "pkulaw-case-number": 125,
}


def select_servers(services_arg: str, include_advanced: bool) -> dict:
    """选择要安装的 MCP 服务。统一积分模式下默认安装全部 10 项。"""
    if include_advanced or services_arg == "all":
        return PKULAW_MCP_SERVERS

    if services_arg in {"basic", "economy"}:
        return BASIC_MCP_SERVERS

    selected_names = [name.strip() for name in services_arg.split(",") if name.strip()]
    unknown = [name for name in selected_names if name not in PKULAW_MCP_SERVERS]
    if unknown:
        print(f"❌ 错误: 未知服务名: {', '.join(unknown)}")
        print(f"可用服务: {', '.join(PKULAW_MCP_SERVERS)}")
        sys.exit(1)
    if not selected_names:
        print("❌ 错误: --services 不能为空")
        sys.exit(1)
    return {name: PKULAW_MCP_SERVERS[name] for name in selected_names}


def build_server_config(token: str, servers: dict) -> dict:
    """构建带 Authorization header 的完整 MCP 服务配置。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    return {
        name: {**cfg, "headers": headers}
        for name, cfg in servers.items()
    }


def normalize_token(token: str) -> str:
    """兼容控制台复制出的 `Bearer ...` 和仅复制 token 正文两种格式。"""
    token = token.strip()
    if token.lower().startswith("bearer "):
        return token[7:].strip()
    return token


def load_mcp_json(path: str) -> dict:
    """读取已有的 mcp.json，不存在则返回空结构。"""
    if not os.path.exists(path):
        return {"mcpServers": {}}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "mcpServers" not in data:
        data["mcpServers"] = {}
    return data


def save_mcp_json(path: str, data: dict) -> None:
    """将配置写回 mcp.json。"""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def install(token: str, mcp_path: str, servers: dict) -> None:
    """执行安装：合并北大法宝 MCP 配置到 mcp.json。"""
    data = load_mcp_json(mcp_path)
    new_servers = build_server_config(token, servers)

    # 统计新增/更新
    added = []
    updated = []
    for name, cfg in new_servers.items():
        if name in data["mcpServers"]:
            updated.append(name)
        else:
            added.append(name)
        data["mcpServers"][name] = cfg

    save_mcp_json(mcp_path, data)

    print(f"✅ 北大法宝 MCP 配置已写入: {mcp_path}")
    if added:
        print(f"   新增 {len(added)} 个服务: {', '.join(added)}")
    if updated:
        print(f"   更新 {len(updated)} 个服务: {', '.join(updated)}")
    print(f"\n📋 本次配置 {len(new_servers)} 个北大法宝 MCP 服务:")
    for name, cfg in new_servers.items():
        print(f"   • {name} ({SERVICE_COSTS[name]} 积分/次) → {cfg['url']}")
    if set(new_servers) == set(BASIC_MCP_SERVERS):
        print("\nℹ️  当前只配置 3 项经济型服务；如需完整能力，可改用 --services all。")
    if set(new_servers) == set(PKULAW_MCP_SERVERS):
        print("\n💡 已配置全部 10 项。日常检索先用 25 积分服务，结果不足或任务明确需要时再调用 125 积分服务。")
    print("\n⚠️  请重启 WorkBuddy 以加载新配置。")


def main():
    parser = argparse.ArgumentParser(description="安装/更新北大法宝 MCP 配置")
    parser.add_argument("positional_token", nargs="?", help="兼容旧用法的位置参数 token")
    parser.add_argument("--token", help="北大法宝 Bearer Token（不推荐写进 shell history）")
    parser.add_argument("--mcp-path", default="~/.workbuddy/mcp.json", help="MCP 配置文件路径")
    parser.add_argument(
        "--services",
        default="all",
        help="all（默认）、economy/basic，或逗号分隔的服务名",
    )
    parser.add_argument(
        "--include-advanced",
        action="store_true",
        help="安装全部高级可选服务，等同于 --services all",
    )
    args = parser.parse_args()

    token = os.environ.get("PKULAW_AUTH_TOKEN", "") or args.token or args.positional_token or ""
    mcp_path = os.path.expanduser(args.mcp_path)
    servers = select_servers(args.services, args.include_advanced)

    if not token:
        token = getpass.getpass("请输入北大法宝 Bearer Token（不会回显）: ").strip()

    token = normalize_token(token)

    if not token:
        print("❌ 错误: 未提供 Authorization Token")
        sys.exit(1)

    install(token, mcp_path, servers)


if __name__ == "__main__":
    main()
