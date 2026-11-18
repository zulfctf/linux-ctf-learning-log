# Lab 03: Inspecting Linux processes and signals

**Purpose:** Learn how to find a process, inspect its state, and terminate only a process you created. This is a self-contained Linux fundamentals exercise, not a claim that a CTF challenge was solved.

**Prerequisites:** Bash, `ps`, `kill`, and a local Linux environment.

## 1. Explore your shell and process identifiers

```bash
echo "Shell PID: $$"
ps -p "$$" -o pid,ppid,stat,comm,args
ps -u "$(id -un)" -o pid,ppid,stat,comm | head
```

- **PID** identifies an individual process.
- **PPID** is the parent process ID.
- **STAT** describes the process state; common codes include `R` (running), `S` (interruptible sleep), `T` (stopped), and `Z` (zombie).
- **COMMAND/COMM** is a short command name; **ARGS** includes its invocation.

## 2. Start a harmless background process

```bash
sleep 300 &
lab_pid=$!
printf 'Started sleep with PID %s\n' "$lab_pid"
ps -p "$lab_pid" -o pid,ppid,stat,etime,comm
```

`&` starts the command in the background. `$!` captures the PID of the most recent background pipeline. Record this PID before moving on. Run the commands in the same shell session.

## 3. Send a graceful termination signal

```bash
kill -TERM "$lab_pid"
wait "$lab_pid"
printf 'wait exit status: %s\n' "$?"
```

`SIGTERM` asks a process to terminate; it can be handled or ignored. `wait` reaps the shell's child. The resulting nonzero status is expected when a process is terminated by a signal.

If the command has already exited, `kill` can report "No such process." That is not permission to target another process with the same PID.

## 4. Questions to investigate

1. Why is `kill -9` (`SIGKILL`) usually a poor first choice?
2. Why should you inspect the full command and owner before terminating a process?
3. What is the difference between `ps` (snapshot) and `top` (updating process view)?
4. Can a zombie process be fixed by repeatedly sending signals to its PID?

<details>
<summary>Explanations</summary>

1. `SIGKILL` cannot be caught or handled, preventing normal cleanup.
2. A PID can refer to an unrelated process, and ending the wrong process can interrupt work.
3. `ps` shows process information at a point in time; `top` refreshes a view repeatedly.
4. No. A zombie has exited and must be reaped by its parent (or an adopting process); signals cannot make it run again.

</details>

## Safety and troubleshooting

- Never copy a PID from another person, a screenshot, or a production system into a `kill` command.
- Avoid `killall` and `pkill` for this lab; they can match other processes.
- If `sleep` exits before inspection, repeat the lab and capture its new PID.
- The exercise requires no root privileges or changes to system configuration.

**Further study:** `man 1 ps`, `man 1 kill`, `man 7 signal`, and `help wait`.
