# Lab 13 — Inspecting HTTP responses locally

## Goal

Understand status codes, response headers, and the difference between a GET and a HEAD request. This exercise uses only a loopback server and synthetic data, not an external website.

Requires Python 3.9 or newer and curl. Open two terminals.

## Terminal A: start a disposable server

```bash
(
  set -eu
  workdir=$(mktemp -d)
  trap 'rm -rf -- "$workdir"' EXIT
  printf 'hello from the lab\n' > "$workdir/index.html"
  python3 -m http.server 8765 --bind 127.0.0.1 --directory "$workdir"
)
```

If the port is occupied, choose another unused port and update all URLs below. Do not stop an unrelated process. The server serves only the temporary directory; do not place sensitive files there. Python's development server is not suitable for production.

## Terminal B: inspect responses

```bash
curl --noproxy '*' -i http://127.0.0.1:8765/
curl --noproxy '*' -I http://127.0.0.1:8765/
curl --noproxy '*' -i http://127.0.0.1:8765/missing.txt
curl --noproxy '*' -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8765/missing.txt
```

Expected observations:

- The first request returns 200, headers, and the synthetic response body.
- The second sends HEAD and returns headers without the response body.
- The third returns 404 with an error response.
- The last prints 404 alone. By default curl can exit successfully after receiving an HTTP error response; use `--fail` when a 4xx or 5xx response should cause a failing exit status.

```bash
if curl --noproxy '*' --fail -sS -o /dev/null http://127.0.0.1:8765/missing.txt; then
  echo 'Unexpected success'
else
  echo "curl exit status: $?"
fi
```

Expected exit status: 22 for this HTTP 404 response. Stop the server with Ctrl+C in terminal A.

## Reading the evidence

| Field | Meaning |
| --- | --- |
| Status code | Server's reported result for the request |
| Content-Type | Declared media type, not proof that the body is safe |
| Content-Length | Declared length in bytes, when present |
| Server | Optional server identification; not proof of a vulnerability |

HTTP status and shell exit status are separate layers. A successful transport does not imply a successful application operation. Likewise, an absent security header or a version string alone does not establish exploitability. This loopback exercise uses plaintext HTTP and no credentials.

## Review questions

1. Why does HEAD omit the response body?
2. Why might curl return exit status zero for a 404?
3. Why bind the development server to loopback rather than every interface?
4. Why is a Server header insufficient evidence for a vulnerability report?

## References

- [Python http.server](https://docs.python.org/3/library/http.server.html)
- [curl manual](https://curl.se/docs/manpage.html)
- [RFC 9110: HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html)

Run only against your own local lab or explicitly authorized systems. Expected outputs are predictions, not claims of personal completion.
