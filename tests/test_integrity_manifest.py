"""Regression tests for the integrity manifest CLI.

Run from repository root: python3 -m unittest discover -s tests -v
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "integrity_manifest.py"


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "sample"
        self.root.mkdir()
        (self.root / "nested").mkdir()
        (self.root / "nested" / "hello.txt").write_bytes(b"hello\n")
        self.manifest = self.base / "manifest.json"

    def run_cli(self, action):
        return subprocess.run(
            [sys.executable, str(SCRIPT), action, str(self.root), str(self.manifest)],
            capture_output=True, text=True, check=False,
        )

    def test_round_trip_and_detect_change(self):
        self.assertEqual(self.run_cli("create").returncode, 0)
        document = json.loads(self.manifest.read_text())
        self.assertEqual(list(document["files"]), ["nested/hello.txt"])
        self.assertEqual(self.run_cli("verify").returncode, 0)
        (self.root / "nested" / "hello.txt").write_bytes(b"changed\n")
        failed = self.run_cli("verify")
        self.assertEqual(failed.returncode, 1)
        self.assertIn("FAIL nested/hello.txt", failed.stdout)

    def test_missing_file_is_failure(self):
        self.assertEqual(self.run_cli("create").returncode, 0)
        (self.root / "nested" / "hello.txt").unlink()
        self.assertEqual(self.run_cli("verify").returncode, 1)

    def test_reject_parent_traversal(self):
        self.manifest.write_text(json.dumps({
            "algorithm": "sha256", "files": {"../outside": "0" * 64}
        }))
        self.assertEqual(self.run_cli("verify").returncode, 2)

    def test_reject_absolute_path(self):
        self.manifest.write_text(json.dumps({
            "algorithm": "sha256", "files": {"/etc/passwd": "0" * 64}
        }))
        self.assertEqual(self.run_cli("verify").returncode, 2)

    def test_reject_symlink_escape(self):
        outside = self.base / "outside.txt"
        outside.write_bytes(b"outside")
        (self.root / "nested" / "escape").symlink_to(outside)
        self.manifest.write_text(json.dumps({
            "algorithm": "sha256", "files": {"nested/escape": "0" * 64}
        }))
        self.assertEqual(self.run_cli("verify").returncode, 1)

    def test_create_skips_symlinks(self):
        outside = self.base / "outside.txt"
        outside.write_bytes(b"outside")
        (self.root / "escape").symlink_to(outside)
        self.assertEqual(self.run_cli("create").returncode, 0)
        files = json.loads(self.manifest.read_text())["files"]
        self.assertNotIn("escape", files)

    def test_invalid_digest_rejected(self):
        self.manifest.write_text(json.dumps({
            "algorithm": "sha256", "files": {"nested/hello.txt": "not-a-digest"}
        }))
        self.assertEqual(self.run_cli("verify").returncode, 2)


if __name__ == "__main__":
    unittest.main()
