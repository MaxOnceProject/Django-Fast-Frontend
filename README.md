# Django Fast Frontend

**Turbocharge front-end creation with Django-admin-like configuration.**

![Version](https://img.shields.io/badge/version-0.4.1-blue)
![Django](https://img.shields.io/badge/django-%3E%3D4.2-green)
![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

django-fast-frontend is a Django package for building admin-like CRUD frontends from Django models using declarative configuration.

It is best suited for internal tools, back-office dashboards, content management screens, and simple model-driven frontends where you want Django-native forms, auth, and templates without building a separate SPA.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements & Installation](#requirements--installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
  - [Core Concepts](#core-concepts)
  - [Examples](#examples)
  - [CRUD and Actions](#crud-and-actions)
  - [Authentication and Authorization](#authentication-and-authorization)
- [Configuration](#configuration)
- [Limitations & Trade-offs](#limitations--trade-offs)
- [Contributing & Development](#contributing--development)
- [License & Further Reading](#license--further-reading)

## Overview

You define a `ModelFrontend` subclass for each model you want to expose, register it, and the package renders:

- a frontend home page
- app-level landing pages
- model list pages
- generated add and change forms
- delete actions
- search, filter, sort, and pagination UI
- optional account pages for login, signup, logout, and password flows

The package uses standard Django models, forms, templates, auth views, and routing. It is admin-like, not admin-compatible.

**Why Use It:**
Use django-fast-frontend when you want:

- a CRUD frontend for Django models without building separate views for every model
- a simpler, more user-facing alternative to Django Admin for internal workflows
- Bootstrap-based pages that still feel like normal Django templates
- a declarative setup where most behavior is controlled with attributes instead of repeated boilerplate

It is not the right tool if you need full Django Admin parity, complex admin inlines, or a heavily customized frontend application.

## Features

- Declarative per-model configuration with `ModelFrontend`
- Bootstrap 5 UI with responsive table and card layouts
- Sidebar or navbar navigation
- Search, filter, sort, and pagination
- Safe redirects for POST flows
- Action dispatch limited to explicitly declared methods
- Row-level authorization hook via `get_queryset(request)`
- Forms never default to `fields = "__all__"`
- Non-editable model fields in `fields` render read-only on change pages
- Built-in account pages using Django auth views

## Requirements & Installation

**Package requirements:**
- Python 3.10+
- Django 4.2+
- `django_bootstrap5>=26.2`

*(This repository's demo and test harness currently target Django 5.2 on Python 3.12.)*

```bash
pip install django-fast-frontend
```

Add the required apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # Django apps...
    "django_bootstrap5",
    "frontend",
    # your apps...
]
```

## Quick Start

### 1. Add the URLs

Use the same pattern as the demo project:

```python
from django.urls import path
import frontend


urlpatterns = [
    path("accounts/", frontend.accounts.urls),
    path("", frontend.site.urls),
]
```

This package exposes URL tuples directly, so `path(..., frontend.site.urls)` is the expected pattern.

### 2. Register a model frontend

Create `frontend.py` in one of your Django apps:

```python
import frontend
from app.models import Author


@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
    list_display = ("name", "title")
    search_fields = ("name", "title")
    sortable_by = ("name", "title")
```

That gives you:

- a frontend home page
- an app landing page
- a model list page
- search and sorting for the configured fields
- a generated form for the configured fields

### 3. Run your project

Once Django starts, the `frontend` app autodiscovers `frontend.py` modules from installed apps and registers the frontends it finds.

## Usage Guide

### Core Concepts

#### `ModelFrontend`

`ModelFrontend` is the main extension point. You define what fields to show, which actions are available, how search and filtering behave, and whether the model should render as cards or a table.

#### Registration and autodiscovery

The package scans installed apps for `frontend.py` modules during Django startup. Any classes registered with `@frontend.register(Model)` are added to the site registry automatically.

#### Request flow

At startup:

1. `FrontendConfig.ready()` autodiscovers `frontend.py` modules.
2. `@frontend.register(Model)` stores each frontend on the site registry.
3. The default global config is registered.
4. Account links are registered when authentication is active.

At request time:

1. The package resolves the model from the URL.
2. It instantiates the matching `ModelFrontend`.
3. It builds the queryset via `get_queryset(request)`.
4. It applies search, filter, sort, and pagination.
5. It renders either the table view or card view.

#### URL structure

Main frontend routes:

- `/`
- `/favicon.ico`
- `/<app_name>/`
- `/<app_name>/<model_name>/`
- `/<app_name>/<model_name>/<action>`
- `/<app_name>/<model_name>/<action>/<id>`

Account routes:

- `/accounts/login/`
- `/accounts/signup/`
- `/accounts/logout/`
- `/accounts/password_change/`
- `/accounts/password_change/done/`
- `/accounts/password_reset/`
- `/accounts/password_reset/done/`
- `/accounts/reset/<uidb64>/<token>/`
- `/accounts/reset/done/`

### Examples

#### Minimal example

```python
import frontend
from app.models import Author


@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
    list_display = ("name", "title")
```

#### Full-featured example

The repository's `app/frontend.py` demonstrates a more complete setup:

```python
@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
    login_required = False
    list_display = ("name", "title")
    inline_button = ("check", "uncheck")
    cards = True
    list_filter = ("name", "title")
    search_fields = ("name", "title", "birth_date")
    toolbar_button = ("everything", "everything_everything")
    sortable_by = ("name", "title")
```

This shows the intended “full-featured” usage pattern.

#### Historical minimal demo app

The repository's `app2/frontend.py` keeps a deliberately minimal example:

```python
@frontend.register(People)
class PeopleFrontend(frontend.ModelFrontend):
    pass
```

This still demonstrates registration, but for real projects you should prefer explicit `fields` or `list_display`.

### CRUD and Actions

#### Built-in CRUD actions

The package supports three built-in mutating actions:

- `table_add`
- `table_change`
- `table_delete`

They are controlled by:

- `add_permission`
- `change_permission`
- `delete_permission`

#### Toolbar actions

Toolbar actions are methods declared in `toolbar_button` and invoked with no arguments.

```python
@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
    toolbar_button = ("rebuild_index",)

    def rebuild_index(self):
        print("rebuilding")
```

To customize the button text, attach action metadata with `@frontend.action`.

```python
@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
    toolbar_button = ("rebuild_index",)

    @frontend.action(description="Rebuild Search Index")
    def rebuild_index(self):
        print("rebuilding")
```

Without `description`, the package falls back to the Django-admin-like default label derived from the method name.

#### Inline actions

Inline actions are methods declared in `inline_button` and invoked with the object instance.

```python
@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
    inline_button = ("publish",)

    def publish(self, obj):
        obj.is_published = True
        obj.save(update_fields=["is_published"])
```

Inline actions support the same label metadata.

```python
@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
    inline_button = ("publish",)

    @frontend.action(description="Publish Now")
    def publish(self, obj):
        obj.is_published = True
        obj.save(update_fields=["is_published"])
```

Only actions explicitly listed in `toolbar_button` or `inline_button` are dispatched.

#### Readonly and non-editable fields

Use `readonly_fields` for editable model fields that should still render as form controls on the change page but remain non-editable in the browser.

If a Django model field is itself non-editable, for example `auto_now_add=True` or `editable=False`, you can still include it in `fields`. django-fast-frontend will keep it out of the generated `ModelForm` and render its current value as read-only content on the change page.

```python
@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title", "created_at")
    readonly_fields = ("created_at",)
```

Non-editable model fields are not shown on the add page because there is no persisted value to display yet, and they are never submitted back through the generated form.

#### Search, filter, sort, and pagination

Search:

- driven by `search_fields`
- uses case-insensitive `icontains`
- query parameter: `q`

Filter:

- driven by `list_filter`
- values come from field choices or distinct database values
- query parameters use the field names directly

Sort:

- driven by `sortable_by`
- query parameter: `s`
- descending sort uses `-field_name`

Pagination:

- driven by `list_per_page`
- query parameter: `page`
- unordered querysets are normalized with `order_by("pk")` before pagination

### Authentication and Authorization

Authentication is required by default.

This is controlled by the global config and per-model `login_required` flags.

To use the built-in account pages, include:

```python
path("accounts/", frontend.accounts.urls)
```

Important current behavior:

- the package does not read a `FRONTEND_AUTHENTICATION` setting
- auth availability is inferred from Django auth backends plus the presence of the `account_login` URL
- logout is POST-only and redirects to `/` by default

If you want anonymous access for one model, disable it on that frontend:

```python
@frontend.register(Author)
class PublicAuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
    login_required = False
```

The demo app uses exactly this pattern in `app/frontend.py`.

Use `get_queryset(request)` to scope data per user.

```python
@frontend.register(Invoice)
class InvoiceFrontend(frontend.ModelFrontend):
    fields = ("number", "status", "total")
    list_display = ("number", "status", "total")

    def get_queryset(self, request=None):
        queryset = super().get_queryset(request)
        if request and not request.user.is_superuser:
            queryset = queryset.filter(owner=request.user)
        return queryset
```

This hook is important because object lookups for change, delete, and inline actions use this queryset.

## Configuration

Supported settings:

```python
FRONTEND_LOGIN_REQUIRED = True
FRONTEND_SIDEBAR = True
FRONTEND_BRAND = "Django Fast Frontend"
FRONTEND_LOGO = "img/django-fast-frontend-logo.png"
FRONTEND_CUSTOM_CSS = "css/custom.css"
FRONTEND_DESCRIPTION = ""
FRONTEND_AUTO_URL = False
FRONTEND_URL = ""
FRONTEND_SITE_CLASS = None
```

### Branding

```python
FRONTEND_BRAND = "Fast Frontend"
FRONTEND_LOGO = "img/my-logo.png"
FRONTEND_DESCRIPTION = "Internal tools for the content team"
```

### Navigation

Sidebar navigation is enabled by default.

```python
FRONTEND_SIDEBAR = True
```

Disable it to use navbar-only navigation:

```python
FRONTEND_SIDEBAR = False
```

By default, sidebar groups are derived from installed app frontends. Group labels come from `AppConfig.verbose_name`.

In this repository, the demo apps produce these group labels:

- `app` → `Content`
- `app2` → `Directory`

Custom sidebar grouping:

```python
import frontend
from app.models import Author
from app2.models import People


frontend.site.set_sidebar_navigation({
    "Content": [Author],
    "Directory": [People],
})
```

You can also use string model identifiers:

```python
frontend.site.set_sidebar_navigation({
    "Content": ["app.Author"],
    "Directory": ["app2.People"],
})
```

Configured sidebar behavior:

- group order is preserved
- item order is preserved
- only listed models are shown
- invalid or unregistered entries are skipped
- account links stay in the navbar dropdown, not the sidebar

### Custom CSS

`FRONTEND_CUSTOM_CSS` lets you load your own stylesheet on every django-fast-frontend page.

```python
FRONTEND_CUSTOM_CSS = "css/custom.css"
```

In plain terms, this is the easiest way to make the frontend look like it belongs to your project without changing package templates.

Typical use cases:

- change brand colors
- adjust spacing and typography
- style the sidebar or navbar
- make tables denser for internal tools
- highlight buttons, cards, or status values

Where to put the file:

- create a static file in your project or app, for example `static/css/custom.css`
- keep the setting value relative to your static files directory, for example `css/custom.css`

Example project setup:

```python
# settings.py
FRONTEND_CUSTOM_CSS = "css/custom.css"
```

```text
myapp/
  static/
    css/
      custom.css
```

Example `custom.css`:

```css
body {
    background: #f6f8fb;
}

.navbar {
    border-bottom: 1px solid #d9e2ec;
}

.navbar-brand {
    font-weight: 700;
    letter-spacing: 0.02em;
}

.frontend-sidebar .nav-link {
    border-radius: 8px;
}

.frontend-sidebar .nav-link:hover {
    background: #e9f2ff;
}

.frontend-toolbar .btn-primary {
    background: #0f766e;
    border-color: #0f766e;
}
```

How to work with it safely:

- start with small visual changes first
- prefer overriding colors, spacing, and typography before rewriting layout behavior
- inspect the rendered HTML in your browser when targeting specific classes
- keep selectors specific enough to avoid changing unrelated pages in your project

What the setting does not do:

- it does not compile Sass
- it does not automatically create the file for you
- it does not replace Bootstrap, it simply loads your stylesheet after the package assets so your rules can override them

If you need deeper structural changes than CSS can handle, move to custom templates or custom views.

The demo app ships a few ready-made theme files under `app/static/css/`:

- `custom.css`
- `custom-blue.css`
- `custom-purple.css`
- `custom-rgb.css`

The demo project currently uses:

```python
FRONTEND_CUSTOM_CSS = "css/custom-purple.css"
```

### Auto URL wiring

If `FRONTEND_AUTO_URL` is truthy, the app appends `frontend.urls` to your root URLconf at startup.

```python
FRONTEND_AUTO_URL = True
FRONTEND_URL = "portal"
```

That produces a frontend mounted under `/portal/`.

Notes:

- leading slashes are normalized away
- a trailing slash is added automatically when needed
- do not combine `FRONTEND_AUTO_URL` with manual inclusion of the same frontend URLs

### Custom site class

You can replace the default site singleton by providing `FRONTEND_SITE_CLASS`.

## Limitations & Trade-offs

django-fast-frontend intentionally does not support most advanced Django Admin APIs.

Examples of unsupported admin concepts:

- `fieldsets`
- `inlines`
- `autocomplete_fields`
- `list_editable`
- `prepopulated_fields`
- `save_model()` and related admin hooks

Use custom forms, custom methods, or custom views when you need behavior outside the supported `ModelFrontend` surface.

## Contributing & Development

### Repository Layout

This repository contains both the published package and a demo harness:

- `frontend/`: the actual PyPI package
- `app/`: a full-featured demo app showing search, filter, sort, cards, toolbar actions, inline actions, and a public frontend override
- `app2/`: a minimal demo app showing pass-through registration with an intentionally empty frontend subclass
- `project/`: the local demo Django project used for development and testing

Only `frontend/` is distributed in the published package. The demo apps and project are examples, not part of the installable library.

### Development Setup

For local development in this repository:

```bash
pip install -r requirements.txt
pip install -e .
```

The demo project reads these environment variables:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_SETTINGS_MODULE`

Example:

```bash
export DJANGO_SECRET_KEY='your-secret-key'
export DJANGO_DEBUG='False'
export DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1'
export DJANGO_SETTINGS_MODULE='project.settings'
```

The demo project already wires:

- `path("accounts/", frontend.accounts.urls)`
- `path("", frontend.site.urls)`

Run tests locally:

```bash
python -m pytest
```

Install Playwright browsers for the local UI smoke suite:

```bash
python -m playwright install chromium
```

Run the local browser smoke suite:

```bash
python -m pytest -m ui app/tests/test_browser_ui.py -v
```

The Playwright suite covers a small smoke path for login, navigation, search, sort, and add/change interactions. For end-to-end validation in this repository, the Docker `ui-test` service is the primary workflow.

Run the Docker end-to-end UI suite with a clean database, fresh migrations, seeded demo data, and persisted screenshots:

```bash
docker compose run --rm -T ui-test
```

The Docker UI service deletes `db.sqlite3`, runs `migrate`, seeds deterministic demo data, starts Django, runs the Playwright suite, and stores screenshots plus the Django server log under `test-results/` inside the project.

Run tests with Docker:

```bash
docker-compose run --rm app python -m pytest
```

Run the Docker browser smoke suite:

```bash
docker compose run --rm -T app python -m pytest -m ui app/tests/test_browser_ui.py -v
```

The Docker image now bakes in Chromium and the required Playwright system dependencies at build time, so the UI suite does not need a separate browser install step inside the running container.

Run migrations:

```bash
python manage.py migrate
```

Run the demo server with Docker:

```bash
docker-compose up --build
```

The demo server is exposed at `http://localhost:8000`.

## License & Further Reading

Released under the **MIT License**.

The repository also includes a full current-state specification in `SPEC.md`. This README is the practical guide. `SPEC.md` is the detailed implementation reference.
