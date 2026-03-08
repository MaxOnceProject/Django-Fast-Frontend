---
applyTo: "project/**,setup.py,Dockerfile,docker-compose.yml,conftest.py"
---
<!-- managed-by: blitz -->

## Context
Read `agent.md` + `project/agent.md` for key files and configuration reference.

## Scope
Django project config, packaging, deployment, and test setup. Dev/demo harness only — not distributed.

## Environment Variables
| Variable | Purpose | Read In |
|---|---|---|
| `DJANGO_SECRET_KEY` | Secret key override | `project/settings.py` |
| `DJANGO_DEBUG` | Toggle debug mode | `project/settings.py` |
| `DJANGO_ALLOWED_HOSTS` | CSV of allowed hosts | `project/settings.py` |
| `DJANGO_SETTINGS_MODULE` | Settings module path | Django internals, `conftest.py` |

## Frontend Django Settings
| Setting | Purpose | Read In |
|---|---|---|
| `FRONTEND_AUTO_URL` | Auto-append frontend URL patterns at startup | `frontend/apps.py` |
| `FRONTEND_URL` | URL prefix used when `FRONTEND_AUTO_URL` is set | `frontend/apps.py` |
| `FRONTEND_SITE_CLASS` | Custom `FrontendSite` subclass to use as singleton | `frontend/sites/site.py` |
| `FRONTEND_LOGIN_REQUIRED` | Default login requirement for the site | `frontend/frontend.py` |
| `FRONTEND_SIDEBAR` | Show sidebar navigation (`True`) or navbar-only mode (`False`) | `frontend/frontend.py` |
| `FRONTEND_BRAND` | Site brand name shown in navbar | `frontend/frontend.py` |
| `FRONTEND_LOGO` | Logo image path | `frontend/frontend.py` |
| `FRONTEND_CUSTOM_CSS` | Custom CSS file path | `frontend/frontend.py` |
| `FRONTEND_DESCRIPTION` | Site description | `frontend/frontend.py` |

## DO / NEVER
- **DO** exclude `app`, `app2`, `project` from `setup.py` `find_packages()`  — they are not part of the PyPI package
- **DO** set `DJANGO_SECRET_KEY` via environment variable in production — never commit a real secret
- **NEVER** set `DEBUG=True` in production environments
- **NEVER** add URLs to `project/urls.py` that belong in `frontend/urls.py`

## Common Tasks
- **Add FRONTEND_* setting**: add to `project/settings.py`
- **Bump version**: update `setup.py` + `agent.md` + `copilot-instructions.md`

## Testing
```bash
docker-compose run --rm app python -m pytest                      # full suite via Docker (preferred)
docker-compose run --rm app python -m pytest path/to/test.py -v  # single file via Docker
python -m pytest                                                  # full suite (local env)
docker-compose up                                                 # dev server on port 8000
python manage.py migrate                                          # apply migrations
```

## Test Results (last run: 2026-03-08)
- **54 passed**, 0 warnings in 3.01s
- Python 3.12.13 | pytest-9.0.2 | Django 5.2.12
- Platform: linux (container)
- Suites: `app/tests/test_frontend.py`, `frontend/tests/test_security.py`, `frontend/tests/test_sidebar.py`

## Gotchas
- `DJANGO_ENVIRONMENT` env var is set in `Dockerfile`/`docker-compose.yml` but **not read** in `settings.py` [potential dead code]
- `FRONTEND_AUTO_URL` in `settings.py` dynamically appends frontend URLs at startup — conflicts if URL patterns already include `frontend.site.urls`
