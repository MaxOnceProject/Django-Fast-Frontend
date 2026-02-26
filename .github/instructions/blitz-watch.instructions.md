---
applyTo: "**/*.py,**/*.html,**/*.css,**/*.js,**/*.ts"
---
## Blitz Watch

After changing source files, patch affected context + instruction files.

Context: `.github/agents/context/{structure,logic,patterns,links}.md`

Map: new/removed/renamed file → structure.md | changed flow/calls → logic.md | changed class/convention → patterns.md | changed import/dep/config → links.md

Do: read changed file + affected context file, make surgical row/section edits only, then patch any `.github/instructions/*.instructions.md` whose applyTo glob covers the changed file. Preserve `## Overrides` verbatim.

Skip: `.gitignore`, `__pycache__`, migrations, `.github/agents/**`, whitespace-only, comments-only.
