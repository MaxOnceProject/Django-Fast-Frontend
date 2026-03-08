---
applyTo: "app/**,app2/**"
---
<!-- managed-by: blitz -->

## Context
Read `agent.md` + `app/agent.md` (or `app2/agent.md`) for key files and registration patterns.

## Scope
Demo/example Django apps (`app/`, `app2/`) showing canonical library usage. Excluded from PyPI package.
`app/` = full-featured example; `app2/` = minimal registration example.

## DO / NEVER
- **DO** keep `app/frontend.py` as a comprehensive example of all `ModelFrontend` features
- **DO** write integration tests covering auth flow + access control in `app/tests/test_frontend.py`
- **DO** use `@pytest.mark.django_db` on every test that touches the database
- **NEVER** add business logic to demo apps — they exist to demonstrate the library
- **NEVER** use `fields = "__all__"` even in demo registrations

## Common Tasks
- **New ModelFrontend feature**: demonstrate it in `app/frontend.py` first
- **New test**: add to `app/tests/test_frontend.py` with `@pytest.mark.django_db`

## Testing
```bash
python -m pytest app/tests/ -v
python -m pytest app2/ -v
```

## Gotchas
- `app/tests/test_frontend.py` uses pytest-style `assert`; `frontend/tests/test_security.py` uses `unittest`-style `self.assert*` — do not mix styles within a file
- Sidebar navigation groups are derived automatically from `AppConfig.verbose_name` — `app` uses `'Content'`, `app2` uses `'Directory'`. To customise group order or hide models, call `frontend.site.set_sidebar_navigation()` in any frontend module loaded during autodiscovery
