# Lab 12 — Inodes, Hard Links, and Symbolic Links

## Objectives

Distinguish a **directory entry** from an **inode**, compare hard links and symbolic links, and inspect paths without modifying anything outside a disposable directory. Requires Bash and GNU coreutils (`stat`, `ln`, `readlink`, `mktemp`).

## Mental model

A Linux filename is a directory entry pointing to an inode. An inode holds metadata and references file data. Two hard links can refer to the same inode. A symbolic link is a separate filesystem object containing a pathname; that pathname may become invalid. Hard links to directories are normally disallowed, and hard links cannot cross filesystem boundaries.

## Safe experiment

Paste into `links-lab.sh` and run `bash links-lab.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
umask 077
workdir=$(mktemp -d)
trap 'rm -rf -- "$workdir"' EXIT

printf 'first\n' > "$workdir/original"
ln -- "$workdir/original" "$workdir/hardlink"
ln -s -- original "$workdir/symlink"

printf '\nInodes and link counts (symlink shown as its own inode):\n'
stat -c '%i %h %n' -- "$workdir/original" "$workdir/hardlink" "$workdir/symlink"
printf '\nSymlink target: '
readlink -- "$workdir/symlink"

printf '\nAppend through the hard link:\n'
printf 'second\n' >> "$workdir/hardlink"
cat -- "$workdir/original"

printf '\nRemove the original directory entry:\n'
rm -- "$workdir/original"
printf 'Hard link still works: '
cat -- "$workdir/hardlink"
if [[ -L "$workdir/symlink" && ! -e "$workdir/symlink" ]]; then
    printf 'Symbolic link is now dangling.\n'
fi
```

Expected observations:
- `original` and `hardlink` initially share an inode number and show a link count of 2. `symlink` has a different inode number.
- Appending via `hardlink` changes content read through `original`, since both names refer to the same file.
- Removing `original` does **not** remove the file data while `hardlink` remains.
- The relative symlink `symlink -> original` becomes dangling after `original` is removed.

The inode numbers and temporary path will vary. The script exits and removes only the directory it created.

## Security relevance

- A pathname can be swapped for a symlink. When verifying or opening security-sensitive files, checking only whether the final resolved pathname stays inside a root does not enforce a **no-symlinks** policy.
- A relative symlink is resolved relative to its parent directory, **not** the current working directory.
- Hard links share the same inode: modifying one name changes what is visible through all other hard links.
- `stat` reports metadata about the link itself by default in GNU coreutils; `stat -L` follows symbolic links.
- Checks followed later by file opens can suffer from time-of-check/time-of-use (TOCTOU) races. Merely validating paths in shell scripts is not a complete security boundary.

## Mini challenges

1. What happens to the hard-link count after removing `original`?
2. How would you inspect where a symbolic link points without following it?
3. Why can `cat "$workdir/symlink"` fail after removing `original`?
4. Can you create a hard link to a file on another filesystem? Why not?
5. Would a content hash alone detect replacing a regular file with a symlink pointing to identical bytes?

## References

- [GNU Coreutils: ln invocation](https://www.gnu.org/software/coreutils/manual/html_node/ln-invocation.html)
- [GNU Coreutils: stat invocation](https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html)
- [Linux manual: symlink(7)](https://man7.org/linux/man-pages/man7/symlink.7.html)

**Safety:** Run only on files you created. Never use privileged commands or make links into another user's directories for this lab.
