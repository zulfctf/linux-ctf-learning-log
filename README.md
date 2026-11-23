# Linux & CTF Learning Log

A collection of Linux fundamentals, safe hands-on labs, and beginner CTF learning notes.

The goal is to document concepts, common pitfalls, and repeatable practice exercises — not to publish challenge flags or imply exercises were completed when they have not been verified.

## Practical labs

| Lab | What it covers |
| --- | --- |
| [01 — File permissions](labs/linux-file-permissions.md) | `chmod`, ownership, directory traversal, permission checks |
| [02 — File identification and encoding](labs/file-identification-and-encoding.md) | `file`, `xxd`, Base64, gzip, tar, format-first investigation |
| [03 — Process inspection and signals](labs/process-inspection-and-signals.md) | `ps`, PIDs, process states, `SIGTERM`, safe cleanup |
| [04 — SHA-256 integrity checks](labs/checksums-and-integrity.md) | `sha256sum`, trusted baselines, tamper detection, checksum limitations |
| [05 — Safe log filtering and pipelines](labs/safe-log-filtering-and-pipelines.md) | `grep`, `awk`, synthetic logs, Bash `pipefail`, and failure detection |
| [06 — Safe shell quoting and filenames](labs/safe-shell-quoting-and-filenames.md) | Quoting, leading dashes, newline filenames, `find -print0`, and `xargs -0` |
| [07 — Loopback TCP and listening sockets](labs/loopback-tcp-and-listening-sockets.md) | Local TCP endpoints, ephemeral ports, Python sockets, and `ss -ltn` |
| [08 — Standard streams and redirection](labs/standard-streams-and-redirection.md) | stdout/stderr, file descriptors, redirection order, and exit statuses |
| [09 — Hostname resolution and local resolver](labs/hostname-resolution-and-local-resolver.md) | `localhost`, `getaddrinfo`, `getent`, NSS vs DNS, loopback checks |
| [10 — SSH host-key verification](labs/ssh-host-key-verification.md) | Offline Ed25519 fingerprints, `known_hosts`, changed keys, trust on first use |
| [11 — Safe temporary workspaces](labs/safe-temporary-workspaces.md) | `mktemp -d`, restrictive `umask`, quoted paths, and `trap` cleanup |

## Executable tools and tests

- [SHA-256 integrity manifest CLI](tools/integrity_manifest.py) — create and verify JSON manifests for files in a local directory using Python's standard library.
- [CLI regression tests](tests/test_integrity_manifest.py) — check intact/modified/missing files, invalid manifests, and path traversal protections.

Requires **Python 3.9+**. Try it with a disposable directory:

```bash
mkdir -p /tmp/ctf-manifest-demo
printf 'hello\n' > /tmp/ctf-manifest-demo/hello.txt
python3 tools/integrity_manifest.py create /tmp/ctf-manifest-demo /tmp/ctf-manifest.json
python3 tools/integrity_manifest.py verify /tmp/ctf-manifest-demo /tmp/ctf-manifest.json
python3 -m unittest discover -s tests -v
```

The manifest records the hashes of files present when it was created. Verification checks those recorded entries; by default it **does not detect newly added files**. Add `--strict` to `verify` to also flag unexpected regular files. Symlinks are excluded from manifest creation, and verification rejects symlink substitutions and paths that escape the selected root. This is a learning tool, not a substitute for a signed, trusted manifest or a production-grade file integrity monitor. Tests are supplied but execution results should be recorded only after running them.

## Concept notes

- [Compression vs Encoding](notes/compression-vs-encoding.md) — why Base64 differs from compression and how to inspect unfamiliar files.

## How to use the labs

1. Open a lab and read its prerequisites and safety notes.
2. Use a disposable Linux VM, container, or personal practice environment.
3. Run commands only against files and processes you own.
4. Compare the observed behavior with the explanation and answer the review questions.
5. Keep your own learning log of what you tested, including mistakes and corrections.

## Learning roadmap

- **Foundations:** navigation, files, permissions, processes, redirection, and pipes.
- **Formats and tooling:** encoding, compression, archives, and hashing.
- **Networking and security:** sockets, DNS, logs, SSH hardening, and least privilege.
- **CTF skills:** controlled enumeration, evidence tracking, and reasoning from system output.

## Safety and contribution standards

- Work only on systems you own or are authorized to test.
- Avoid destructive commands and never paste unknown shell scripts without reviewing them.
- Keep examples reproducible and explain what each command does.
- Don't add fabricated challenge completions or meaningless commits merely to increase contribution counts.
