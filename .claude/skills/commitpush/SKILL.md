---
name: commitpush
description: Commit staged or unstaged changes as small, atomic commits and push to the current branch. Invoke manually with /commitpush.
---

Commit the current working tree changes as one or more small, atomic commits, then push to the remote branch.

## Rules

- **Never commit automatically.** Only run this skill when the user explicitly invokes `/commitpush`.
- **Prefer small, atomic commits** over one large commit. Group changes by logical unit — for example, a source change and its corresponding test belong together, but unrelated changes should be separate commits.
- **Never commit unrelated files together.** If the working tree contains changes across multiple logical concerns, split them into separate commits.
- **Never commit generated files, secrets, or environment-specific configs** (e.g. `.env`, `__pycache__`, `.venv`).
- **Never force-push** unless the user explicitly asks.

## Steps

### 1. Inspect the working tree
Run the following in parallel:
```bash
git status
git diff
git log --oneline -5
```

Review all modified, deleted, and untracked files. Understand what changed and why.

### 2. Group changes into atomic commits
Identify logical groupings. Examples of good atomic units:
- A new feature in one module + its tests
- A bug fix in one function + its test update
- A config or tooling change (e.g. `pyproject.toml`)
- A documentation-only change

Do **not** lump unrelated changes into one commit.

### 3. Commit each group
For each logical group:
1. Stage only the relevant files with `git add <file> ...` — never use `git add -A` or `git add .`
2. Write a clear, imperative commit message that says *what* changed and *why*
3. Append the co-author trailer

Commit message format:
```
<imperative summary under 72 chars>

<optional body if more context is needed>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Use a HEREDOC to pass the message:
```bash
git commit -m "$(cat <<'EOF'
<message here>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

### 4. Push
After all commits are made:
```bash
git push
```

### 5. Report
Summarise each commit (hash + message) and confirm the push succeeded.
