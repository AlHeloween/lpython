import argparse
import pathlib
import statistics
import subprocess
import sys
import time
import os


ROOT = pathlib.Path(__file__).resolve().parents[1]
LPYTHON_BENCH = ROOT / "integration_tests" / "benchmark_math_perf.py"
CPYTHON_BENCH = ROOT / "integration_tests" / "benchmark_math_perf_cpython.py"
BUILD_DIR = ROOT / "integration_tests" / "benchmark_build"
LPYTHON_EXE = BUILD_DIR / ("benchmark_math_perf.out" if sys.platform != "win32" else "benchmark_math_perf.exe")

def get_lpython_command() -> list[str]:
    if sys.platform == "win32":
        wrapper = ROOT / "lpython.cmd"
        if wrapper.exists():
            return [str(wrapper)]
        return [str(ROOT / "src" / "bin" / "lpython.exe")]
    wrapper = ROOT / "src" / "bin" / "lpython"
    return [str(wrapper)]


def run_once(cmd: list[str]) -> tuple[float, str]:
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.perf_counter() - t0
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}"
        )
    return dt, proc.stdout


def run_binary_once(path: pathlib.Path) -> tuple[float, str]:
    t0 = time.perf_counter()
    proc = subprocess.run([str(path)], capture_output=True, text=True)
    dt = time.perf_counter() - t0
    if proc.returncode != 0:
        raise RuntimeError(
            f"binary failed ({proc.returncode}): {path}\n{proc.stdout}\n{proc.stderr}"
        )
    return dt, proc.stdout


def parse_checksums(output: str) -> dict[str, str]:
    checksums = {}
    for line in output.splitlines():
        if line.startswith("checksum_"):
            name, value = line.split("=", 1)
            checksums[name] = value.strip()
    if not checksums:
        raise RuntimeError("checksum lines not found in output")
    return checksums


def summarize(label: str, times: list[float]) -> str:
    return (
        f"{label}: mean={statistics.mean(times):.6f}s "
        f"min={min(times):.6f}s max={max(times):.6f}s"
    )


def compile_lpython_binary(lpython_cmd: list[str]) -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    if LPYTHON_EXE.exists():
        LPYTHON_EXE.unlink()
    cmd = lpython_cmd + ["-o", str(LPYTHON_EXE), str(LPYTHON_BENCH)]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if proc.returncode != 0:
        raise RuntimeError(
            f"compile failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}"
        )
    if not LPYTHON_EXE.exists():
        raise RuntimeError(f"expected output binary not found: {LPYTHON_EXE}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--mode",
        choices=["end-to-end", "binary-runtime"],
        default="binary-runtime",
    )
    args = parser.parse_args()

    lpython_cmd = get_lpython_command()

    print(f"python={args.python}")
    print(f"lpython={' '.join(lpython_cmd)}")
    print(f"cpython_benchmark={CPYTHON_BENCH}")
    print(f"lpython_benchmark={LPYTHON_BENCH}")
    print(f"repeats={args.repeats}")
    print(f"mode={args.mode}")
    print()

    py_cmd = [args.python, str(CPYTHON_BENCH)]

    py_times = []
    lp_times = []
    py_checksums = None
    lp_checksums = None

    for _ in range(args.repeats):
        dt, out = run_once(py_cmd)
        py_times.append(dt)
        py_checksums = parse_checksums(out)

    if args.mode == "end-to-end":
        lp_cmd = lpython_cmd + [str(LPYTHON_BENCH)]
        for _ in range(args.repeats):
            dt, out = run_once(lp_cmd)
            lp_times.append(dt)
            lp_checksums = parse_checksums(out)
    else:
        compile_lpython_binary(lpython_cmd)
        print(f"lpython_binary={LPYTHON_EXE}")
        print()
        warm_dt, warm_out = run_binary_once(LPYTHON_EXE)
        lp_checksums = parse_checksums(warm_out)
        print(f"warmup={warm_dt:.6f}s")
        for _ in range(args.repeats):
            dt, out = run_binary_once(LPYTHON_EXE)
            lp_times.append(dt)
            lp_checksums = parse_checksums(out)

    print("[suite] workloads=factorial_repeat,sqrt_repeat,floor_ceil_repeat,frexp_repeat")
    print(summarize("CPython", py_times))
    if args.mode == "end-to-end":
        print(summarize("LPython", lp_times))
    else:
        print(summarize("LPythonBinary", lp_times))
    print(f"speedup={statistics.mean(py_times) / statistics.mean(lp_times):.2f}x")
    for name in sorted(py_checksums):
        print(f"{name}_match={py_checksums[name] == lp_checksums.get(name)}")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
