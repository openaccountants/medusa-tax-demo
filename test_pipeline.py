"""Tests for Medusa tax provider demo."""

import unittest
from oa_client import OAClient
import tax_provider
import medusa_client


class MedusaTaxDemoTests(unittest.TestCase):
    def setUp(self):
        self.oa = OAClient(token=None)
        self.plan = self.oa.start("Calculate sales tax on checkout", "US")
        slug = (self.plan.get("skills_to_load") or [None])[0]
        self.skill = self.oa.get_skill(slug)

    def test_mock_oa_client_rates(self):
        self.assertEqual(self.plan["jurisdiction"], "US")
        self.assertEqual(self.skill["tier"], 1)
        self.assertIn("Amir Pelinkovic", self.skill["verifier"])

    def test_chicago_undercharging(self):
        cart = {
            "id": "cart_01",
            "state": "IL",
            "city": "Chicago",
            "subtotal": 200.0,
            "currency": "USD",
            "medusa_region_rate": 0.0625,
        }
        res = tax_provider.check(cart, self.skill)
        self.assertEqual(res["status"], "warn")
        self.assertIn("Under-charging", res["headline"])
        self.assertAlmostEqual(res["oa_rate"], 0.1025)

    def test_portland_overcharging(self):
        cart = {
            "id": "cart_02",
            "state": "OR",
            "city": "Portland",
            "subtotal": 150.0,
            "currency": "USD",
            "medusa_region_rate": 0.06,
        }
        res = tax_provider.check(cart, self.skill)
        self.assertEqual(res["status"], "warn")
        self.assertIn("Over-charging", res["headline"])
        self.assertAlmostEqual(res["oa_rate"], 0.0)

    def test_austin_correct(self):
        cart = {
            "id": "cart_03",
            "state": "TX",
            "city": "Austin",
            "subtotal": 300.0,
            "currency": "USD",
            "medusa_region_rate": 0.0825,
        }
        res = tax_provider.check(cart, self.skill)
        self.assertEqual(res["status"], "ok")
        self.assertIn("Correct", res["headline"])

    def test_samples_extraction(self):
        carts = medusa_client.extract("samples/carts.json")
        self.assertEqual(len(carts), 4)
        norm = medusa_client.normalize(carts[0])
        self.assertEqual(norm["state"], "IL")
        self.assertEqual(norm["city"], "Chicago")


if __name__ == "__main__":
    unittest.main()
