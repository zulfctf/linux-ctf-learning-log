# Lab 10 — SSH host-key verification and known_hosts (offline)

**Goal:** understand why SSH checks a server's *host key* before trusting the connection, without connecting to any network host.

## Safety and prerequisites

Use a local Linux shell with `ssh-keygen` (OpenSSH). This lab creates a disposable **host-key simulation**, not a user login key. Never replace your real `~/.ssh/known_hosts`, accept an unexpected key change automatically, or copy a fingerprint from the same untrusted channel as a suspicious connection.

## Build a disposable host-key record

```bash
lab=$(mktemp -d)
# Run in a disposable lab directory; keep all generated material there.
ssh-keygen -q -t ed25519 -N '' -f "$lab/host_ed25519"
printf 'training.example.invalid ' > "$lab/known_hosts"
cat "$lab/host_ed25519.pub" >> "$lab/known_hosts"
ssh-keygen -lf "$lab/host_ed25519.pub" -E sha256
ssh-keygen -F training.example.invalid -f "$lab/known_hosts"
```

The first command creates a private/public Ed25519 key pair. The `known_hosts` line binds a **hostname** to a **public host key**. `ssh-keygen -lf` prints the key's fingerprint; `-F` looks up the stored hostname. The `.invalid` name is reserved for examples and is never contacted.

## Simulate a changed host key

```bash
ssh-keygen -q -t ed25519 -N '' -f "$lab/replacement_ed25519"
ssh-keygen -lf "$lab/replacement_ed25519.pub" -E sha256
ssh-keygen -lf "$lab/host_ed25519.pub" -E sha256
```

The two fingerprints should differ. A real SSH client that previously trusted one host key will normally warn when the server presents a different key. A changed key can be legitimate (server rebuild or rotation), but may also signal interception. **Verify the new fingerprint through an independent trusted channel before updating the entry.** This offline exercise does not prove the identity of any real server.

## Cleanup

```bash
rm -f -- "$lab/host_ed25519" "$lab/host_ed25519.pub" "$lab/replacement_ed25519" "$lab/replacement_ed25519.pub" "$lab/known_hosts"
rmdir -- "$lab"
```

## Check your understanding

1. How does a server host key differ from a user's SSH authentication key?
2. Why is a matching fingerprint useful only when the expected fingerprint is trusted?
3. Why is blindly deleting a changed `known_hosts` entry dangerous?
4. What is the difference between first-use trust (TOFU) and a previously verified key?

## References

- OpenSSH manual: [ssh(1)](https://man.openbsd.org/ssh.1) — host authentication and changed-key warnings.
- OpenSSH manual: [ssh-keygen(1)](https://man.openbsd.org/ssh-keygen.1) — `-F`, `-l`, and fingerprint formats.
- OpenSSH manual: [ssh_config(5)](https://man.openbsd.org/ssh_config.5) — `StrictHostKeyChecking` behavior.
