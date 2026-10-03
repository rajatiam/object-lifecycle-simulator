"""Exercise the shipped examples through the real process entrypoint."""

import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def test_help_entrypoint(self):
        result = subprocess.run(
            [sys.executable, "-m", "object_lifecycle_simulator", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout)

    def test_documented_workflow(self):
        with tempfile.TemporaryDirectory() as folder:
            clone = Path(folder)
            shutil.copytree(
                ROOT / "object_lifecycle_simulator",
                clone / "object_lifecycle_simulator",
            )
            shutil.copytree(ROOT / "examples", clone / "examples")
            for command in [
                "plan examples/objects.json examples/policies.json --as-of 2026-10-03"
            ]:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "object_lifecycle_simulator",
                        *command.split(),
                    ],
                    cwd=clone,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
            self.assertEqual(
                payload["summary"], {"keep": 1, "transition": 1, "delete": 1}
            )
