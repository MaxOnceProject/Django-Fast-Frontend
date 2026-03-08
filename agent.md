<!-- managed-by: blitz -->
# Django Fast Frontend — Knowledge Index

## Project
PyPI-installable Django library for admin-like CRUD frontend interfaces. Mirrors Django Admin API
(`ModelAdmin` → `ModelFrontend`) but renders a Bootstrap 5 frontend instead of the admin panel.
Version: 0.4.1 | Python 3.8+ | Django 4.2+ | Tests: pytest + pytest-django + factory-boy

## Reading Order
1. **This file** — scope map, boundaries, architecture
2. `frontend/agent.md` — core library scope, key files, change guidance [verified]
3. `app/agent.md` — full-featured demo app scope, registration examples [verified]
4. `app2/agent.md` — minimal demo app scope [verified]
5. `project/agent.md` — project config, packaging, deployment [verified]

## Scopes
| Scope | Path | Description | agent.md |
|---|---|---|---|
| `frontend-core` | `frontend/` | Core library: registry, views, forms, accounts, templatetags | `frontend/agent.md` |
| `demo-app` | `app/` | Full-featured demo app with integration tests | `app/agent.md` |
| `demo-app-minimal` | `app2/` | Minimal pass-through demo app | `app2/agent.md` |
| `project-config` | `project/`, `setup.py`, `Dockerfile`, `conftest.py` | Django project config, packaging, deployment | `project/agent.md` |
| `frontend-templates` | `frontend/templates/` | HTML templates: base, site, home, partials, accounts | — |

## Architecture
```
HTTP → project/urls.py → frontend.site.urls
  → FrontendModelView.get/post(app_name, model_name, action, id)
    → site.get_model_config(model) → ModelFrontend instance
      → queryset / form / search / filter / sort / pagination
        → site.http_response(request, context, template) → render HTML

Startup: FrontendConfig.ready() → site.autodiscover_modules()
  → imports {app}/frontend.py → @register(Model) → site._registry[model]

Accounts: project/urls.py → frontend.accounts.urls → urlpatterns_account
  → FrontendLoginView / FrontendSignUpView / FrontendPassword*View

Config: frontend/frontend.py auto-registers Frontend(Config) at import
  → if login_required + authentication → registers AccountFrontend
```

## Scope Boundaries
- **`frontend/`** — the PyPI package; all changes affect published API [verified: `setup.py` excludes app/app2/project]
- **`app/`** — excluded from PyPI; full-featured usage example and integration test host [verified]
- **`app2/`** — excluded from PyPI; minimal registration example [verified]
- **`frontend/templates/`** — rendered by `FrontendSite.http_response()`; use `django_bootstrap5`
- **`project/`** — dev/demo harness only; never distributed [verified]

## External Dependencies
| Package | Purpose | Required |
|---|---|---|
| `django>=4.2` | Web framework, ORM, auth | Yes |
| `django_bootstrap5>=24.3` | Bootstrap 5 template rendering | Yes |
| `pytest`, `pytest-django`, `factory-boy` | Test stack | Dev only |

## Configuration Reference
| Setting | Default | Read In |
|---|---|---|
| `FRONTEND_LOGIN_REQUIRED` | `True` | `frontend/frontend.py` |
| `FRONTEND_SIDEBAR` | `True` | `frontend/frontend.py` |
| `FRONTEND_BRAND` | `'Django Fast Frontend'` | `frontend/frontend.py` |
| `FRONTEND_LOGO` | `'img/django-fast-frontend-logo.png'` | `frontend/frontend.py` |
| `FRONTEND_CUSTOM_CSS` | `'css/custom.css'` | `frontend/frontend.py` |
| `FRONTEND_DESCRIPTION` | `''` | `frontend/frontend.py` |
| `FRONTEND_AUTO_URL` | — | `frontend/apps.py` |
| `FRONTEND_URL` | `''` | `frontend/apps.py` |
| `FRONTEND_SITE_CLASS` | `None` | `frontend/sites/site.py` |

## Maintenance Notes
- **Blitz-managed artifacts**: `/agent.md`, `frontend/agent.md`, `app/agent.md`, `app2/agent.md`, `project/agent.md`
- Patch triggers: new/renamed files, changed public API, new/removed deps, architectural changes
- Skip: whitespace-only edits, comment-only edits, `__pycache__`, migrations, `agent-output/`
