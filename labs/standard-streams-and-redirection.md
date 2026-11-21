# Lab 08: Standard streams, redirection, and safe error capture

**Goal:** Distinguish standard input (file descriptor 0), standard output (1), and standard error (2), and learn why the order of shell redirections matters when collecting evidence.

**Environment:** Bash, Python 3, and a disposable directory. No root privileges, network access, or real system logs required.

## 1. Create a controlled example

Run these commands in **Bash**:

```bash
lab_dir=$(mktemp -d) || exit 1
python3 -c 'import sys; print("RESULT", flush=True); print("WARNING", file=sys.stderr, flush=True)'
```

The example writes `RESULT` to stdout and `WARNING` to stderr. Both normally appear on the terminal, but they are separate streams. Their relative display order is not a reliable way to identify the stream.

## 2. Capture stdout and stderr separately

```bash
python3 -c 'import sys; print("RESULT"); print("WARNING", file=sys.stderr)' \
  > "$lab_dir/stdout.txt" 2> "$lab_dir/stderr.txt"
printf 'stdout: '; cat -- "$lab_dir/stdout.txt"
printf 'stderr: '; cat -- "$lab_dir/stderr.txt"
```

Expected output:

```text
stdout: RESULT
stderr: WARNING
```

`>` redirects file descriptor 1 and `2>` redirects descriptor 2. Redirection targets are created or truncated: **do not point them at valuable files**.

## 3. Redirection order changes the result

Run the two commands below. Both create a new file in the disposable directory.

```bash
python3 -c 'import sys; print("RESULT"); print("WARNING", file=sys.stderr)' \
  > "$lab_dir/combined.txt" 2>&1
python3 -c 'import sys; print("RESULT"); print("WARNING", file=sys.stderr)' \
  2>&1 > "$lab_dir/stdout-only.txt"
```

In the **first** command, stdout goes to `combined.txt`, then stderr is duplicated to the *current* stdout destination (the file). Both lines end up in that file, although their order is not guaranteed.

In the **second** command, stderr is first duplicated to the terminal's original stdout destination, and only then stdout is sent to `stdout-only.txt`. Thus `WARNING` remains visible in the terminal and only `RESULT` goes into the file. The syntax `2>&1` is a descriptor duplication, **not** a request to merge streams retroactively.

Verify the files without relying on display ordering:

```bash
python3 - "$lab_dir" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
assert set((root / "combined.txt").read_text().splitlines()) == {"RESULT", "WARNING"}
assert (root / "stdout-only.txt").read_text().splitlines() == ["RESULT"]
assert (root / "stdout.txt").read_text().splitlines() == ["RESULT"]
assert (root / "stderr.txt").read_text().splitlines() == ["WARNING"]
print("PASS: stdout, stderr, and redirection order verified")
PY
```

## 4. Capture a failure status as well as error text

```bash
python3 -c 'import sys; print("synthetic failure", file=sys.stderr); sys.exit(7)' \
  > "$lab_dir/failure.out" 2> "$lab_dir/failure.err"
status=$?
printf 'Exit status: %s\n' "$status"
cat -- "$lab_dir/failure.err"
```

Expected: exit status `7` and the message `synthetic failure`. A command can print an error message yet exit zero, or exit nonzero without printing anything. **Capture the exit status immediately**; `$?` changes after the next command. If your shell has `set -e` enabled, run this example in a subshell with `set +e` or use an `if` statement to prevent intentional failure from aborting the session.

For pipelines, see [Lab 05](safe-log-filtering-and-pipelines.md) on `pipefail`: without it, the pipeline's exit status generally reflects only the last command.

## 5. Questions and cleanup

1. Which descriptor does `2>` redirect?
2. Why are `>file 2>&1` and `2>&1 >file` different?
3. Why should an investigation record exit codes *and* captured output?
4. What could happen if a redirect target names an existing important file?

Check the path before cleanup, then remove **only** the disposable directory:

```bash
printf 'Disposable directory: %q\n' "$lab_dir"
# Run only after verifying the printed path.
rm -r -- "$lab_dir"
```

**Safety:** All messages are synthetic. This exercise does not inspect or modify security settings or other users' files. Redirection can overwrite files; choose new paths in a directory you own.

**References:** [GNU Bash redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html), [GNU Bash exit status](https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html), and `man 1 bash`.
