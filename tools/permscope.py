"""Read-only POSIX permission audit for a directory you control.

Usage: python3 tools/permscope.py PATH
       python3 tools/permscope.py --self-test
Exit: 0 no findings, 1 findings, 2 scan error.
Checks world-writable regular files/directories and broadly readable .pem/.key
files (heuristic, not proof of secret exposure). Symlinks are skipped.
Use on a stable local tree; this is not a race-safe filesystem sandbox.
"""
import argparse
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path


def audit(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("root must be a real directory")
    findings = []

    def check(path):
        mode = path.lstat().st_mode
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            return
        relative = str(path.relative_to(root))
        if mode & stat.S_IWOTH and not (
            stat.S_ISDIR(mode) and mode & stat.S_ISVTX
        ):
            findings.append({"path": relative, "rule": "world-writable"})
        if stat.S_ISREG(mode) and path.suffix.lower() in (".pem", ".key"):
            if mode & (stat.S_IRGRP | stat.S_IROTH):
                findings.append({"path": relative, "rule": "key-like-file-readable"})

    def fail(error):
        raise error

    check(root)
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=fail):
        dirs.sort()
        for name in sorted(dirs + files):
            check(Path(directory) / name)
    return findings


class Tests(unittest.TestCase):
    def test_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "config"
            p.touch()
            p.chmod(0o666)
            self.assertEqual(audit(root), [{"path": "config", "rule": "world-writable"}])
            p.chmod(0o600)
            self.assertEqual(audit(root), [])

    def test_key_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "demo.key"
            p.touch()
            p.chmod(0o644)
            (root / "alias").symlink_to(p)
            self.assertEqual(audit(root), [{"path": "demo.key", "rule": "key-like-file-readable"}])

    def test_sticky_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root.chmod(0o1777)
            self.assertEqual(audit(root), [])
            root.chmod(0o700)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return 0 if unittest.TextTestRunner().run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        ).wasSuccessful() else 2
    if args.path is None:
        parser.error("PATH required")
    try:
        findings = audit(args.path)
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(findings, indent=2))
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
