---
name: fixreview
description: Fix issues from the most recent /codereview output. Prompts the user to choose which severity levels to fix. Invoke manually with /fixreview.
---

Apply fixes from the most recent code review in this conversation.

## Rules

- **Never run automatically.** Only run this skill when the user explicitly invokes `/fixreview`.
- **Requires a prior review.** If no `/codereview` output is present in the conversation, tell the user to run `/codereview` first and stop.
- **Follow CLAUDE.md.** All fixes must comply with the project's coding standards (type hints, docstrings, naming, pathlib, etc.).
- **Run linting and tests after fixing.** Never consider the work complete until `ruff` and `pytest` both pass.

## Steps

### 1. Parse the most recent review

Scan the conversation history for the most recent `/codereview` output. Extract every reported issue and group them by severity label exactly as written in the review (e.g. `error`, `warning`, `suggestion`). Preserve the full detail of each issue: file path, line number, description, and recommended fix.

If no review is found in the conversation, respond:
> No code review found. Please run `/codereview` first.

Then stop.

### 2. Determine severity levels present

Identify which distinct severity labels appear in the review. Sort them from most to least severe using this canonical order (unlisted labels go after `suggestion`, sorted alphabetically):

```
error > warning > suggestion
```

Build a cumulative set of fix options, one per level, where each option includes all severities at or above that level. For example, if the review contains `error`, `warning`, and `suggestion`:

| Option label | Severities included |
|---|---|
| Fix errors only | error |
| Fix errors and warnings | error, warning |
| Fix all issues | error, warning, suggestion |

If only two levels are present (e.g. `error` and `warning`), present only two options. Always include a "Fix all issues" option that covers every severity level found.

### 3. Ask the user which issues to fix

Use the `AskUserQuestion` tool to present the options. Set `header` to `"Severity"`. Each option's description should list how many issues are included at that level and what kinds of issues they are. Example:

> **Fix errors only** — 2 issues: type annotation errors and silent misbehaviour in utils

Do not proceed until the user answers.

### 4. Fix the selected issues

For each issue in the selected set, in file order (alphabetical by path, then by line number ascending):

1. Read the file if not already read.
2. Apply the fix described in the review. Prefer minimal, targeted edits — do not refactor surrounding code unless it is part of the reported issue.
3. When fixing a function that is missing type hints or docstrings as a direct consequence of the reported issue, add them. Do not add them to unrelated functions in the same file.
4. After editing a file, re-read the relevant section to verify the change is correct before moving on.

If a recommended fix in the review is ambiguous or conflicts with another fix in the same file, resolve it conservatively: apply the less invasive option and note the ambiguity in the final report.

### 5. Run linting and tests

After all edits are complete, run in sequence:

```bash
uv run ruff check --fix .
uv run ruff format .
uv run pytest tests/ -v
```

If `ruff` introduces further changes, note them. If any tests fail, diagnose and fix the root cause — do not delete or weaken tests to make them pass. If fixing a test failure requires changes beyond the reviewed issues, explain what was found and ask the user how to proceed before making additional edits.

### 6. Report

Summarise the work done:
- List each issue fixed (file, line, brief description)
- List any issues skipped and why (e.g. ambiguous, already fixed, out of scope of selection)
- Confirm the final `ruff` and `pytest` status
