# Filesystem mount diagnostics

A read-only filesystem is different from a permissions error. `sudo` cannot make a read-only mount writable. This lab uses only a disposable directory and does not remount anything.

## Practice on Linux

```bash
(
  set -eu
  d=$(mktemp -d)
  trap 'rm -rf -- "$d"' EXIT
  findmnt -T "$d" -o TARGET,FSTYPE,OPTIONS
  df -h "$d"
  touch "$d/probe"
  test -f "$d/probe"
)
```

`findmnt -T` identifies the mount containing a path. Look for `ro` or `rw` in its comma-separated options. `df -h` reports available space, not write permissions. The probe should succeed on a writable temporary directory. If it fails, stop and inspect the error rather than escalating privileges.

## Troubleshooting a real failure

Inspect the existing parent directory with `findmnt -T . -o TARGET,FSTYPE,OPTIONS`, `pwd`, `id`, `ls -ld .`, and `df -h .`. A permission-denied error can arise from ownership or access controls even on an `rw` mount. A read-only filesystem error indicates a mount or filesystem restriction. A full disk is a separate failure mode.

For WSL, inspect `wsl --status` and `wsl --list --verbose` from Windows PowerShell. Back up important files before repair; do not unregister a distribution or force a remount as a first step.

## Review questions

- Why can an `rw` mount still reject a write?
- Why does `sudo touch` not solve a read-only mount?
- What is the difference between available disk space and mount options?

Record your own observations; this exercise does not claim personal completion.
