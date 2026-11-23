# Lab 11 — Safe Temporary Workspaces and Cleanup

## Goal

Learn to create private, unpredictable temporary directories, keep shell variables quoted, and clean up reliably when a script exits. This is an offline lab for a disposable Linux shell with GNU `mktemp` and Bash.

## Why predictable names are unsafe

Avoid patterns such as `/tmp/my-script-$$`, `/tmp/report.txt`, or `/tmp/file-$RANDOM` for security-sensitive temporary work. In shared directories, another local user may anticipate names and interfere with files. `mktemp` creates the destination atomically rather than checking for a free name and then creating it.

## Run the experiment

Copy the following into `safe-temp-lab.sh` and run `bash safe-temp-lab.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Affect this shell process; newly created files should not be world-readable.
umask 077

# Use a random, atomically created private directory in the system temp area.
workdir=$(mktemp -d)
cleanup() {
  # Be defensive: only clean up the directory this script created.
  if [[ -n ${workdir:-} && -d $workdir ]]; then
    rm -rf -- "$workdir"
  fi
}
trap cleanup EXIT

printf 'training data\n' > "$workdir/input.txt"
cp -- "$workdir/input.txt" "$workdir/output.txt"
printf 'Workdir permissions: '
stat -c '%a' -- "$workdir"
printf 'Content: '
cat -- "$workdir/output.txt"
printf 'Temporary workspace will be removed when this script exits.\n'
```

Expected: a directory mode of `700` and the content `training data`. The exact temporary name is intentionally different every run. After successful exit, the trap deletes the workspace. Only run the sample on a machine you control; don't use this cleanup pattern on a path provided by another user.

## Why each line matters

- `umask 077` removes access for group and other users from newly created files unless permissions are deliberately changed.
- `mktemp -d` creates an unpredictable directory atomically. Its output should be captured and quoted.
- `trap cleanup EXIT` runs cleanup for normal exit and many error exits; it does **not** run after `SIGKILL`, a power failure, or a machine crash.
- `rm -rf -- "$workdir"` removes the **created** workspace. Never substitute an unchecked, user-controlled pathname.
- `set -euo pipefail` helps catch errors, unset variables, and failing pipeline components; it does not replace careful error handling.

## Optional exploration

Try `umask` in the shell and compare `stat -c '%a' file` on files created under different umasks. For a temporary *file*, GNU `mktemp` (without `-d`) can create a private file instead. Avoid storing credentials in temporary files unless absolutely necessary, and remember that file permissions alone do not protect data from privileged processes.

## Review questions

1. Why is `mktemp -d` preferable to writing to a fixed name under `/tmp`?
2. What could go wrong if `"$workdir"` were not quoted?
3. Which circumstances prevent an `EXIT` trap from running?
4. Why is an empty or externally supplied cleanup path dangerous?
5. What security guarantee does `umask 077` provide, and what does it **not** provide?

## References

- GNU Coreutils: [mktemp invocation](https://www.gnu.org/software/coreutils/manual/html_node/mktemp-invocation.html)
- GNU Bash: [Bourne shell builtins — trap](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html)
- GNU Coreutils: [umask invocation](https://www.gnu.org/software/coreutils/manual/html_node/umask-invocation.html)

**Safety:** This lab is about local defensive practices. Do not run cleanup commands against shared or untrusted paths.
