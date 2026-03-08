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
| `requirements.txt` | Demo/test harness dependency pins for Django 5.2, pytest 9, and Playwright browser tests | dependency list |
| `conftest.py` | pytest config; sets `DJANGO_SETTINGS_MODULE` (6 lines) | `pytest_configure()` |
| `pytest.ini` | pytest marker registration for the `ui` browser suite | `ui` marker |
| `Dockerfile` | Python 3.12-slim image; installs requirements, Playwright Chromium runtime, and editable package for the container | — |
| `docker-compose.yml` | Dev server plus `ui-test` service for Docker end-to-end runs with mounted source and env vars | — |

## Dependencies
- Internal: imports `frontend.site.urls` and `frontend.accounts.urls` in `project/urls.py`
- External: `setup.py install_requires` for the package, `requirements.txt` for the demo/test harness

## Change Guidance
- Runtime floor or dependency change → sync `README.md`, `setup.py`, `requirements.txt`, `Dockerfile`, `/agent.md`, and `.github/copilot-instructions.md`
- Docker UI workflow change → sync `docker-compose.yml`, `README.md`, `/agent.md`, and this file
- URL/bootstrap change → update `project/urls.py` or `project/settings.py`; validate against `FRONTEND_AUTO_URL` duplication

## Testing
```bash
docker compose run --rm -T ui-test  # Docker Playwright E2E suite with clean db, seeded data, and saved screenshots
```
