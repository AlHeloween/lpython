# LPython Math Imports And Benchmarking Notes

## Scope

This note describes how LPython resolves `math` imports, what the runtime
`math` module actually exports, and what constraints matter when writing
performance benchmarks for LPython.

The goal is to replace trial-and-error with source-grounded guidance.

## 1. Where `import math` resolves from

LPython resolves modules by searching the import paths and then the runtime
library directory. The key lookup path is implemented in
`src/lpython/semantics/python_ast_to_asr.cpp:60-103`.

- `get_full_path()` first tries `<runtime_library_dir>/<module>.py` at
  `src/lpython/semantics/python_ast_to_asr.cpp:63-77`.
- It has special handling for `lpython.py` and `numpy.py` at
  `src/lpython/semantics/python_ast_to_asr.cpp:78-99`.
- If a module path is not found in user import paths, the compiler falls back
  to the runtime library directory at
  `src/lpython/semantics/python_ast_to_asr.cpp:4866-4870`.
- Plain `import ...` constructs are lowered by
  `src/lpython/semantics/python_ast_to_asr.cpp:4953-4995`.
- `from ... import ...` constructs are lowered by
  `src/lpython/semantics/python_ast_to_asr.cpp:4875-4908`.

The runtime library directory itself is chosen in
`src/lpython/utils.cpp:55-80`.

- Development tree: `src/bin -> ../runtime` at `src/lpython/utils.cpp:67-71`
- Installed tree: `bin -> ../share/lpython/lib` at `src/lpython/utils.cpp:76-78`

That means `import math` is not magical. In practice it depends on the runtime
file `src/runtime/math.py` in a build tree, or `share/lpython/lib/math.py` in
an installed package.

## 2. Why standalone packages previously broke on `import math`

The runtime Python modules were copied into the build tree, but were not
originally installed into `share/lpython/lib`. That meant the installed runtime
search path existed, but did not contain `math.py`.

The current install fix is driven from `CMakeLists.txt`, where runtime files are
configured and installed from the build tree.

- Runtime files are configured with LF normalization in `CMakeLists.txt`
- Installed runtime module destination is `share/lpython/lib`

When diagnosing future import failures, verify the installed payload first:

- `share/lpython/lib/math.py`
- `share/lpython/lib/lpython_builtin.py`
- `share/lpython/lib/lpython/lpython.py`

## 3. What `math.py` actually exports

The runtime `math` module is implemented in `src/runtime/math.py`.

The current implementation is intentionally split:

- Runtime-backed scalar wrappers:
  - `sqrt`, `cbrt`, `log`, `log10`, `log2`, `log1p`, `expm1`
  - `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`
  - `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh`
  - `erf`, `erfc`, `gamma`, `lgamma`
  - `fmod`, `remainder`, `copysign`, `hypot`, `ldexp`, `trunc`
- LPython-native higher-level helpers:
  - `factorial`, `comb`, `perm`, `gcd`, `lcm`, `isqrt`
  - `fsum`, `prod`, `dist`
  - `degrees`, `radians`, `isclose`
  - tuple assembly helpers `modf` and `frexp`

Representative definitions:

- `modf`: `src/runtime/math.py:10-20`
- `ldexp`: `src/runtime/math.py:458-459`
- `copysign`: `src/runtime/math.py:508-512`
- `hypot`: `src/runtime/math.py:515-519`
- `trunc`: `src/runtime/math.py:521-540`
- `sqrt`: `src/runtime/math.py:543-551`
- `cbrt`: `src/runtime/math.py:553-557`
- `log2`: `src/runtime/math.py:594-595`
- `expm1`: `src/runtime/math.py:700-705`
- `log1p`: `src/runtime/math.py:707-708`
- `remainder`: `src/runtime/math.py:722-723`
- `frexp`: `src/runtime/math.py:751-781`

This matters for benchmarking: scalar wrappers mostly measure the runtime/codegen
path, while helpers like `frexp` and `modf` still include LPython-level tuple
assembly logic.

## 4. Which import styles are already tested in-tree

The existing integration coverage shows two supported styles:

- `from math import ...` in `integration_tests/test_math.py:1-3`
- `import math` with module-qualified access in
  `integration_tests/test_math1.py:1-11`

Examples already covered by tests:

- direct import and use of `exp()` at `integration_tests/test_math.py:58-61`
- module-qualified `math.factorial()` at `integration_tests/test_math1.py:6-11`
- direct import of constants `pi` and `e` at
  `integration_tests/test_math1.py:1-11`

So the source tree indicates:

- `import math` is intended to work
- `from math import ...` is also intended to work
- missing-symbol failures should be treated as implementation gaps, not as user
  misuse by default

## 5. Why benchmark code must be written differently from CPython code

LPython still has type-system and semantic restrictions that affect benchmark
authoring.

### 5.1 Builtin `int` and `float` annotations are not the right benchmark types

LPython emits a semantic error for `int` annotations and tells the user to use
its fixed-size scalar aliases instead. See:

- `src/lpython/semantics/python_ast_to_asr.cpp:909-919`

The same codepath also handles unsupported `float` similarly at
`src/lpython/semantics/python_ast_to_asr.cpp:919-920`.

Practical consequence:

- Use `i32`, `i64`, `f32`, `f64` in LPython benchmark sources
- Do not assume a CPython-idiomatic `int`/`float` benchmark file is valid LPython input

### 5.2 `try/except` is parsed but not lowered through semantics

The parser defines `Try_t` construction macros in
`src/lpython/parser/semantics.h:301-316`.

However, the semantic visitor file `src/lpython/semantics/python_ast_to_asr.cpp`
does not implement a `visit_Try(...)` lowering path. That explains why using
`try/except ImportError` in a shared CPython/LPython benchmark source is a poor
fit today.

Practical consequence:

- Do not rely on `try/except` fallback logic inside LPython benchmark sources
- Prefer separate CPython and LPython benchmark source files if compatibility
  glue is needed

### 5.3 Imported symbol lookup is strict

When `from module import symbol` is lowered, LPython requires the symbol to be
resolvable from the loaded module symbol table. The failure is raised at:

- `src/lpython/semantics/python_ast_to_asr.cpp:936-943`

Practical consequence:

- Benchmark only symbols that are explicitly implemented in `src/runtime/math.py`
- If a symbol compiles in one import style but not another, inspect the loaded
  module symbol table path rather than assuming a runtime bug immediately

## 6. Benchmark authoring guidance

For LPython math benchmarks in this repository:

1. Use a dedicated LPython benchmark source with LPython scalar types.
   - Example types: `i32`, `f64`
   - Source of that requirement: `src/lpython/semantics/python_ast_to_asr.cpp:909-919`

2. Use math functions that reflect the path you want to measure.
   - Runtime-heavy candidates: `sqrt`, `cbrt`, `log2`, `log1p`, `expm1`,
     `sin`, `cos`, `hypot`
   - Mixed LPython/runtime candidates: `frexp`, `modf`
   - Algorithmic LPython candidates: `factorial`, `gcd`, `isclose`

3. Keep CPython and LPython benchmark inputs separate if compatibility glue
   would otherwise require `try/except` or unsupported typing.

4. For installed-package benchmarking, verify the runtime module payload exists
   before interpreting benchmark results.
   - `share/lpython/lib/math.py`
   - `share/lpython/lib/lpython_builtin.py`

5. Run LPython on Windows through the wrapper, not directly through
   `src/bin/lpython.exe`, if the benchmark emits an executable.
   - This follows the repo’s Windows command policy and the wrapper behavior.

## 7. Current practical conclusion

Current verified benchmark state in this tree:

- Runtime-only benchmark entrypoint:
  - `tools/run_math_benchmark.py --mode binary-runtime --repeats 2`
- Current checked workloads:
  - `factorial_repeat`
  - `sqrt_repeat`
  - `floor_ceil_repeat`
  - `frexp_repeat`
- Latest verified oracle after the current `math.py` refactor work:
  - run id `20260319T214232Z_6f1cef28`
  - `LPythonBinary mean=0.191826s`
  - checksum parity for all workloads

So the current working model is:

- `math` support is runtime-module based, not compiler-intrinsic by default.
- Scalar floating-point functions should prefer runtime-backed wrappers.
- Tuple-return helpers remain reasonable LPython-native glue unless a better C
  ABI pattern is introduced.
- Benchmarks must respect LPython-specific scalar types and current semantic
  limitations.

That is the defensible path for future performance work in this tree.
