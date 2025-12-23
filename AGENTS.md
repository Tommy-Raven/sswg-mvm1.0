# Agent Guidelines (Root Scope)

- This repository is treated as read-only for QA unless a task explicitly permits edits or test execution.
- Use `rg` for searching; avoid `ls -R` or `grep -R`.
- Do not validate commands with `echo $?`; rely on actual command outputs.
- When reporting issues or improvements, append a `task-stub` block immediately after each issue description with clear, actionable steps.
- Final responses must be concise, include citations where relevant, and prefix any test/check commands with emojis: ✅ pass, ⚠️ warning/limitation, ❌ fail.
- For frontend visual changes, capture screenshots via the browser tool and cite the artifact.
- Honor instruction precedence: system > developer > user > AGENTS, with deeper `AGENTS.md` overriding parent scopes.
- If any placeholders or TODOs remain in the final diff, include a **Notes** section after Testing; omit the section otherwise.
- When changes are made: commit them, then invoke `make_pr` with an appropriate title and body; never leave committed changes without calling `make_pr`, and never call `make_pr` without commits.
