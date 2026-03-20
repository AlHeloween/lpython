# AGENTS.md

## Command Execution Policy

- For long-running, noisy, or crash-prone commands on Windows, use the repo-root
  `cmd_runner.py` workflow instead of ad-hoc shell polling.
- Do not use `Start-Sleep` as a polling mechanism while waiting for command
  completion.
- When a task is started, carry it through to completion whenever feasible.
- Do not stop at a partial implementation or mid-verification state if the
  remaining work is still actionable in the current turn.
- Prefer the `cmd_runner` flow:
  - `start` to launch the command and capture a `run_id`
  - `status` or `wait` to observe completion state
  - `tail` or log files for output inspection
  - `stop` only when cancellation is required
- Prefer repo-local invocation:

  ```powershell
  uv run .\cmd_runner.py start --cwd <repo_root> --timeout-s <N> -- <COMMAND>
  ```

- Use `logs/cmd_runner/...` artifacts as the oracle for long-running command
  output when possible.
- Never use `cmd /c "..."` directly. Always use `powershell -c 'cmd /c "..."'` for Windows command execution.
