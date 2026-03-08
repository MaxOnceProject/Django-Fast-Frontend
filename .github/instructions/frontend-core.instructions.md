---
applyTo: "frontend/**/*.py"
---
<!-- managed-by: blitz -->

## Context
Read `agent.md` + `frontend/agent.md` for architecture, key files, and change guidance.

## Scope
Core library (`frontend/`) distributed as `django-fast-frontend` on PyPI. Changes here affect the published package.

## DO / NEVER
- **DO** keep `ModelFrontend` declarative — attributes + overrideable methods, no class-level logic
- **DO** use `get_queryset(request)` as the row-level authorization override point
- **DO** call `super().ready()` before `autodiscover_modules()` in `FrontendConfig.ready()`
- **DO** add a security test to `frontend/tests/test_security.py` for any new action dispatch path
- **NEVER** mutate `site._registry` directly — use `site.register()` or `@register`
- **NEVER** bypass `_check_global_auth()` or `_check_model_auth()` in views
- **NEVER** `getattr`-dispatch without checking against `toolbar_button` / `inline_button` first
- **NEVER** use `fields = "__all__"` on any `ModelFrontend` subclass

## Common Tasks
- **New ModelFrontend attribute**: add to `sites/model.py` class body
- **New URL**: add to `frontend/urls.py`
- **New view**: add to `frontend/views.py`; add security test in `frontend/tests/test_security.py`
- **Changed public export**: update `frontend/__init__.py`

## Testing
```bash
python -m pytest frontend/tests/ -v   # unit + security
python -m pytest app/tests/ -v        # integration
python -m pytest                      # full suite
```

## Gotchas
- `frontend/frontend.py` is the auto-registered `Config` class — it auto-imports from itself via `frontend/__init__.py`; this soft-circular import is intentional
- `FRONTEND_AUTO_URL` dynamically appends to ROOT_URLCONF; combine with `FRONTEND_URL` to set the prefix; test with `project/urls.py` excluded if using this mode
- `FRONTEND_SITE_CLASS` in `settings.py` replaces the `FrontendSite` singleton — custom subclass must exist before autodiscovery runs in `FrontendConfig.ready()`
