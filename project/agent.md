<!-- managed-by: blitz -->
## Read First
See `/agent.md` for project scope and architecture.

## Responsibilities
Django project configuration, packaging, and deployment. Dev/demo harness only — not distributed
in the PyPI package. Provides settings, URL routing, packaging metadata, Docker setup, and test
configuration for the demo harness.

## Boundaries
- **May change**: settings values, Docker config, test setup
- **Must stay aligned**: `setup.py` version must match `agent.md` and `copilot-instructions.md`
- **Out of scope**: `frontend/` (core library), `app/`, `app2/` (demo apps)

## Key Files
| File | Role | Key Exports |
|---|---|---|
| `project/settings.py` | Django settings; env var overrides for SECRET_KEY, DEBUG, ALLOWED_HOSTS; FRONTEND_* settings (~150 lines) | `INSTALLED_APPS`, `MIDDLEWARE`, `ROOT_URLCONF`, `DATABASES`, `FRONTEND_CUSTOM_CSS` |
| `project/urls.py` | Root URL config: admin, accounts, frontend site (23 lines) | `urlpatterns` |
| `project/asgi.py` | ASGI entrypoint for deployments or async servers | `application` |
| `project/wsgi.py` | WSGI entrypoint for classic Django hosting | `application` |
| `manage.py` | Django management command entrypoint | `main()` |
| `setup.py` | PyPI packaging; excludes app/app2/project from dist (33 lines) | `setup()` call, `version="0.4.1"` |
| `requirements.txt` | Demo/test harness dependency pins for Django 5.2 and pytest 9 | dependency list |
| `conftest.py` | pytest config; sets `DJANGO_SETTINGS_MODULE` (6 lines) | `pytest_configure()` |
| `Dockerfile` | Python 3.12-slim image; installs requirements and editable package for the container | — |
| `docker-compose.yml` | Dev server on port 8000; runs migrate on start, mounts source, sets env vars | — |

## Dependencies
- Internal: imports `frontend.site.urls` and `frontend.accounts.urls` in `project/urls.py`
- External: `setup.py install_requires` for the package, `requirements.txt` for the demo/test harness

## Change Guidance
- Runtime floor or dependency change → sync `README.md`, `setup.py`, `requirements.txt`, `Dockerfile`, `/agent.md`, and `.github/copilot-instructions.md`
- URL/bootstrap change → update `project/urls.py` or `project/settings.py`; validate against `FRONTEND_AUTO_URL` duplication
