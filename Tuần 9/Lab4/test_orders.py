import os
import unittest
from unittest.mock import patch

from app import create_app


class OrderRoutingTest(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ):
            os.environ.pop("V2_PERCENT", None)
            self.app = create_app()
        self.client = self.app.test_client()

    def assert_routes_to(self, account_id, version, headers=None):
        response = self.client.post(
            "/orders", json={"account_id": account_id}, headers=headers
        )
        self.assertEqual(response.status_code, 201 if version == "v2" else 200)
        self.assertEqual(response.headers["X-Order-Handler"], version)
        result = response.get_json()
        self.assertEqual(result["account_id"], account_id)
        self.assertEqual(result["status"], "created")
        if version == "v2":
            self.assertTrue(result["order_id"])
        else:
            self.assertNotIn("order_id", result)

    def test_cohorts_route_to_v2_even_at_zero_percent(self):
        self.app.config["V2_PERCENT"] = 0
        for cohort in ("beta", "Internal"):
            with self.subTest(cohort=cohort):
                self.assert_routes_to("customer_69", "v2", {"X-Cohort": cohort})

    def test_allow_list_routes_to_v2_even_at_zero_percent(self):
        self.app.config["V2_PERCENT"] = 0
        for account_id in ("acct_42", "acct_99"):
            with self.subTest(account_id=account_id):
                self.assert_routes_to(account_id, "v2")

    def test_default_five_percent_uses_stable_buckets(self):
        self.assertEqual(self.app.config["V2_PERCENT"], 5)
        for _ in range(2):
            self.assert_routes_to("customer_195", "v2")  # Bucket 4
            self.assert_routes_to("customer_69", "v1")  # Bucket 5

    def test_unknown_cohort_uses_normal_routing(self):
        self.assert_routes_to("customer_69", "v1", {"X-Cohort": "other"})

    def test_zero_percent_disables_bucket_rollout(self):
        self.app.config["V2_PERCENT"] = 0
        self.assert_routes_to("customer_195", "v1")

    def test_hundred_percent_routes_all_sample_accounts_to_v2(self):
        with patch.dict(os.environ, {"V2_PERCENT": "100"}):
            self.client = create_app().test_client()
        for account_id in ("customer_69", "customer_195", "another_customer", "acct_42"):
            with self.subTest(account_id=account_id):
                self.assert_routes_to(account_id, "v2")

    def test_invalid_payload_returns_bad_request(self):
        for payload in ([], {}, {"account_id": 42}, {"account_id": " "}):
            with self.subTest(payload=payload):
                response = self.client.post("/orders", json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertNotIn("X-Order-Handler", response.headers)

    def test_invalid_rollout_percentage_is_rejected(self):
        for percent in ("-1", "101", "invalid"):
            with self.subTest(percent=percent), patch.dict(os.environ, {"V2_PERCENT": percent}):
                with self.assertRaises(ValueError):
                    create_app()


if __name__ == "__main__":
    unittest.main()
