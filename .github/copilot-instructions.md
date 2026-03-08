<!-- managed-by: blitz -->
# Copilot Instructions — Django Fast Frontend

## Context Acceleration
**STOP — read `agent.md` files BEFORE exploring source code.**
agent.md files contain 80% of the knowledge you need. Source exploration is for the remaining 20%.
- `agent.md` — scope map, architecture, dependencies, API reference
- `{scope}/agent.md` — key files, call chains, API defaults, change guidance

Only read source files when `agent.md` + auto-loaded `.instructions.md` don't answer your question.

## Project
Django Fast Frontend — PyPI library (`django-fast-frontend` v0.4.1) for declarative admin-like CRUD interfaces.
Mirrors Django Admin (`ModelAdmin` → `ModelFrontend`) but renders Bootstrap 5. Package minimums are Django 4.2+ / Python 3.10+; the demo harness currently targets Django 5.2 on Python 3.12 Docker.

## Stack
| Aspect | Value |
|---|---|
| Language | Python 3.10+ |
| Framework | Django 4.2+ library, Django 5.2+ demo harness |
| UI | django_bootstrap5>=26.2 |
| Tests | pytest>=9.0 + pytest-django>=4.12 + pytest-factoryboy>=2.8.1 + Playwright local and Docker UI smoke tests |
| Container | Docker + docker-compose (Python 3.12-slim image with Playwright Chromium baked in) |

## Scopes
| Scope | Path | agent.md |
|---|---|---|
| `frontend-core` | `frontend/` | `frontend/agent.md` |
| `demo-app` | `app/` | `app/agent.md` |
| `demo-app-minimal` | `app2/` | `app2/agent.md` |
| `project-config` | `project/`, `manage.py`, `setup.py`, `requirements.txt`, `Dockerfile`, `docker-compose.yml` | `project/agent.md` |
| `frontend-templates` | `frontend/templates/` | — |

## Coding Rules
- **DO** declare `fields` explicitly on `ModelFrontend` — never `"__all__"`
- **DO** use `@frontend.register(Model)` decorator for registration
- **DO** use `get_queryset(request)` override for row-level authorization
- **DO** whitelist actions via `toolbar_button` / `inline_button` before `getattr` dispatch
- **DO** use `_safe_redirect()` for all POST redirects — never trust raw `HTTP_REFERER`
- **DO** mark DB-touching tests with `@pytest.mark.django_db`
- **NEVER** commit secrets, tokens, passwords, or API keys in source files

## Commands
| # | Task | Command | Source |
|---|---|---|---|
| 1 | Setup (Docker) | `docker-compose up --build` | Dockerfile, docker-compose.yml |
| 2 | Setup (local) | `pip install -r requirements.txt && pip install -e .` | requirements.txt, setup.py |
| 3 | Dev server | `docker-compose up` | docker-compose.yml |
| 4 | Run all tests | `docker-compose run --rm app python -m pytest` | conftest.py |
| 4a | Run all tests (local) | `python -m pytest` | conftest.py |
| 4b | Run UI smoke tests (local) | `python -m pytest -m ui app/tests/test_browser_ui.py -v` | pytest.ini |
| 4c | Run UI smoke tests (Docker) | `docker compose run --rm -T ui-test` | docker-compose.yml |
| 5 | Run single test | `docker-compose run --rm app python -m pytest path/to/test.py -v` | conftest.py |
| 5a | Install Playwright browser (local) | `python -m playwright install chromium` | requirements.txt |
| 6 | Migrate (Docker) | `docker-compose run --rm app python manage.py migrate` | docker-compose.yml |
| 6a | Migrate (local) | `python manage.py migrate` | manage.py |
| 7 | Build package | `python setup.py sdist bdist_wheel` | setup.py |
| 8 | Access demo | `docker-compose up` → `http://localhost:8000` | docker-compose.yml |
| 9 | Check errors | `python -m pytest --tb=short` | conftest.py |
