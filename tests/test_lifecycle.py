import unittest
from object_lifecycle_simulator.core import plan


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.obj = {
            "key": "logs/app",
            "created": "2026-01-01",
            "storage_class": "standard",
        }
        self.policy = {
            "prefix": "logs/",
            "expire_after_days": 30,
            "transition_after_days": 10,
            "storage_class": "archive",
        }

    def action(self, obj=None, as_of="2026-03-01", policies=None):
        return plan([obj or self.obj], policies or [self.policy], as_of)["objects"][0]

    def test_expiry(self):
        self.assertEqual(self.action()["action"], "delete")

    def test_hold_overrides_deletion(self):
        self.assertEqual(self.action(dict(self.obj, legal_hold=True))["action"], "keep")

    def test_retention_and_boundary(self):
        self.assertEqual(
            self.action(dict(self.obj, retain_until="2026-03-02"))["action"], "keep"
        )
        self.assertEqual(
            self.action(dict(self.obj, retain_until="2026-03-01"))["action"], "delete"
        )

    def test_transition_before_expiration(self):
        self.assertEqual(self.action(as_of="2026-01-12")["action"], "transition")

    def test_longest_prefix(self):
        self.assertEqual(
            self.action(
                policies=[self.policy, {"prefix": "logs/app", "expire_after_days": 300}]
            )["action"],
            "keep",
        )

    def test_duplicate_policies_rejected(self):
        with self.assertRaises(ValueError):
            plan([self.obj], [self.policy, self.policy], "2026-03-01")

    def test_future_creation_rejected(self):
        with self.assertRaises(ValueError):
            self.action(as_of="2025-01-01")

    def test_already_transitioned_is_noop(self):
        self.assertEqual(
            self.action(dict(self.obj, storage_class="archive"), as_of="2026-01-12")[
                "action"
            ],
            "keep",
        )
