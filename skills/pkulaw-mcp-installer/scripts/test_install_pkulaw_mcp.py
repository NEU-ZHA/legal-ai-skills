#!/usr/bin/env python3
"""Regression tests for the PKULaw MCP installer."""

import unittest

from install_pkulaw_mcp import (
    BASIC_MCP_SERVERS,
    PKULAW_MCP_SERVERS,
    SERVICE_COSTS,
    build_server_config,
    normalize_token,
    select_servers,
)


class InstallerTests(unittest.TestCase):
    def test_catalog_has_all_ten_services_and_costs(self):
        self.assertEqual(len(PKULAW_MCP_SERVERS), 10)
        self.assertEqual(set(PKULAW_MCP_SERVERS), set(SERVICE_COSTS))
        self.assertEqual(set(SERVICE_COSTS.values()), {25, 125})

    def test_all_and_economy_profiles(self):
        self.assertEqual(select_servers("all", False), PKULAW_MCP_SERVERS)
        self.assertEqual(select_servers("economy", False), BASIC_MCP_SERVERS)
        self.assertEqual(select_servers("basic", False), BASIC_MCP_SERVERS)

    def test_console_bearer_prefix_is_normalized(self):
        self.assertEqual(normalize_token("Bearer example-token"), "example-token")
        self.assertEqual(normalize_token("bearer example-token"), "example-token")
        self.assertEqual(normalize_token("example-token"), "example-token")

    def test_authorization_header_has_one_bearer_prefix(self):
        config = build_server_config("example-token", BASIC_MCP_SERVERS)
        for server in config.values():
            self.assertEqual(server["headers"]["Authorization"], "Bearer example-token")


if __name__ == "__main__":
    unittest.main()
