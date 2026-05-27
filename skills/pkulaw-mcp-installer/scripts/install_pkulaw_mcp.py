#!/usr/bin/env python3
"""
北大法宝 MCP 一键安装脚本

将北大法宝 MCP 服务配置写入目标 MCP 配置文件。
支持增量合并，不会覆盖已有配置。

用法:
  PKULAW_AUTH_TOKEN="..." python3 install_pkulaw_mcp.py [--mcp-path <path>]
  python3 install_pkulaw_mcp.py --token <authorization_token> [--mcp-path <path>]

参数:
  --token              北大法宝 API 的 Bearer Token（不推荐写进 shell history）
  --mcp-path           MCP 配置文件路径（默认 ~/.workbuddy/mcp.json）
"""

import getpass
import json
import os
import sys


# 北大法宝 MCP 服务定义模板
PKULAW_MCP_SERVERS = {
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
    "pkulaw-case-search": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/mcp-case-search-service",
    },
    "pkulaw-case-number": {
        "type": "streamableHttp",
        "url": "https://apim-gateway.pkulaw.com/case_number_recognition",
    },
}


def build_server_config(token: str) -> dict:
    """构建带 Authorization header 的完整 MCP 服务配置。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    return {
        name: {**cfg, "headers": headers}
        for name, cfg in PKULAW_MCP_SERVERS.items()
    }


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


def install(token: str, mcp_path: str) -> None:
    """执行安装：合并北大法宝 MCP 配置到 mcp.json。"""
    data = load_mcp_json(mcp_path)
    new_servers = build_server_config(token)

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
    print(f"\n📋 共配置 {len(new_servers)} 个北大法宝 MCP 服务:")
    for name, cfg in new_servers.items():
        print(f"   • {name} → {cfg['url']}")
    print("\n⚠️  请重启 WorkBuddy 以加载新配置。")


def main():
    token = os.environ.get("PKULAW_AUTH_TOKEN", "")
    mcp_path = os.path.expanduser("~/.workbuddy/mcp.json")

    if "--token" in sys.argv:
        idx = sys.argv.index("--token")
        if idx + 1 < len(sys.argv):
            token = sys.argv[idx + 1]
        else:
            print("❌ 错误: --token 需要提供 Token 参数")
            sys.exit(1)

    # Backward compatibility with the old positional form.
    positional = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if not token and positional:
        token = positional[0]

    if "--mcp-path" in sys.argv:
        idx = sys.argv.index("--mcp-path")
        if idx + 1 < len(sys.argv):
            mcp_path = os.path.expanduser(sys.argv[idx + 1])
        else:
            print("❌ 错误: --mcp-path 需要提供路径参数")
            sys.exit(1)

    if not token:
        token = getpass.getpass("请输入北大法宝 Bearer Token（不会回显）: ").strip()

    if not token:
        print("❌ 错误: 未提供 Authorization Token")
        sys.exit(1)

    install(token, mcp_path)


if __name__ == "__main__":
    main()
