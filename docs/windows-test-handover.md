# Windows Test Handover

## Current state

- Verified on Windows in the `lpython` micromamba environment.
- Full suite command:

  ```powershell
  micromamba run -n lpython python run_tests.py --no-color
  ```

- Passing oracle:
  - Run id: `20260319T151133Z_6619a0ec`
  - Log: `logs/cmd_runner/20260319T151133Z_6619a0ec/stdout.log`
  - Result: `TESTS PASSED`

## What was fixed

1. Windows test launch now resolves to an absolute executable path instead of
   relying on bare `lpython` lookup from the repo root.
2. The test harness prefers the repo-root `lpython.cmd` wrapper on Windows so
   runtime executions bootstrap the Visual Studio environment before linking.
3. The wrapper falls back to `src/bin/lpython.exe` in a build tree.
4. Runtime Python files are configured with LF endings so LPython can parse
   them correctly on Windows.
5. Intrinsic module compilation uses the normalized runtime files.
6. `run_with_dbg` tests are no longer hard-skipped on Windows. The harness now
   probes whether the active build supports runtime stacktraces and only skips
   when that feature is genuinely unavailable.

## Files changed for the Windows test pass

- `libasr/src/libasr/compiler_tester/tester.py`
- `cmake/lpython.cmd.in`
- `CMakeLists.txt`
- `src/bin/CMakeLists.txt`

## Windows runtime stacktrace build

- Configure with:

  ```powershell
  cmake -S . -B build-windows-stacktrace -DWITH_RUNTIME_STACKTRACE=yes
  ```

- Build from a Visual Studio developer shell:

  ```powershell
  cmake --build build-windows-stacktrace --target lpython
  ```

- Backend notes:
  - Windows runtime stacktraces use `DbgHelp`, not `link.h`.
  - Debug-info builds rely on `/DEBUG` during the final Windows link step so
    the generated executable keeps PDB-backed line information.
  - Unix `llvm-dwarfdump` / `lines.dat` generation remains unchanged and is not
    used on Windows.

- Focused validation:

  ```powershell
  micromamba run -n lpython python run_tests.py --no-color --test runtime_errors/test_assert_01.py --test runtime_errors/test_assert_03.py --test runtime_errors/test_quit_01.py --test runtime_errors/test_raise_01.py
  ```

- Broad validation:

  ```powershell
  micromamba run -n lpython python run_tests.py --no-color
  ```

- Normal Windows builds without `-DWITH_RUNTIME_STACKTRACE=yes` remain
  supported. In that case the harness still skips `run_with_dbg` instead of
  failing those tests.
