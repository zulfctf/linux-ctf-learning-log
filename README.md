# Linux & CTF Learning Log

A collection of Linux fundamentals, safe hands-on labs, and beginner CTF learning notes.

The goal is to document concepts, common pitfalls, and repeatable practice exercises — not to publish challenge flags or imply exercises were completed when they have not been verified.

## Practical labs

| Lab | What it covers |
| --- | --- |
| [01 — File permissions](labs/linux-file-permissions.md) | `chmod`, ownership, directory traversal, permission checks |
| [02 — File identification and encoding](labs/file-identification-and-encoding.md) | `file`, `xxd`, Base64, gzip, tar, format-first investigation |
| [03 — Process inspection and signals](labs/process-inspection-and-signals.md) | `ps`, PIDs, process states, `SIGTERM`, safe cleanup |

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
