# Lab 14 — JSON syntax and duplicate keys

Security tools often exchange JSON. Valid syntax alone does not guarantee that a document has the expected structure or an unambiguous meaning.

## Offline exercise

Requires Python 3.9+. Run in a disposable shell:

```bash
workdir=$(mktemp -d)
(
  cd "$workdir" || exit 1
  printf '%s\n' '{"role":"reader","role":"admin"}' > duplicate.json
  printf '%s\n' '{"role":"reader",}' > malformed.json
  python3 -m json.tool duplicate.json
  python3 -m json.tool malformed.json
  printf 'Malformed JSON exit status: %s\n' "$?"
)
rm -r -- "$workdir"
```

The default Python decoder retains the last value of a repeated key. The malformed example fails because JSON does not allow trailing commas. A successful parse is not evidence that duplicate keys were absent.

## Reject ambiguous objects

Run this standalone Python example:

```python
import json

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result

def reject_constant(value):
    raise ValueError(f"nonstandard numeric constant: {value}")

def parse_record(raw):
    record = json.loads(raw, object_pairs_hook=unique_object,
                        parse_constant=reject_constant)
    if not isinstance(record, dict) or set(record) != {"role"}:
        raise ValueError("expected exactly one role field")
    if record["role"] not in ("reader", "writer"):
        raise ValueError("unexpected role")
    return record

examples = [
    '{"role":"reader"}',
    '{"role":"reader","role":"writer"}',
    '{"role":"admin"}',
    '{"role":NaN}',
    '{"role":"reader",}',
    '[]',
]
for raw in examples:
    try:
        print("Accepted:", parse_record(raw))
    except ValueError as exc:
        print("Rejected:", exc)
```

Expected: only the first example is accepted. The hook also detects duplicate keys in nested objects. The constant hook rejects Python's default extensions NaN and Infinity. This example is not a general schema validator or authorization mechanism: real services must independently authorize actions and limit input size and nesting before processing untrusted data.

## Review questions

1. Why can two JSON parsers disagree about duplicate keys?
2. Why does syntax validation not establish authorization?
3. How would you add a required integer field while rejecting Boolean values (which are subclasses of int in Python)?

## References

- [RFC 8259, section 4](https://www.rfc-editor.org/rfc/rfc8259#section-4)
- [Python JSON documentation](https://docs.python.org/3/library/json.html)

Use synthetic inputs only; no external service is required.
