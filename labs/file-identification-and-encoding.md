# Lab 02: File identification, encoding, and compression

**Goal:** choose the next command from evidence about a file's contents instead of guessing from its extension.

**Requirements:** `file`, `xxd` (or `od`), `base64`, `gzip`, `tar`, and a shell. Work only with files generated below.

## Set up a throwaway working directory

```bash
mkdir -p "$HOME/ctf-format-lab"
cd "$HOME/ctf-format-lab"
printf 'hello from the lab\n' > message.txt
base64 message.txt > message.b64
gzip -c message.txt > message.gz
tar -cf archive.tar message.txt
```

## Examine first, transform second

```bash
file message.txt message.b64 message.gz archive.tar
xxd -l 32 message.gz
head -c 80 message.b64; printf '\n'
```

Expected general observations:
- `message.txt` contains ordinary text.
- `message.b64` is printable text representing the bytes of `message.txt`. The `file` command may identify it only as ASCII text; it cannot always determine that text is Base64.
- `message.gz` is gzip-compressed data, often beginning with hexadecimal bytes `1f 8b`.
- `archive.tar` is an archive container, not necessarily compressed.

Do not rely on filename extensions alone: they can be arbitrary or misleading.

## Decode vs decompress vs extract

```bash
base64 -d message.b64 > decoded.txt
gzip -dc message.gz > decompressed.txt
tar -tf archive.tar
```

`base64 -d` reverses an encoding. `gzip -dc` decompresses gzip data to stdout. `tar -tf` lists archive entries without extracting them.

Validate exact outcomes:

```bash
cmp message.txt decoded.txt
cmp message.txt decompressed.txt
```

Both `cmp` commands should exit with status 0 (no differences).

## Reasoning questions

1. Why is a file named `payload.txt` not guaranteed to be plain text?
2. Why might Base64 decoding a random binary file produce an error or useless output?
3. What is the difference between `tar -tf archive.tar` and `tar -xf archive.tar`?
4. Which inspection command would you use before opening an unfamiliar downloaded archive?

<details>
<summary>Suggested answers</summary>

1. Extensions are names, not trustworthy content metadata.
2. Binary data is not necessarily valid Base64 text, and decoding the wrong representation cannot reveal a meaningful format.
3. `-t` lists members; `-x` extracts them.
4. Start with `file` and inspect the archive listing before extracting in a controlled directory.

</details>

## Safety note

Untrusted archives can contain malicious paths or other dangerous content. Do not extract unknown archives directly into sensitive directories. This lab uses only files you created yourself.

## Cleanup

```bash
rm -r -- "$HOME/ctf-format-lab"
```

Confirm that the path is your disposable lab directory before deleting it.

## Related note

See [Compression vs Encoding](../notes/compression-vs-encoding.md) for the original learning note.
