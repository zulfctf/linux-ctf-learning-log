# Lab 04: SHA-256 checksums and file integrity

**Objective:** Detect accidental or unexpected changes to a file using a cryptographic hash. This exercise uses only disposable local files.

**Requirements:** Linux shell, `sha256sum`, `printf`, `cp`, `cmp`, `mkdir`. No administrator access or network connection required.

## 1. Create a baseline

```bash
mkdir -p "$HOME/ctf-integrity-lab"
cd "$HOME/ctf-integrity-lab" || exit 1
printf 'configuration=secure\n' > config.txt
sha256sum config.txt
sha256sum config.txt > SHA256SUMS
cat SHA256SUMS
```

A SHA-256 digest is a 256-bit fingerprint, conventionally displayed as 64 hexadecimal characters. Identical bytes yield identical digests. A digest is not encryption: it does not conceal the file.

## 2. Verify the unchanged file

```bash
sha256sum -c SHA256SUMS
```

Expected output includes `config.txt: OK`. The check compares the file's current digest against the recorded digest.

## 3. Detect a modification

```bash
cp config.txt config.original.txt
printf 'configuration=changed\n' > config.txt
sha256sum -c SHA256SUMS
```

Expected: `config.txt: FAILED` and a nonzero exit status. This failure is intentional. To capture the status without losing it to another command:

```bash
sha256sum -c SHA256SUMS
result=$?
printf 'Verification exit status: %s\n' "$result"
```

Restore the original file and verify again:

```bash
cp config.original.txt config.txt
sha256sum -c SHA256SUMS
cmp config.txt config.original.txt
```

Both final commands should succeed.

## 4. Think like an analyst

1. Why does a hash change when even one byte changes?
2. Can a checksum alone prove who created a downloaded file?
3. What happens if an attacker replaces both the file **and** its `SHA256SUMS` entry?
4. When is `cmp` useful compared with `sha256sum`?

<details>
<summary>Answer guide</summary>

1. Cryptographic hash functions are designed so small input changes produce unpredictable digest changes (the avalanche effect).
2. No. A hash establishes byte-for-byte consistency with a **trusted** reference, not authorship.
3. Verification can pass against the attacker-controlled reference. Obtain expected hashes over a separately trusted channel, or use a verified digital signature.
4. `cmp` directly compares two available files; a trusted checksum is useful when the original file is not present.

</details>

## Security considerations

- SHA-256 is useful for integrity checks but is **not** a password-storage scheme.
- A published checksum on the same compromised page as a malicious download is not an independent trust anchor.
- A checksum file contains paths. Review untrusted manifests before using `sha256sum -c` and work inside a disposable directory.
- Digital signatures can authenticate a publisher when the signing key is independently trusted; a plain hash cannot.

## Cleanup

```bash
cd "$HOME" || exit 1
rm -r -- "$HOME/ctf-integrity-lab"
```

Only remove the folder if you created it for this exercise and no longer need its contents.

**References:** `man 1 sha256sum`, `man 1 cmp`; [GNU Coreutils: sha2 utilities](https://www.gnu.org/software/coreutils/manual/html_node/sha2-utilities.html).
