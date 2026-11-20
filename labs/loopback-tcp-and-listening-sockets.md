# Lab 07: Loopback TCP and listening sockets

**Goal:** Distinguish an IP address from a port, observe a TCP listener, and test a connection without scanning other machines.

**Requirements:** Linux, Python 3 (standard library), and optionally `ss` from iproute2. No root privileges, internet access, or external targets are needed.

## 1. Know the scope

`127.0.0.1` is IPv4 loopback: traffic addressed to it stays on the local host. A TCP endpoint combines an IP address and a port. A listening socket waits for incoming connections; a connected socket exchanges data with one peer. A successful TCP connection only proves something accepted the connection, **not** that the service is trustworthy.

Do not change the bind address to `0.0.0.0` or a public interface for this lab. That could expose the demonstration service to other devices.

## 2. Run a disposable local TCP exercise

Copy the complete block into a Linux terminal:

```bash
python3 - <<'PY'
import socket
import threading

# Port zero asks the OS to choose an available ephemeral port.
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    host, port = listener.getsockname()
    print("Listening on {}:{}".format(host, port))

    def serve_once():
        conn, peer = listener.accept()
        with conn:
            data = conn.recv(1024)
            conn.sendall(b"ACK:" + data)
            print("Accepted a local client from", peer[0])

    worker = threading.Thread(target=serve_once)
    worker.start()
    with socket.create_connection((host, port), timeout=3) as client:
        client.settimeout(3)
        client.sendall(b"hello")
        reply = client.recv(1024)
    worker.join(timeout=3)
    assert not worker.is_alive(), "server did not finish"
    assert reply == b"ACK:hello", reply
    print("PASS: loopback TCP request and response")
PY
```

Expected: a `Listening on 127.0.0.1:<port>` line, an accepted local client, and `PASS: loopback TCP request and response`. The port is chosen dynamically, so its number varies.

The example creates one listener, serves one client, then closes both sockets automatically. It is not an HTTP server and does not parse untrusted commands.

## 3. Inspect listeners (optional)

In a separate terminal, `ss -ltn` lists listening TCP sockets. `-l` means listening, `-t` means TCP, and `-n` avoids service-name resolution. The short Python example exits quickly, so you may not catch its listener in `ss`; this is expected.

For a listener you can observe, run this in terminal A, then press Ctrl+C when finished:

```bash
python3 - <<'PY'
import socket
with socket.socket() as s:
    s.bind(("127.0.0.1", 0))
    s.listen()
    print("Temporary loopback listener:", s.getsockname(), flush=True)
    input("Inspect with 'ss -ltn' in another terminal, then press Enter to stop...")
PY
```

In terminal B run `ss -ltn` and find the printed port on `127.0.0.1`. Do not infer a process owner from `ss -ltn`; `ss -ltnp` requests process information, which may be limited by permissions.

## 4. Review questions

1. Why is binding to `127.0.0.1` safer for this exercise than binding to `0.0.0.0`?
2. Why is the selected port different between runs?
3. What does a successful TCP handshake prove, and what does it *not* prove?
4. Why might `ss -ltn` not display the short-lived example?
5. How do listening and established TCP sockets differ?

**Safety:** Only connect to the local test service you created. Do not use this exercise to probe third-party networks.

**References:** [Python socket documentation](https://docs.python.org/3/library/socket.html), [Linux ss manual](https://man7.org/linux/man-pages/man8/ss.8.html), [RFC 1122, Internet host requirements](https://www.rfc-editor.org/rfc/rfc1122).
