# Lab 15 — Environment variables and process inheritance

Environment variables are strings supplied to a process when it starts. They can configure tools, but they are not a secure secret store.

## Offline exercise

Run this in a disposable Bash subshell on Linux (requires Bash and GNU env):

```bash
(
  set -eu
  unset LAB_MODE
  LAB_MODE=local
  bash -c 'printf "unexported: %s\n" "${LAB_MODE-unset}"'
  export LAB_MODE
  bash -c 'printf "exported: %s\n" "$LAB_MODE"; LAB_MODE=child'
  printf 'parent: %s\n' "$LAB_MODE"
  LAB_MODE=temporary bash -c 'printf "temporary: %s\n" "$LAB_MODE"'
  env -i PATH=/usr/bin:/bin bash -c 'printf "clean: %s\n" "${LAB_MODE-unset}"'
)
```

Expected output:

```text
unexported: unset
exported: local
parent: local
temporary: temporary
clean: unset
```

The unexported shell variable is absent from the child environment. Exporting it makes it available to subsequently launched children. Changing a variable in a child does not change its parent's copy. A command-prefix assignment supplies a value to that command; `env -i` starts with an empty environment before adding the explicitly listed variables.

## Defensive relevance

- PATH controls executable lookup for names without a slash. Use a known trusted PATH or an appropriate absolute executable path for sensitive scripts.
- Avoid dumping the entire environment into logs or bug reports: it may contain credentials.
- An exported secret can be inherited by subprocesses and may be observable through process inspection depending on operating system permissions and configuration.
- A clean environment reduces accidental inheritance but does not sandbox a process or remove its filesystem or network permissions.
- Use synthetic values only in this exercise; never paste real tokens.

## Review questions

1. Why does the first child print unset?
2. Why does changing LAB_MODE in a child leave the parent unchanged?
3. What is the difference between clearing the environment and restricting process privileges?
4. Why should diagnostic logs avoid printing all environment variables?

## References

- [Bash manual: Environment](https://www.gnu.org/software/bash/manual/html_node/Environment.html)
- [GNU Coreutils: env invocation](https://www.gnu.org/software/coreutils/manual/html_node/env-invocation.html)
- [Linux environ(7)](https://man7.org/linux/man-pages/man7/environ.7.html)
