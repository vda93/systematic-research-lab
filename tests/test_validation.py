"""Semantic identities, explicit tolerances and invalid-input boundaries."""

import unittest

from srl.validation import compare_events


class ValidationTests(unittest.TestCase):
    def test_identity_join_accepts_reordering_and_counts_matches(self):
        left = [{"key": "b", "value": 2}, {"key": "a", "value": 1}]
        result = compare_events(iter(left), reversed(left))
        self.assertEqual(result, {"status": "PASS", "matched": 2, "differences": []})

    def test_only_declared_numeric_field_gets_absolute_tolerance(self):
        left = [{"key": "a", "price": 10.0, "side": "buy"}]
        near = [{"key": "a", "price": 10.00001, "side": "buy"}]
        self.assertEqual(compare_events(left, near, tolerant_fields=("price",), atol=.0001)["status"], "PASS")
        self.assertEqual(compare_events(left, near)["status"], "FAIL")
        far = [{"key": "a", "price": 10.0, "side": "sell"}]
        self.assertEqual(compare_events(left, far, tolerant_fields=("price",), atol=100)["status"], "FAIL")

    def test_missing_identity_schema_and_exact_type_are_differences(self):
        left = [{"key": "a", "value": 1}]
        for right in [[{"key": "b", "value": 1}], [{"key": "a"}], [{"key": "a", "value": True}]]:
            result = compare_events(left, right)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(result["differences"])

    def test_both_empty_is_fail_not_parity_evidence(self):
        self.assertEqual(compare_events([], [])["status"], "FAIL")

    def test_tolerance_accepts_boundary_but_rejects_opposite_extremes(self):
        self.assertEqual(compare_events([{"key": "a", "v": 1}], [{"key": "a", "v": 2}],
                                        tolerant_fields=("v",), atol=1)["status"], "PASS")
        self.assertEqual(compare_events([{"key": "a", "v": -1e308}], [{"key": "a", "v": 1e308}],
                                        tolerant_fields=("v",), atol=1e308)["status"], "FAIL")

    def test_invalid_rows_and_tolerance_are_rejected(self):
        good = [{"key": "a", "value": 1.0}]
        bad_rows = [[{}], [{"key": " "}], [{"key": float("nan")}],
                    [{"key": "a", "value": float("inf")}],
                    [{"key": "a", "value": [1]}], good + good,
                    [{"key": "a", float("nan"): 1}]]
        for bad in bad_rows:
            with self.subTest(rows=bad), self.assertRaises(ValueError):
                compare_events(good, bad)
        for args in [dict(tolerant_fields=("key",)), dict(tolerant_fields=("value", "value")),
                     dict(tolerant_fields=("missing",)), dict(atol=-1),
                     dict(atol=float("nan")), dict(atol=float("inf")), dict(atol=True)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                compare_events(good, good, **args)
        with self.assertRaises(ValueError):
            compare_events([{"key": "a", "value": "one"}], good, tolerant_fields=("value",))


if __name__ == "__main__":
    unittest.main()
