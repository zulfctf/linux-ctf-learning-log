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

    def run_cli(self, action, *options):
        return subprocess.run(
            [sys.executable, str(SCRIPT), action, str(self.root), str(self.manifest), *options],
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

    def test_reject_symlink_to_file_inside_root(self):
        self.assertEqual(self.run_cli("create").returncode, 0)
        source = self.root / "nested" / "hello.txt"
        source.rename(self.root / "original.txt")
        source.symlink_to(self.root / "original.txt")
        result = self.run_cli("verify")
        self.assertEqual(result.returncode, 1)
        self.assertIn("symlink not allowed", result.stdout)

    def test_reject_symlink_in_parent_directory(self):
        self.assertEqual(self.run_cli("create").returncode, 0)
        (self.root / "nested").rename(self.root / "real")
        (self.root / "nested").symlink_to(self.root / "real", target_is_directory=True)
        result = self.run_cli("verify")
        self.assertEqual(result.returncode, 1)
        self.assertIn("symlink not allowed", result.stdout)

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


    def test_strict_flags_untracked_file_without_changing_default(self):
        self.assertEqual(self.run_cli("create").returncode, 0)
        (self.root / "new.txt").write_text("new data", encoding="utf-8")
        self.assertEqual(self.run_cli("verify").returncode, 0)
        checked = self.run_cli("verify", "--strict")
        self.assertEqual(checked.returncode, 1)
        self.assertIn("FAIL untracked file: new.txt", checked.stdout)

    def test_strict_excludes_manifest_and_symlinks(self):
        self.manifest = self.root / "manifest.json"
        self.assertEqual(self.run_cli("create").returncode, 0)
        (self.root / "link").symlink_to(self.root / "nested" / "hello.txt")
        checked = self.run_cli("verify", "--strict")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertNotIn("untracked file", checked.stdout)

    def test_strict_detects_new_nested_file(self):
        self.assertEqual(self.run_cli("create").returncode, 0)
        (self.root / "nested" / "second.txt").write_text("extra", encoding="utf-8")
        checked = self.run_cli("verify", "--strict")
        self.assertEqual(checked.returncode, 1)
        self.assertIn("nested/second.txt", checked.stdout)

    def test_reject_noncanonical_paths(self):
        for name in ("nested//hello.txt", "./nested/hello.txt", "nested/../hello.txt", "nested\\\\hello.txt"):
            with self.subTest(name=name):
                self.manifest.write_text(json.dumps({
                    "algorithm": "sha256", "files": {name: "0" * 64}
                }))
                self.assertEqual(self.run_cli("verify").returncode, 2)

    def test_reject_unsupported_algorithm(self):
        self.manifest.write_text(json.dumps({
            "algorithm": "md5", "files": {"nested/hello.txt": "0" * 64}
        }))
        self.assertEqual(self.run_cli("verify").returncode, 2)

    def test_create_skips_manifest_inside_root(self):
        self.manifest = self.root / "manifest.json"
        self.assertEqual(self.run_cli("create").returncode, 0)
        document = json.loads(self.manifest.read_text())
        self.assertNotIn("manifest.json", document["files"])
        self.assertEqual(self.run_cli("verify").returncode, 0)

    def test_detects_empty_manifest_without_crashing(self):
        self.manifest.write_text(json.dumps({"algorithm": "sha256", "files": {}}))
        result = self.run_cli("verify")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Verified 0 entries", result.stdout)


if __name__ == "__main__":
    unittest.main()
