# Lab 01: Linux file permissions

**Goal:** inspect and change permissions on files you own, understand the owner/group/other model, and distinguish file permissions from directory permissions.

**Environment:** a local Linux VM or container with a non-root user. Never run these commands on production files or folders.

## Setup

```bash
mkdir -p "$HOME/ctf-permissions-lab"
cd "$HOME/ctf-permissions-lab"
printf 'lab-only\n' > sample.txt
mkdir -p private
```

## 1. Read permission metadata

```bash
ls -ld . private sample.txt
stat -c '%a %A %U:%G %n' sample.txt private
id
```

The leading character of the long listing indicates file type (e.g. `-` for regular file, `d` for directory). The next nine characters form three `rwx` triples for owner, group, and others. A mode such as `640` means owner read/write (6), group read (4), and others no access (0).

## 2. Change a file mode

```bash
chmod 640 sample.txt
stat -c '%a %A %n' sample.txt
chmod u+x sample.txt
stat -c '%a %A %n' sample.txt
chmod u-x sample.txt
```

Observe that `u+x` changes only the owner's execute bit. A text file does not need to be executable simply to be read.

## 3. Compare directory permissions

```bash
chmod 700 private
stat -c '%a %A %n' private
printf 'inside\n' > private/example.txt
ls -l private
```

On directories, `x` permits traversal/search, `r` permits listing names, and `w` (with `x`) permits adding/removing entries. File permissions and parent-directory permissions jointly affect access.

## 4. Understand ownership without modifying it

```bash
ls -l sample.txt
id -gn
```

`chown` changes ownership, but typically requires sufficient privileges; do **not** run `sudo chown` as part of this beginner lab. Use `chown --help` to inspect its syntax.

## Check your understanding

1. What does `chmod 600 sample.txt` permit?
2. Why might a user be unable to read `private/example.txt` even if that file itself is world-readable?
3. Why is `chmod -R 777` an unsafe default?

<details>
<summary>Answers</summary>

1. The owner may read and write; group and others get no permissions.
2. A parent directory may not grant execute/traversal access.
3. It grants broad read, write, and execute/traversal access, including to unintended users.

</details>

## Cleanup

```bash
rm -r -- "$HOME/ctf-permissions-lab"
```

Only run cleanup if this is **your** lab folder and it contains no files you want to keep.
