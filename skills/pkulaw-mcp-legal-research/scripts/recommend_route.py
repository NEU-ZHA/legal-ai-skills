#!/usr/bin/env python3
"""Return the lowest-cost PKULaw MCP route for a declared legal-research intent."""

import argparse
import json


ROUTES = {
    "law-topic": {
        "primary": ["law-keyword"],
        "primary_cost": 25,
        "escalation": ["law-semantic"],
        "escalation_cost": 125,
        "escalate_when": "两轮有理由的关键词检索仍未找到相关规范时升级。",
    },
    "article": {
        "primary": ["fatiao"],
        "primary_cost": 25,
        "escalation": [],
        "escalation_cost": 0,
        "escalate_when": "不自动升级；先核对法规名称和条号。",
    },
    "case-topic": {
        "primary": ["case-keyword"],
        "primary_cost": 25,
        "escalation": ["case-semantic"],
        "escalation_cost": 125,
        "escalate_when": "两轮有理由的关键词检索仍未找到事实相似案例时升级。",
    },
    "exact-case-number": {
        "primary": ["case-keyword"],
        "primary_cost": 25,
        "escalation": ["case-number"],
        "escalation_cost": 125,
        "escalate_when": "关键词检索没有返回精确案号匹配或来源记录时升级。",
    },
    "citation-check": {
        "primary": ["citation-validator"],
        "primary_cost": 125,
        "escalation": [],
        "escalation_cost": 0,
        "escalate_when": "任务直接需要专门核验能力；不要调用无关服务。",
    },
    "law-recognition": {
        "primary": ["law-recognition"],
        "primary_cost": 125,
        "escalation": [],
        "escalation_cost": 0,
        "escalate_when": "仅在需要从非结构化文本提取法条时使用。",
    },
    "add-links": {
        "primary": ["doc-link"],
        "primary_cost": 125,
        "escalation": [],
        "escalation_cost": 0,
        "escalate_when": "仅在引用依据已经核验后运行。",
    },
    "cross-domain": {
        "primary": ["law-keyword", "case-keyword"],
        "primary_cost": 50,
        "escalation": ["semantic-nlsql"],
        "escalation_cost": 125,
        "escalate_when": "问题无法可靠拆分，或定向检索后仍有影响结论的关键缺口时升级。",
    },
}


def recommend(intent: str) -> dict:
    route = ROUTES[intent]
    return {"intent": intent, **route, "never_call_all_services": True}


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend a cost-aware PKULaw MCP route")
    parser.add_argument("--intent", required=True, choices=sorted(ROUTES))
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()
    indent = None if args.compact else 2
    print(json.dumps(recommend(args.intent), ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
