#!/usr/bin/env python3
"""Regression tests for PKULaw MCP cost-aware routing."""

import unittest

from recommend_route import ROUTES, recommend


class RouteTests(unittest.TestCase):
    def test_every_route_avoids_calling_all_services(self):
        for intent in ROUTES:
            with self.subTest(intent=intent):
                self.assertTrue(recommend(intent)["never_call_all_services"])

    def test_common_retrieval_starts_with_25_point_services(self):
        for intent in ("law-topic", "article", "case-topic", "exact-case-number"):
            with self.subTest(intent=intent):
                self.assertEqual(ROUTES[intent]["primary_cost"], 25)

    def test_cross_domain_is_cheaper_before_semantic_escalation(self):
        route = ROUTES["cross-domain"]
        self.assertLess(route["primary_cost"], route["escalation_cost"])
        self.assertEqual(route["escalation"], ["semantic-nlsql"])

    def test_specialist_tasks_call_only_the_required_service(self):
        for intent in ("citation-check", "law-recognition", "add-links"):
            with self.subTest(intent=intent):
                self.assertEqual(len(ROUTES[intent]["primary"]), 1)
                self.assertEqual(ROUTES[intent]["escalation"], [])


if __name__ == "__main__":
    unittest.main()
