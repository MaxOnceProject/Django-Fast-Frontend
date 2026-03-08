<!-- managed-by: blitz -->
## Read First
See `/agent.md` for project scope and architecture.

## Responsibilities
Django project configuration, packaging, and deployment. Dev/demo harness only — not distributed
in the PyPI package. Provides settings, URL routing, Docker setup, and test configuration.

## Boundaries
- **May change**: settings values, Docker config, test setup
- **Must stay aligned**: `setup.py` version must match `agent.md` and `copilot-instructions.md`
- **Out of scope**: `frontend/` (core library), `app/`, `app2/` (demo apps)

## Test Commands
```bash
docker-compose run --rm app python -m pytest          # full suite via Docker (preferred)
docker-compose run --rm app python -m pytest path/to/test.py -v  # single file via Docker
python -m pytest                                      # local (requires local env)
```

## Key Files
| File | Role | Key Exports |
|---|---|---|
| `project/settings.py` | Django settings; env var overrides for SECRET_KEY, DEBUG, ALLOWED_HOSTS; FRONTEND_* settings (~150 lines) | `INSTALLED_APPS`, `MIDDLEWARE`, `ROOT_URLCONF`, `DATABASES`, `FRONTEND_CUSTOM_CSS` |
| `project/urls.py` | Root URL config: admin, accounts, frontend site (23 lines) | `urlpatterns` |
| `setup.py` | PyPI packaging; excludes app/app2/project from dist (33 lines) | `setup()` call, `version="0.4.1"` |
| `conftest.py` | pytest config; sets `DJANGO_SETTINGS_MODULE` (6 lines) | `pytest_configure()` |
| `Dockerfile` | Python 3.10 image; installs deps, runs migrate (23 lines) | — |
| `docker-compose.yml` | Dev server on port 8000; mounts source, sets env vars (16 lines) | — |

## Dependencies
- Internal: imports `frontend.site.urls` and `frontend.accounts.urls` in `project/urls.py`
- External: all packages in `requirements.txt` + `setup.py install_requires`
