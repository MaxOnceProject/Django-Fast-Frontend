<!-- managed-by: blitz -->
## Read First
See `/agent.md` for project scope and architecture. See `app/agent.md` for full-featured demo patterns.

## Responsibilities
Minimal demo app showing pass-through `ModelFrontend` registration with `django-fast-frontend`.
Not distributed in the PyPI package. Demonstrates decorator registration with an intentionally empty
`ModelFrontend` subclass; this is a historical minimal example, while new code should still prefer
explicit `fields` declarations.

## Boundaries
- **May change**: model fields, frontend config attributes
- **Must stay aligned**: registration pattern must reflect library conventions
- **Out of scope**: `frontend/` (core library), `app/` (full-featured demo), `project/` (config)

## Key Files
| File | Role | Key Exports |
|---|---|---|
| `app2/admin.py` | Django Admin mirror for the demo model | `PeopleAdmin` |
| `app2/models.py` | `People` model (name, title, birth_date) (11 lines) | `People` |
| `app2/frontend.py` | Minimal `PeopleFrontend` (pass-through empty subclass, 13 lines) | `PeopleFrontend` |
| `app2/apps.py` | AppConfig (7 lines); `verbose_name = 'Directory'` drives sidebar group label | `AppConfig` |

## Change Guidance
- Keep `app2/frontend.py` minimal unless you are intentionally expanding the example
- If you add forms or actions here, declare `fields` or `list_display` explicitly before changing behavior
