# Lab 06: Safe shell quoting and unusual filenames

**Goal:** Learn why whitespace, leading dashes, and newline characters in filenames can break naive shell commands, and how to process paths without losing their boundaries.

**Environment:** Bash on Linux with GNU `find`, `xargs`, `sha256sum`, and Python 3. No root privileges or network required. Work only in a disposable directory.

## 1. Create a controlled sample

Run this in Bash:

```bash
lab_dir=$(mktemp -d) || exit 1
printf 'alpha\n' > "$lab_dir/report one.txt"
printf 'beta\n' > "$lab_dir/-leading-dash.txt"
printf 'gamma\n' > "$lab_dir/line
break.txt"
printf 'Created sample files in %s\n' "$lab_dir"
```

The third filename contains a **literal newline**. It is valid on Linux; a filename cannot contain a NUL byte or `/` within a single component.

## 2. Quote variables and delimit option arguments

```bash
cat -- "$lab_dir/report one.txt"
cat -- "$lab_dir/-leading-dash.txt"
```

Quoting `"$lab_dir/..." ` preserves spaces and newlines as part of one argument. The `--` delimiter tells many GNU tools to stop interpreting subsequent arguments as options. It is not supported by every command; consult its help or manual.

Do **not** use `for file in $(find ...)`: command substitution and word splitting corrupt paths with whitespace, and filenames can contain glob characters too.

## 3. Process filenames using NUL delimiters

```bash
find "$lab_dir" -maxdepth 1 -type f -print0 |
  xargs -0 -r sha256sum --
```

`find -print0` separates pathnames with NUL, which cannot appear inside a Linux filename. GNU `xargs -0` reads those exact boundaries. `-r` avoids running `sha256sum` if no files are found. Hash output for the filename containing a newline may use escaped display formatting; it is **not** a newline-delimited machine-readable list.

For robust machine-readable processing, use `sha256sum -z` (GNU coreutils) or handle filenames as bytes in Python.

## 4. Verify all three paths safely

```bash
python3 - "$lab_dir" <<'PY'
import os
import sys

root = os.fsencode(sys.argv[1])
names = os.listdir(root)
assert len(names) == 3, names
assert b"report one.txt" in names
assert b"-leading-dash.txt" in names
assert b"line\nbreak.txt" in names
print("PASS: three distinct filenames preserved")
PY
```

This check does not claim that a remote system was inspected. It only verifies the local sample data.

## 5. Review questions

1. Why is `"$file"` safer than `$file` in Bash?
2. Why is newline-separated `find` output unsuitable as a universal pathname protocol?
3. What is the purpose of `--` and why should you check whether a command supports it?
4. What is the difference between `find -print0` and `xargs -0`?

## 6. Cleanup

```bash
# First verify this variable still points to your disposable lab directory.
printf 'About to remove: %q\n' "$lab_dir"
rm -r -- "$lab_dir"
```

Never run the cleanup with an empty, unset, or untrusted directory variable. Do not reuse it for real files.

**References:** [GNU findutils: Unusual File Names](https://www.gnu.org/software/findutils/manual/html_node/find_html/Unusual-Characters-in-File-Names.html), [GNU coreutils: sha2 utilities](https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html), and [GNU Bash: Quoting](https://www.gnu.org/software/bash/manual/html_node/Quoting.html).

**Security takeaway:** Pathnames are data, not shell syntax. Avoid constructing shell commands from untrusted filenames, and prefer argument arrays or NUL-delimited interfaces when handling arbitrary local paths.
