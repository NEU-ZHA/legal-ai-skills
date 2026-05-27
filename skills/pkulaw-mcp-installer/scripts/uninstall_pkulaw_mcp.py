#!/usr/bin/env python3
"""
北大法宝 MCP 卸载脚本

从 WorkBuddy 的 mcp.json 中移除所有北大法宝 MCP 服务配置。

用法:
  python3 uninstall_pkulaw_mcp.py [--mcp-path <path>]
"""

import json
import os
import sys

PKULAW_SERVER_NAMES = [
    "pkulaw-law-search",
    "pkulaw-citation",
    "pkulaw-hyperlink",
    "pkulaw-recognition",
    "pkulaw-nl-sql",
    "pkulaw-law-keyword",
    "pkulaw-fatiao",
    "pkulaw-case",
    "pkulaw-case-search",
    "pkulaw-case-number",
]


def uninstall(mcp_path: str) -> None:
    if not os.path.exists(mcp_path):
        print(f"⚠️  文件不存在: {mcp_path}")
        sys.exit(1)

    with open(mcp_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "mcpServers" not in data:
        print("⚠️  mcp.json 中没有 mcpServers 配置")
        sys.exit(0)

    removed = []
    for name in PKULAW_SERVER_NAMES:
        if name in data["mcpServers"]:
            del data["mcpServers"][name]
            removed.append(name)

    with open(mcp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    if removed:
        print(f"✅ 已移除 {len(removed)} 个北大法宝 MCP 服务: {', '.join(removed)}")
    else:
        print("ℹ️  未发现北大法宝 MCP 服务配置，无需移除")
    print("⚠️  请重启 WorkBuddy 以使变更生效。")


def main():
    mcp_path = os.path.expanduser("~/.workbuddy/mcp.json")
    if "--mcp-path" in sys.argv:
        idx = sys.argv.index("--mcp-path")
        if idx + 1 < len(sys.argv):
            mcp_path = os.path.expanduser(sys.argv[idx + 1])

    uninstall(mcp_path)


if __name__ == "__main__":
    main()
