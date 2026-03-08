<!-- managed-by: blitz -->
## Read First
See `/agent.md` for project scope and architecture. See `app/agent.md` for full-featured demo patterns.

## Responsibilities
Minimal demo app showing pass-through `ModelFrontend` registration with `django-fast-frontend`.
Not distributed in the PyPI package. Demonstrates that a working frontend requires only a model and
a minimal `ModelFrontend` subclass with explicit `fields`.

## Boundaries
- **May change**: model fields, frontend config attributes
- **Must stay aligned**: registration pattern must reflect library conventions
- **Out of scope**: `frontend/` (core library), `app/` (full-featured demo), `project/` (config)

## Key Files
| File | Role | Key Exports |
|---|---|---|
| `app2/models.py` | `People` model (name, title, birth_date) (11 lines) | `People` |
| `app2/frontend.py` | Minimal `PeopleFrontend` (pass-through, 13 lines) | `PeopleFrontend` |
| `app2/apps.py` | AppConfig (7 lines); `verbose_name = 'Directory'` drives sidebar group label | `AppConfig` |
