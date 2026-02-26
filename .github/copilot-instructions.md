# Copilot Instructions — Django Fast Frontend

## Context Acceleration
Pre-analyzed context files exist — read these BEFORE exploring source code:
- `.github/agents/context/structure.md` — file tree, key files with line counts, entry points, commands
- `.github/agents/context/logic.md` — request flows, call chains, error paths, silent failures
- `.github/agents/context/patterns.md` — class hierarchies, registration, naming, DO/NEVER rules, template contracts, boilerplate
- `.github/agents/context/links.md` — import graph, external packages, config keys, env vars, API surface

**Lookup**: Need file locations/roles → structure | Need call chains/error paths → logic | Need conventions/how-to → patterns | Need deps/config/APIs → links

These cover ~95% of codebase questions. Only read source files when you need exact implementation details not in the context files. Do NOT re-explore the codebase with search tools for information already covered above.

## Project
Django Fast Frontend is a PyPI-installable Django library that lets developers create admin-like CRUD frontend interfaces for Django models using declarative configuration classes. It mirrors Django Admin's API pattern (`ModelAdmin` → `ModelFrontend`) but renders a Bootstrap 5 frontend instead of the admin panel.

## Stack
| Aspect | Value |
|---|---|
| Language | Python 3.8+ |
| Framework | Django 4.2+ |
| UI | django_bootstrap5 |
| Tests | pytest + pytest-django + factory-boy |
| Container | Docker + docker-compose |
| Package | `django-fast-frontend` v0.3.0 on PyPI |

## Architecture
```
HTTP Request → project/urls.py → frontend.site.urls / frontend.accounts.urls
  → views.FrontendModelView.get/post(app_name, model_name, action, id)
    → site.get_model_config(model) → ModelFrontend instance
      → queryset / form / search / filter / sort / pagination
        → site.http_response(request, context, template) → render HTML
```
Registration (startup): `FrontendConfig.ready()` → `site.autodiscover_modules()` → imports `{app}/frontend.py` → `@frontend.register(Model)` → `site._registry[model]`

## Directory Map
```
frontend/           Core library (the PyPI package)
  sites/            Site registry, ModelFrontend, Config, decorators
  templates/        HTML templates (base, site, home, partials)
  templatetags/     Custom Django template filters
app/, app2/         Demo/example apps using the library
project/            Django project config (settings, urls, wsgi)
```

## Coding Rules
- Always declare `fields` explicitly on `ModelFrontend` — never use `"__all__"`
- Use `@frontend.register(Model)` decorator for model registration
- Use `get_queryset(request)` when overriding querysets for row-level authorization
- Validate action names against `toolbar_button` or `inline_button` before dispatch
- Use `_safe_redirect()` for POST redirects — never trust raw `HTTP_REFERER`
- Mark tests with `@pytest.mark.django_db` when accessing the database
- Follow naming: `{Model}Frontend` for classes, `{app}/frontend.py` for config files
- Keep `ModelFrontend` subclasses declarative — logic goes in overridden methods

## Quick Start: Adding a New Model Frontend
1. Create model in `{app}/models.py`
2. Create/edit `{app}/frontend.py`:
   ```python
   import frontend
   from {app}.models import MyModel

   @frontend.register(MyModel)
   class MyModelFrontend(frontend.ModelFrontend):
       fields = ('field1', 'field2')
       list_display = ('field1', 'field2')
   ```
3. Ensure app is in `INSTALLED_APPS` (autodiscovery requires it)
4. `python manage.py makemigrations {app}` + `python manage.py migrate`
5. Add tests in `{app}/tests/test_frontend.py` with `@pytest.mark.django_db`

## Commands
| Task | Command |
|---|---|
| Run dev server | `docker-compose up` or `python manage.py runserver` |
| Run all tests | `python -m pytest` |
| Run specific tests | `python -m pytest app/tests/ -v` |
| Migrate DB | `python manage.py migrate` |
| Build package | `python setup.py sdist bdist_wheel` |

## Safety
- Never include secrets, API keys, tokens, passwords, or customer data
- Never use `fields = "__all__"` — always declare explicit field lists
- Always check existing patterns before creating new abstractions
- When unsure about data classification or security boundaries, ask
