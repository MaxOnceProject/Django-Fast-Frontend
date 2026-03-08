---
applyTo: "**/*.py,**/*.html,**/*.css,**/*.yml"
---
<!-- managed-by: blitz -->

## Role
Passive maintenance only. Patch Blitz-managed artifacts when source changes warrant it. Not a daemon.

## Watch Map
Patch when: new/removed/renamed files or modules · changed public interfaces or exported APIs · architectural changes · new or removed dependencies · changed entry points or URL patterns · changed validation commands.

Skip: whitespace-only · comment-only · minor internal refactors · test-only changes not affecting responsibilities or boundaries · `.git` · `__pycache__` · migrations · `agent-output/` · `.github/agents/**`.

## Map: source change → artifact
- New/removed/renamed file → `agent.md` scopes table + relevant `{scope}/agent.md` key files table
- Changed `frontend/__init__.py` exports → `frontend/agent.md` + `frontend-core.instructions.md`
- Changed `frontend/views.py` flows → `frontend/agent.md` call chain + `frontend-core.instructions.md` arch flow
- Changed `setup.py` version → `agent.md` + `copilot-instructions.md` + `project-config.instructions.md`
- New/removed dependency → `agent.md` deps table + `frontend-core.instructions.md`
- New/changed template → `frontend-templates.instructions.md` hierarchy
- Changed `Dockerfile` / `docker-compose.yml` / `requirements.txt` → `copilot-instructions.md` commands table + `project/agent.md`
- Changed `README.md` / `docs/` → relevant `agent.md` + `.instructions.md` knowledge sections

## Surgical Rules
Read changed file + relevant artifact. Patch only the affected row/section. Preserve `## Overrides` and `<!-- blitz:preserve -->` blocks. Never full-file rewrite.
