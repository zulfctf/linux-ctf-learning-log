#!/usr/bin/env python3
"""Create and verify SHA-256 manifests for files in a local directory.

Uses only the Python standard library. No network calls or elevated privileges.
Manifest paths are relative POSIX paths and the manifest is JSON for unambiguous
filename handling. Never treat an untrusted manifest as an authentication proof.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys

CHUNK_SIZE = 1024 * 1024


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_relative(name: str) -> Path:
    """Reject absolute paths, traversal, and noncanonical path components."""
    p = PurePosixPath(name)
    if (not name or "\\" in name or p.is_absolute() or
            any(part in ("", ".", "..") for part in name.split("/")) or
            str(p) != name):
        raise ValueError(f"unsafe manifest path: {name!r}")
    return Path(*p.parts)


def confined_regular_file(root: Path, rel: Path) -> Path:
    """Resolve symlinks and refuse paths that escape the chosen root."""
    candidate = root / rel
    # Manifest creation excludes symlinks. Apply the same policy when
    # verifying, including symlinks in intermediate directory components.
    # Otherwise a file could be replaced by a link after the baseline was made.
    part_path = root
    for part in rel.parts:
        part_path = part_path / part
        if part_path.is_symlink():
            raise ValueError(f"symlink not allowed: {rel.as_posix()}")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError(f"path escapes root: {rel.as_posix()}")
    if not resolved.is_file():
        raise ValueError(f"not a regular file: {rel.as_posix()}")
    return resolved


def create(root: Path, manifest: Path) -> int:
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    entries = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(base) / d).is_symlink())
        for name in sorted(files):
            path = Path(base) / name
            rel = path.relative_to(root)
            if path.is_symlink() or path.resolve() == manifest:
                continue
            if not path.is_file():
                continue
            entries[rel.as_posix()] = digest(path)
    # Manifest is written only after scanning; the caller chooses its location.
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"algorithm": "sha256", "files": entries},
                                   indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Recorded {len(entries)} files in {manifest}")
    return 0


def verify(root: Path, manifest: Path, strict: bool = False) -> int:
    document = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("algorithm") != "sha256":
        raise ValueError("unsupported manifest format or algorithm")
    entries = document.get("files")
    if not isinstance(entries, dict):
        raise ValueError("manifest files must be an object")
    failures = 0
    for name, expected in sorted(entries.items()):
        if not isinstance(name, str) or not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise ValueError(f"invalid manifest entry: {name!r}")
        rel = safe_relative(name)
        try:
            actual = digest(confined_regular_file(root, rel))
        except (OSError, ValueError) as exc:
            print(f"FAIL {name}: {exc}")
            failures += 1
            continue
        ok = actual == expected
        print(f"{'OK  ' if ok else 'FAIL'} {name}")
        failures += not ok
    if strict:
        # Compare a fresh snapshot with recorded paths. Use the same symlink
        # policy as creation, and never include the manifest itself.
        current = set()
        for base, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not (Path(base) / d).is_symlink())
            for filename in files:
                path = Path(base) / filename
                if path.is_symlink() or not path.is_file() or path.resolve() == manifest:
                    continue
                current.add(path.relative_to(root).as_posix())
        for extra in sorted(current - entries.keys()):
            print(f"FAIL untracked file: {extra}")
            failures += 1
    print(f"Verified {len(entries)} entries; {failures} failures")
    return 1 if failures else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create", "verify"])
    parser.add_argument("root", type=Path, help="directory to inspect")
    parser.add_argument("manifest", type=Path, help="JSON manifest path")
    parser.add_argument("--strict", action="store_true", help="also fail on files not listed in the manifest when verifying")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        manifest = args.manifest.resolve()
        if not root.is_dir():
            raise ValueError("root must be a directory")
        return create(root, manifest) if args.action == "create" else verify(root, manifest, strict=args.strict)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
