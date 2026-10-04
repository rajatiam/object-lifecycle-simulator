import unittest, json, csv, io
from object_lifecycle_simulator.core import compare


class FeatureTests(unittest.TestCase):
    def test_changed_actions_and_inventory(self):
        before = {
            "dry_run": True,
            "objects": [
                {"key": "a", "action": "keep"},
                {"key": "gone", "action": "keep"},
            ],
        }
        after = {
            "dry_run": True,
            "objects": [
                {"key": "a", "action": "delete"},
                {"key": "new", "action": "keep"},
            ],
        }
        result = compare(before, after)
        self.assertEqual(result["added"], ["new"])
        self.assertEqual(result["removed"], ["gone"])
        self.assertEqual(result["changed"][0]["key"], "a")

    def test_transition_target_changes_detected(self):
        before = {
            "dry_run": True,
            "objects": [
                {"key": "a", "action": "transition", "storage_class": "archive"}
            ],
        }
        after = {
            "dry_run": True,
            "objects": [
                {"key": "a", "action": "transition", "storage_class": "infrequent"}
            ],
        }
        self.assertEqual(len(compare(before, after)["changed"]), 1)

    def test_non_dry_run_rejected(self):
        with self.assertRaises(ValueError):
            compare({"dry_run": False, "objects": []}, {"dry_run": True, "objects": []})
