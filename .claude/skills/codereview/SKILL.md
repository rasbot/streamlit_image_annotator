---
name: codereview
description: Run a thorough Python code review using the python-code-reviewer agent. Invoke manually with /codereview.
---

Run a thorough code review of the Python source code in this project using the python-code-reviewer agent.

## Rules

- **Never run automatically.** Only run this skill when the user explicitly invokes `/codereview`.
- **Do not make changes.** This skill is read-only — it reviews and reports, but does not modify files.
- **Cover all source files.** Review every Python file under `src/`.

## Steps

### 1. Launch the python-code-reviewer agent

Use the Task tool with `subagent_type: "python-code-reviewer"` and the following prompt:

```
Perform a thorough code review of this Python project. Review every file under src/ for:

- Type hint completeness and correctness (modern syntax: str | None, list[str], etc.)
- Google-style docstrings on all public modules, classes, functions, and methods
- Naming conventions (snake_case functions/variables, PascalCase classes, UPPER_SNAKE_CASE constants)
- Code quality: function length, guard clauses, comprehensions, pathlib usage, f-strings
- Error handling: specific exceptions, no silent pass, custom exception classes
- Security: no hardcoded secrets, no eval/exec/pickle on untrusted data, safe YAML loading
- Correctness: logic errors, edge cases, off-by-one errors, incorrect assumptions
- Pythonic idiom: idiomatic use of standard library and language features

For each issue found, report:
- File path and line number
- Severity: error | warning | suggestion
- Description of the issue
- Recommended fix (code snippet if helpful)

Finish with a summary: total issues by severity, and an overall assessment of code quality.
```

### 2. Report

Present the agent's full findings to the user, including:
- All issues grouped by file
- The overall summary
