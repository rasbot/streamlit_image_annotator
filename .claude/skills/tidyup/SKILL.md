---
name: tidyup
description: Run a full project health check - verify coding standards, sync and run tests, update README. Invoke manually with /tidyup.
---

Run a full project health check: verify coding standards, sync tests with source, run the test suite, and update the README.

## Steps

### 1. Read the README
Read `README.md` and understand the current documented state of the project.

### 2. Check Coding Standards
Read every file in `src/` and verify compliance with `CLAUDE.md`:
- Every public module, class, function, and method has a Google-style docstring (summary line, Args, Returns, Raises as applicable — no redundant type annotations in Args)
- Every function and method has complete type hints on all parameters and the return type
- Modern type syntax is used: `str | None` not `Optional[str]`, `list[str]` not `List[str]`, `collections.abc` not `typing`
- No mutable default arguments
- Constants are `UPPER_SNAKE_CASE` and immutable (`frozenset` for sets of values)
- `pathlib.Path` is used instead of raw `os.path` string manipulation where practical
- Custom exceptions are used for domain-specific errors

Report any violations found. Fix them directly.

### 3. Sync Unit Tests with Source
For each file in `src/`, check that a corresponding test file exists in `tests/`. For each public function, method, and class:
- Verify existing tests cover the happy path, error paths, and edge cases
- Add any missing tests
- Remove or update any tests that no longer reflect the current implementation
- Ensure mocks patch at the correct module boundary (e.g., `audio_extractor.os.path.isfile` not `os.path.isfile`)

### 4. Run the Test Suite
```bash
uv run pytest -v
```

All tests must pass. If any fail, fix the underlying issue — do not delete or weaken tests to make them pass.

### 5. Update the README
Compare the README against the current state of the project. Update it if any of the following have changed:
- Supported file formats
- CLI flags or their types (e.g., `--dBFS` accepts floats)
- Installation or usage instructions
- Project structure
- Development/testing commands

Do not change sections that are already accurate.

### 6. Report
Summarise what was checked, what was fixed, and confirm the final test count and pass rate.
