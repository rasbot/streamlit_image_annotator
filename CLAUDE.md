# Project Guidelines for Claude Code

## Session Startup — Do This First

At the beginning of every session, before doing any work:

1. Read the `README.md` to understand the project's purpose, architecture, and conventions.
2. Scan the project structure (`src/`, `tests/`, `pyproject.toml`, etc.) to understand the layout.
3. Read `pyproject.toml` to understand dependencies, Python version, and tool configurations.
4. If any of the following are missing, **stop and ask the user** before proceeding:
   - `src/` directory for source code
   - `tests/` directory for unit tests
   - `pyproject.toml` with `[tool.ruff]`, `[tool.pytest.ini_options]`, and `[project]` sections
   - `uv` as the package manager (look for `uv.lock` or `[tool.uv]` in `pyproject.toml`)
   - If these are missing, suggest setting them up and offer to help scaffold the structure.

## Project Structure

All projects should follow this layout:

```
project-root/
├── src/
│   └── package_name/
│       ├── __init__.py
│       └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── ...
├── pyproject.toml
├── uv.lock
├── README.md
└── CLAUDE.md
```

- All source code lives under `src/`.
- All tests live under `tests/` and mirror the `src/` structure.
- Configuration goes in `pyproject.toml`, not `setup.cfg` or `setup.py`.

## Python Coding Standards

### Type Hints — Required Everywhere

- Every function and method must have type hints for all parameters and the return type.
- Use modern syntax: `str | None` not `Optional[str]`, `list[str]` not `List[str]`.
- Use `from __future__ import annotations` if supporting Python < 3.10.
- Use specific types: `list[str]` not `list`, `dict[str, int]` not `dict`.
- Use `Any` sparingly and only when truly necessary.
- Add variable annotations for non-obvious types: `results: list[str] = []`.

### Docstrings — Required for All Public Interfaces

- Use Google-style docstrings consistently.
- Every public module, class, function, and method must have a docstring.
- Private functions should have docstrings if their behavior is non-obvious.
- Docstrings must include: summary line, Args, Returns, and Raises sections as applicable.
- The summary line should describe *what* the function does, not restate the signature.
- When modifying existing code that lacks docstrings or type hints, **add them**.

Example:

```python
def calculate_risk_score(provider_id: str, lookback_days: int = 365) -> float:
    """Calculate the aggregate risk score for a healthcare provider.

    Queries claim history within the lookback window and applies the weighted
    scoring model defined in the risk configuration.

    Args:
        provider_id: The NPI or internal identifier for the provider.
        lookback_days: Number of days of history to consider. Defaults to 365.

    Returns:
        A normalized risk score between 0.0 and 1.0.

    Raises:
        ProviderNotFoundError: If no provider matches the given ID.
        InsufficientDataError: If fewer than 10 claims exist in the window.
    """
```

### Naming Conventions

- Functions and variables: `snake_case` — use descriptive verb phrases for functions.
- Classes: `PascalCase` — use nouns describing what the object is.
- Constants: `UPPER_SNAKE_CASE` — defined at module level.
- Booleans: should read as questions — `is_valid`, `has_coverage`, `should_retry`.
- No magic numbers or strings. Use named constants or enums.
- Avoid vague names like `data`, `result`, `temp`, `process`, `handle`.

### Code Quality

- Functions should generally be under 40 lines. Extract helpers for complex logic.
- Use early returns and guard clauses to reduce nesting.
- Prefer comprehensions over manual loops for simple transformations.
- Use `pathlib.Path` over `os.path`.
- Use f-strings for formatting.
- Use context managers (`with`) for all resource management.
- Never use mutable default arguments. Use `None` and assign inside the function body.
- Use `dataclass` or `pydantic.BaseModel` for structured data, not raw dicts.
- Define `__all__` in public modules.

### Error Handling

- Never use bare `except:` or `except Exception:` without good reason.
- Catch specific exceptions at the appropriate level.
- Always log or re-raise caught exceptions with context — no silent `pass`.
- Use custom exception classes for domain-specific errors.
- Validate inputs at function boundaries.

### Imports

- Follow standard ordering: stdlib → third-party → local.
- Use absolute imports. Avoid relative imports unless within a package's internal modules.
- Place imports used only for type checking behind `if TYPE_CHECKING:`.

## Package Management — uv

- Use `uv` for all dependency management.
- Add dependencies with `uv add <package>`.
- Add dev dependencies with `uv add --dev <package>`.
- Run tools with `uv run <command>`.
- Never use `pip install` directly.

## Linting and Formatting — Ruff

**After every change**, run the following before considering work complete:

```bash
uv run ruff check --fix .
uv run ruff format .
```

This handles linting, formatting, and import sorting in one tool. Ruff configuration should be in `pyproject.toml` under `[tool.ruff]`. If it does not exist, suggest adding a baseline config:

```toml
[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "RUF"]

[tool.ruff.lint.isort]
known-first-party = ["package_name"]
```

## Testing — pytest

- All tests use `pytest`. Never use `unittest` directly.
- Test files are in `tests/` and mirror the `src/` directory structure.
- Test names describe the scenario and expected outcome: `test_calculate_risk_score_returns_zero_for_new_provider`.
- Follow the Arrange-Act-Assert pattern.
- Use `pytest.mark.parametrize` for similar test cases.
- Use fixtures in `conftest.py` for shared setup.
- Use `pytest.approx` for floating-point comparisons.
- Test edge cases: empty inputs, None values, boundary conditions, error paths.
- Run tests with: `uv run pytest tests/ -v`

## README Maintenance

- The README should reflect the current state of the project.
- When adding new features, modules, or significant changes, update the README to reflect them.
- Keep the README sections current: purpose, installation, usage, project structure, and development setup.

## Git Practices

- Write clear, imperative commit messages: "Add risk score calculation" not "added stuff".
- Keep commits focused on a single logical change.
- Do not commit generated files, cache directories, or environment-specific configs.

## When Modifying Existing Code

- Always read and understand the surrounding code before making changes.
- Preserve existing conventions within a file even if they differ from these guidelines — consistency within a file matters more than global uniformity.
- When touching a function that lacks type hints or docstrings, add them as part of your change.
- Do not refactor unrelated code unless explicitly asked to.
- Run linting and tests after every change.

## Security

- Never hardcode secrets, API keys, tokens, or credentials.
- Do not log sensitive data (PII, PHI, credentials).
- Validate and sanitize external input.
- Use `yaml.safe_load()` not `yaml.load()`.
- Never use `eval()`, `exec()`, or `pickle.load()` on untrusted data.