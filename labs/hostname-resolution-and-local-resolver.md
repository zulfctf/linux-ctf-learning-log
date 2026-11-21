# Lab 09: Hostname resolution, DNS, and the local resolver

**Goal:** Understand why resolving a hostname is not necessarily a DNS query, and distinguish local name-service lookup from a direct DNS lookup.

**Environment:** Linux with Python 3.9+ and optionally `getent`. The core exercise uses only the loopback hostname and Python's standard library; no external DNS requests, root access, or network scanning.

## 1. Three different concepts

- A **hostname** is a human-readable label, such as `localhost`.
- A **resolver** maps a name to address records. On Linux, applications commonly use the system's name-service configuration, which may consult `/etc/hosts`, DNS, or other configured sources.
- **DNS** is a network protocol and distributed naming system. A successful `getaddrinfo()` call does **not** prove that a DNS server was contacted.

`/etc/nsswitch.conf` commonly controls the order of sources for the `hosts` database, but configurations differ. `/etc/resolv.conf` can identify DNS resolver settings; neither file alone proves which source answered a particular lookup.

## 2. Inspect the local resolver without modifying it

Run in your own Linux environment:

```bash
python3 - <<'PY'
import socket

results = socket.getaddrinfo("localhost", None, type=socket.SOCK_STREAM)
addresses = sorted({item[4][0] for item in results})
print("localhost addresses:", ", ".join(addresses))
assert addresses, "localhost should resolve on a normally configured host"
print("PASS: local hostname resolved")
PY
```

Typical results include `127.0.0.1` and/or `::1`. Exact results vary with IPv4/IPv6 and system configuration. Both are loopback addresses; neither points to a public host.

If `getent` is installed, compare the system name-service result:

```bash
getent ahosts localhost
```

`getent ahosts` asks the system resolver for socket addresses. It may list the same address more than once for different socket types. An unavailable `getent` command is not evidence of DNS failure.

## 3. Inspect configuration safely (read-only)

```bash
if test -r /etc/nsswitch.conf; then
  grep -E '^[[:space:]]*hosts:' /etc/nsswitch.conf || true
fi
if test -r /etc/hosts; then
  grep -E '(^|[[:space:]])localhost([[:space:]]|$)' /etc/hosts || true
fi
```

A `hosts:` line describes lookup sources and order, not necessarily the source used for every query. Entries for `localhost` in `/etc/hosts` are common, but the actual result depends on the machine. **Do not edit either file for this exercise.**

## 4. Controlled exercise: validate loopback answers

```bash
python3 - <<'PY'
import ipaddress
import socket

answers = {record[4][0] for record in socket.getaddrinfo(
    "localhost", None, type=socket.SOCK_STREAM
)}
assert answers, "no address returned"
for address in sorted(answers):
    parsed = ipaddress.ip_address(address)
    print(address, "loopback:", parsed.is_loopback)
    assert parsed.is_loopback, f"unexpected non-loopback localhost mapping: {address}"
print("PASS: all localhost answers are loopback")
PY
```

If this check fails, **investigate the host's configuration** rather than assuming the script is defective or changing system files blindly. This is a diagnostic assertion for an expected local setup, not a guarantee across every operating environment.

## 5. Review questions

1. Why can `localhost` resolve even with no internet access?
2. Does `socket.getaddrinfo()` prove a DNS packet was sent? Why not?
3. How are `/etc/hosts`, `/etc/nsswitch.conf`, and `/etc/resolv.conf` different?
4. Why might `getent ahosts localhost` print duplicate addresses?
5. What is the difference between IPv4 `127.0.0.1` and IPv6 `::1`?

**Safety:** No files are changed, no external hostnames are queried, and no network scanning is performed. The commands only inspect local configuration and resolve `localhost`.

**References:** [Python socket.getaddrinfo](https://docs.python.org/3/library/socket.html#socket.getaddrinfo), [Python ipaddress](https://docs.python.org/3/library/ipaddress.html), [Linux getent(1)](https://man7.org/linux/man-pages/man1/getent.1.html), [Linux nsswitch.conf(5)](https://man7.org/linux/man-pages/man5/nsswitch.conf.5.html), [Linux hosts(5)](https://man7.org/linux/man-pages/man5/hosts.5.html).
