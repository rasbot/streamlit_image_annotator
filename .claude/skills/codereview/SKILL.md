---
name: codereview
description: Run a thorough Python code review using the python-code-reviewer agent. Invoke manually with /codereview.
---

Run a thorough code review of Python source code in this project using the python-code-reviewer agent.

## Rules

- **Never run automatically.** Only run this skill when the user explicitly invokes `/codereview`.
- **Do not make changes.** This skill is read-only — it reviews and reports, but does not modify files.

## Determining the review scope

The skill may be invoked with an optional argument:

| Invocation | Scope |
|---|---|
| `/codereview` | Every Python file under `src/` |
| `/codereview <dir>` | Every Python file under the given directory (e.g. `src/streamlit_image_annotator`) |
| `/codereview <file>` | Only the specified Python file (e.g. `src/streamlit_image_annotator/constants.py`) |

Always include `README.md` in the review for context regardless of scope.

Before launching the agent, state clearly which files will be reviewed.

If the provided path does not exist or contains no Python files, tell the user and stop.

## Steps

### 1. Resolve the scope

- If no argument was provided, set scope to `src/` (all Python files recursively).
- If an argument was provided, check whether it is a directory or a file:
  - **Directory:** collect all `*.py` files under it recursively.
  - **File:** use that single file.
- Add `README.md` to the file list.

### 2. Launch the python-code-reviewer agent

Use the Task tool with `subagent_type: "python-code-reviewer"` and a prompt built from the resolved scope:

```
Perform a thorough code review of the following files in this Python project:

<file list here>

For each file, review:

- Type hint completeness and correctness (modern syntax: str | None, list[str], etc.)
- Google-style docstrings on all public modules, classes, functions, and methods
- Naming conventions (snake_case functions/variables, PascalCase classes, UPPER_SNAKE_CASE constants)
- Code quality: function length, guard clauses, comprehensions, pathlib usage, f-strings
- Error handling: specific exceptions, no silent pass, custom exception classes
- Security: no hardcoded secrets, no eval/exec/pickle on untrusted data, safe YAML loading
- Correctness: logic errors, edge cases, off-by-one errors, incorrect assumptions
- Pythonic idiom: idiomatic use of standard library and language features

For the README.md, check only that it accurately reflects the current source code (structure, features, usage).

For each issue found, report:
- File path and line number
- Severity: error | warning | suggestion
- Description of the issue
- Recommended fix (code snippet if helpful)

Finish with a summary: total issues by severity, and an overall assessment of code quality.
```

### 3. Report

Present the agent's full findings to the user, including:
- All issues grouped by file
- The overall summary
