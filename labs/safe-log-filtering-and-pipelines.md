# Lab 05: Safe log filtering and shell pipeline exit codes

**Goal:** Practice reading a small, synthetic event log with `grep`, `awk`, and `sort`, while understanding how pipelines can hide failures.

**Environment:** Bash and common GNU/Linux tools (`mktemp`, `printf`, `grep`, `awk`, `sort`). No root access, network access, or real security logs needed.

## 1. Create disposable sample data

```bash
lab_dir=$(mktemp -d) || exit 1
printf '%s\n' \
  'INFO login alice' \
  'WARN retry alice' \
  'ERROR denied bob' \
  'INFO logout alice' \
  'ERROR denied carol' > "$lab_dir/events.log"
cat "$lab_dir/events.log"
```

The log format is deliberately simplified: **severity, action, username**. It is not a parser for production syslog, JSON logs, or arbitrary untrusted log formats.

## 2. Filter and count

Show only errors:

```bash
grep '^ERROR ' "$lab_dir/events.log"
```

Expected lines:

```text
ERROR denied bob
ERROR denied carol
```

Count errors per username (third whitespace-delimited field):

```bash
awk '$1=="ERROR" {count[$3]++} END {for (user in count) print user, count[user]}' "$lab_dir/events.log" | sort
```

Expected output:

```text
bob 1
carol 1
```

This exercise uses exact field matching in `awk`, rather than assuming every occurrence of the word ERROR is a severity label.

## 3. Understand exit statuses

A successful command generally exits with status `0`. `grep` returns `1` when no lines match; this is **not** the same as an I/O error (typically status `2`).

```bash
grep '^CRITICAL ' "$lab_dir/events.log"
printf 'grep exit status: %s\n' "$?"
```

Expected status: `1`.

Without `pipefail`, Bash reports the last command's exit status for a pipeline. Compare:

```bash
( grep '^ERROR ' "$lab_dir/does-not-exist" | sort >/dev/null; printf 'default pipeline status: %s\n' "$?" )
( set -o pipefail; grep '^ERROR ' "$lab_dir/does-not-exist" | sort >/dev/null; printf 'pipefail status: %s\n' "$?" )
```

Expected: the default pipeline reports `0` because `sort` succeeds despite `grep` failing; the `pipefail` pipeline reports nonzero. The exact nonzero code can vary by command and error. Both examples intentionally read a nonexistent file.

**Important:** `set -e` is not a complete error-handling strategy; its behavior depends on shell context. Check critical commands explicitly, and consider `set -o pipefail` in Bash scripts.

## 4. Review questions

1. Why is `grep '^ERROR '` more specific than `grep ERROR`?
2. What happens to `awk` field numbers if a username contains whitespace?
3. Why could a pipeline appear successful even if an earlier command failed?
4. Why should security scripts use a documented log schema rather than assume every log uses whitespace-separated fields?

## 5. Cleanup

```bash
rm -r -- "$lab_dir"
```

Only run cleanup if `lab_dir` still points to the temporary directory created in step 1. Never use an unreviewed variable in a removal command.

**References:** `man 1 grep`, `man 1 awk`, `man 1 sort`, `help set` (Bash), and the [GNU Bash pipeline documentation](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html).

**Scope:** These commands analyze synthetic local data. They do not establish that any real host was investigated or secured.
