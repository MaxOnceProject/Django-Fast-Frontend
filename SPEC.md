# Django Fast Frontend Specification

Version: 0.4.1
Status: Current-state specification derived from implementation and tests as of 2026-03-08.

## 1. Purpose

django-fast-frontend is a Django application that generates admin-like CRUD frontends for Django models using declarative configuration. It mirrors part of the Django admin mental model by letting users define a per-model configuration class, but it renders a Bootstrap 5 frontend instead of using Django Admin.

The package is intended for:

- Internal tools and back-office style frontends.
- Rapid model CRUD interfaces with minimal custom template work.
- Projects that want Django-native models, forms, auth, and templates rather than a separate SPA.

The package is not a full replacement for Django Admin and does not implement the full ModelAdmin API.

## 2. Scope

### 2.1 Distributed Package Scope

The published package consists of the `frontend/` package only. The following are not part of the published PyPI artifact:

- `app/`
- `app2/`
- `project/`

### 2.2 In-Scope Features

- Model registration via decorator or site API.
- Site-wide configuration via a config frontend class.
- Autodiscovery of `frontend.py` modules in installed apps.
- Generated list pages, add pages, change pages, delete actions, toolbar actions, and inline actions.
- Search, filter, sort, and pagination.
- Bootstrap-based HTML templates.
- Optional account URLs and auth-aware navigation.
- Sidebar or navbar model navigation.

### 2.3 Out of Scope

- Django Admin parity.
- Nested inlines, fieldsets, autocomplete fields, bulk admin actions, and most advanced ModelAdmin hooks.
- API endpoints or JSON-first interfaces.
- Rich workflow engines, audit logging, rate limiting, or object history.

## 3. Runtime Requirements

### 3.1 Package Requirements

- Python >= 3.10
- Django >= 4.2
- django_bootstrap5 >= 26.2

### 3.2 Demo and Test Harness Requirements

- Django >= 5.2, < 6.0
- pytest >= 9.0
- pytest-django >= 4.12
- pytest-factoryboy >= 2.8.1
- factory-boy >= 3.3.3

## 4. Package Structure

### 4.1 Public Entry Points

The package re-exports the following symbols from `frontend/__init__.py`:

- `site`
- `FrontendSite`
- `ModelFrontend`
- `Config`
- `AccountFrontend`
- `accounts`
- `register`

### 4.2 Main Modules

- `frontend/apps.py`: AppConfig and startup bootstrap.
- `frontend/frontend.py`: default global config registration and optional account registration.
- `frontend/urls.py`: site and account URL patterns.
- `frontend/views.py`: request handling for CRUD and account views.
- `frontend/forms.py`: dynamic ModelForm generation.
- `frontend/sites/abstract.py`: base site registry and rendering helpers.
- `frontend/sites/site.py`: concrete frontend site singleton.
- `frontend/sites/model.py`: `ModelFrontend` base class.
- `frontend/sites/config.py`: global site config base class.
- `frontend/sites/decorators.py`: `@register` decorator.
- `frontend/templatetags/django_fast_frontend.py`: template filters.

## 5. Core Concepts

### 5.1 Frontend Site

The package uses a singleton site object, exposed as `frontend.site`, to hold all registered model frontends plus special entries for global config and accounts.

Registry keys are:

- Django model classes for model frontends.
- The string `config` for the site config.
- The string `accounts` for account navigation support.

### 5.2 Model Frontend

A `ModelFrontend` subclass declares how a model should be presented and manipulated. The class is intentionally declarative: attributes configure behavior, and a small set of methods may be overridden for customization.

### 5.3 Global Config

The global config is a `Config` subclass registered as the special `config` entry. The default concrete class is `Frontend` from `frontend/frontend.py`.

### 5.4 Account Site

The package also exposes `frontend.accounts.urls` for login, signup, logout, password change, and password reset flows. These routes are separate from the main model site routes.

## 6. Startup and Registration Lifecycle

### 6.1 App Startup

On Django app startup, `FrontendConfig.ready()` performs the following:

1. Calls `super().ready()`.
2. Runs autodiscovery for `frontend.py` modules in every installed app.
3. Optionally appends `frontend.urls` into the root URLconf if `FRONTEND_AUTO_URL` is truthy.

### 6.2 Autodiscovery Rules

Autodiscovery imports `<app>.frontend` for each installed app. During import, model frontends are typically registered via `@frontend.register(Model)`.

Autodiscovery also scans imported module globals and registers any object that is an instance of `FrontendAbstract`, using its `model` attribute and class.

### 6.3 Default Global Registration

Importing `frontend/frontend.py` registers the default global `Frontend` config if the site registry does not yet contain `config`.

If the registered config has `login_required = True` and the config instance reports `authentication = True`, the package also registers the special `accounts` entry.

## 7. Public API

### 7.1 `frontend.register(models=None, site=None)`

Decorator used as:

```python
import frontend
from myapp.models import Author

@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
```

Behavior:

- Registers the decorated class against the provided model on the default site singleton.
- Returns the original class unchanged.
- The `site` parameter exists in the signature but is not honored by the implementation; registration always targets the imported default site singleton.

### 7.2 `frontend.site.register(model, frontend_class=None)`

Registers a model frontend class instance in the site registry.

Constraints:

- `frontend_class` is required.
- The site stores an instance of the frontend class, not the class itself.

### 7.3 `frontend.site.unregister(model)`

Removes a registered model or special key from the registry.

### 7.4 `frontend.site.urls`

Exposes a Django URL tuple `(urlpatterns, app_name, namespace)` compatible with Django `path()`/`include()` usage.

### 7.5 `frontend.accounts.urls`

Exposes account URL patterns for login and password flows.

## 8. Settings Contract

The following settings are read by the package.

### 8.1 Site Appearance and Behavior

- `FRONTEND_LOGIN_REQUIRED`: default `True`
- `FRONTEND_SIDEBAR`: default `True`
- `FRONTEND_BRAND`: default `Django Fast Frontend`
- `FRONTEND_LOGO`: default `img/django-fast-frontend-logo.png`
- `FRONTEND_CUSTOM_CSS`: default `css/custom.css`
- `FRONTEND_DESCRIPTION`: default empty string

### 8.2 Bootstrap and URL Wiring

- `FRONTEND_AUTO_URL`: if truthy, app startup appends `include('frontend.urls')` to the root URLconf.
- `FRONTEND_URL`: optional prefix used when `FRONTEND_AUTO_URL` is enabled. Leading slash is removed and trailing slash is enforced.
- `FRONTEND_SITE_CLASS`: optional replacement class for the site singleton.

### 8.3 Django Auth Dependencies

Authentication detection depends on:

- `AUTHENTICATION_BACKENDS` being configured.
- The URL resolver containing the named URL `account_login`.

There is no implemented `FRONTEND_AUTHENTICATION` setting in the package code, even though README examples reference it.

## 9. URL Contract

### 9.1 Main Frontend URLs

The main site exposes these routes:

- `/`
- `/favicon.ico`
- `/<app_name>/`
- `/<app_name>/<model_name>/`
- `/<app_name>/<model_name>/<action>`
- `/<app_name>/<model_name>/<action>/<id>`

All routes share the same URL name: `frontend`.

### 9.2 Account URLs

The accounts site exposes:

- `/accounts/login/`
- `/accounts/signup/`
- `/accounts/logout/`
- `/accounts/password_change/`
- `/accounts/password_change/done/`
- `/accounts/password_reset/`
- `/accounts/password_reset/done/`
- `/accounts/reset/<uidb64>/<token>/`
- `/accounts/reset/done/`

### 9.3 Expected Integration

Typical project usage is:

```python
from django.urls import path
import frontend

urlpatterns = [
    path("accounts/", frontend.accounts.urls),
    path("", frontend.site.urls),
]
```

The demo project uses exactly this wiring pattern.

## 10. Request Lifecycle

### 10.1 Home Page

`GET /`:

- Applies the global auth check.
- Builds navbar metadata.
- Renders a home page with cards representing registered models.
- When auth is active, account links are excluded from the home cards.

### 10.2 App Landing Page

`GET /<app_name>/`:

- Applies the global auth check.
- Renders a home page limited to models from the selected app.

### 10.3 Model List Page

`GET /<app_name>/<model_name>/`:

- Applies global and per-model auth checks.
- Resolves the Django model via `apps.get_model(app_name, model_name)`.
- Instantiates the model frontend config for that model.
- Builds the list queryset via `model_config.queryset(request)`.
- Applies search, filter, sort, and pagination.
- Renders either a table or card layout.

### 10.4 Add Page

`GET /<app_name>/<model_name>/table_add`:

- Applies auth checks.
- Builds a blank generated form.
- Renders the form inside the shared model template.

### 10.5 Change Page

`GET /<app_name>/<model_name>/table_change/<id>`:

- Applies auth checks.
- Uses `model_config.get_queryset(request)` for object lookup.
- Pre-populates a generated form with the target object's `__dict__` values.
- Marks configured readonly fields with `readonly` widget attributes.

### 10.6 POST Add

`POST /<app_name>/<model_name>/table_add`:

- Requires `add_permission = True`.
- Validates the generated form.
- Saves on success.
- Redirects with `_safe_redirect()` to the referer if same-host, otherwise to `/<app>/<model>/`.

### 10.7 POST Change

`POST /<app_name>/<model_name>/table_change/<id>`:

- Requires `change_permission = True`.
- Uses `get_queryset(request)` for object lookup.
- Binds the generated form to the instance.
- Saves on success.
- Redirects with `_safe_redirect()`.

### 10.8 POST Delete

`POST /<app_name>/<model_name>/table_delete/<id>`:

- Requires `delete_permission = True`.
- Uses `get_queryset(request)` for object lookup.
- Deletes the object.
- Redirects to `/<app>/<model>/`.

### 10.9 POST Toolbar Action

`POST /<app_name>/<model_name>/<action>` where `<action>` matches an entry in `toolbar_button`:

- The action name must be declared in `toolbar_button`.
- The attribute on the frontend instance must be callable.
- The callable is invoked with no arguments.
- Redirects with `_safe_redirect()`.

### 10.10 POST Inline Action

`POST /<app_name>/<model_name>/<action>/<id>` where `<action>` matches an entry in `inline_button`:

- The action name must be declared in `inline_button`.
- The attribute must be callable.
- The target object is resolved through `get_queryset(request)`.
- The callable is invoked with the object instance as the sole argument.
- Redirects with `_safe_redirect()`.

### 10.11 Unknown POST Action

Unknown actions do not raise. The view redirects back to the model list URL.

## 11. Authentication and Authorization Model

### 11.1 Global Auth Check

Global auth is enforced by `_check_global_auth()`.

Request is redirected to `settings.LOGIN_URL?next=<request.path>` when all of the following are true:

- Global config `login_required` is true.
- Global config instance property `authentication` is true.
- `request.user.is_authenticated` is false.

### 11.2 Per-Model Auth Check

Per-model auth is enforced by `_check_model_auth()`.

Request is redirected to `settings.LOGIN_URL?next=<request.path>` when all of the following are true:

- Model config `login_required` is true.
- Global config instance property `authentication` is true.
- `request.user.is_authenticated` is false.

### 11.3 Authorization Flags

The package uses these booleans on `ModelFrontend`:

- `view_permission`
- `add_permission`
- `change_permission`
- `delete_permission`

These are presentation and action gates. There is no Django permission object integration. Row-level authorization is expected to be implemented by overriding `get_queryset(request)`.

### 11.4 Row-Level Authorization Hook

`ModelFrontend.get_queryset(request=None)` is the canonical extension point for scoping visible and mutable objects per request.

All sensitive object lookups in POST change, POST delete, POST inline action, and GET change use `get_queryset(request)` rather than `model.objects` directly.

## 12. `ModelFrontend` Contract

### 12.1 Attributes

Supported class attributes and defaults:

- `login_required = True`
- `toolbar_button = ()`
- `description = ""`
- `list_display = ()`
- `cards = False`
- `list_per_page = 100`
- `view_permission = True`
- `inline_button = ()`
- `search_fields = ()`
- `sortable_by = ()`
- `list_filter = ()`
- `fields = list_display`
- `readonly_fields = ()`
- `change_permission = False`
- `delete_permission = False`
- `add_permission = False`

### 12.2 Key Methods

Methods intended for use or override:

- `get_queryset(request=None)`
- `queryset(request=None, *args, **kwargs)`
- `get_form()`
- `get_pagination(request, objects)`
- `get_search_results(objects, search_fields, search_query)`
- `get_filter_results(objects, filter_fields, filter_args)`
- `get_sort_results(objects, sort_fields, sort_args)`
- `get_filter_options()`
- `get_filter_args(request_get)`

There are also simple accessors for each declarative attribute.

### 12.3 Queryset Rendering Behavior

`queryset()` returns a 2-tuple:

- `objects`: a queryset or values queryset suitable for listing.
- `fields`: the resolved column list.

Resolution rules:

- If `fields` includes `id`, values are selected exactly as listed.
- If `fields` is empty or falsy, the code falls back to `.values()` on the base queryset and infers field names from the first row, excluding `id`. If there are no rows, it falls back to the model's concrete field names excluding `id`.
- Otherwise, it selects the configured fields plus `id` so action links remain available.

### 12.4 Form Generation Behavior

`get_form()` delegates to `generate_form_for_model(model, fields)`.

Form behavior:

- A dynamic `ModelForm` class is created at runtime.
- If `fields` is empty or falsy, the form uses an empty tuple, not `__all__`.
- The package logs a warning when a form is generated without explicit fields.

Practical consequence:

- A model frontend with no `fields` and no `list_display` may still render list data, but its generated add/change form will be empty.

### 12.5 Search

Search is an OR query across all configured `search_fields` using `field__icontains`.

Query parameter:

- `q`

### 12.6 Filter

Filter UI is built from `list_filter`.

Behavior:

- For each filter field, choices come from field choices when available, otherwise from distinct database values.
- Submitted filters are read from all query parameters except `q` and `s`.
- Empty-string values are ignored.
- Filtering is implemented as OR conditions across all selected values and all configured filter fields using `field__icontains`.

Query parameters:

- any field name in `list_filter`

### 12.7 Sort

Sort UI is built from `sortable_by`.

Behavior:

- Only configured field names are allowed.
- Descending versions are allowed via `-fieldname`.
- If the incoming sort argument is not explicitly allowed, it is ignored.

Query parameter:

- `s`

### 12.8 Pagination

Pagination behavior:

- Uses Django `Paginator`.
- Page size is `list_per_page`.
- Reads the `page` query parameter.
- If the input object has an `ordered` attribute and it is false, the queryset is ordered by `pk` before paginating.

This ordering fallback exists to avoid Django's `UnorderedObjectListWarning`.

## 13. Templates and UI Composition

### 13.1 Base Template

`frontend/templates/frontend/base.html` provides:

- Bootstrap 5.3.8 CSS and JS via CDN with SRI.
- Bootstrap Icons 1.13.1 via CDN with SRI.
- jQuery 3.7.1 via CDN with SRI.
- Brand logo and title.
- Optional account dropdown in the navbar.
- Sidebar navigation when enabled.
- Navbar dropdown model navigation when sidebar is disabled.

### 13.2 Home Template

`frontend/home.html` renders model cards using `meta.cards`.

### 13.3 Site Template

`frontend/site.html` is the shared model page template and decides between:

- form mode for add or change pages
- list mode for browse pages

### 13.4 Partials

Main partials:

- `_toolbar.html`: add button and toolbar actions
- `_search.html`: search form
- `_filter_sort.html`: modal for filters and sorting
- `_table.html`: table listing
- `_cards.html`: card listing
- `_pagination.html`: previous and next pagination links
- `_form.html`: generated form and delete/inline controls

### 13.5 Template Tags

Custom filters:

- `split(value, arg)`: string split helper
- `label(value)`: converts underscore-separated action names into title-cased labels

## 14. Navigation Model

### 14.1 Navbar Registry

The site builds a navbar registry from registered models.

Grouping rules:

- Models are grouped by Django app config name.
- Group display names come from `AppConfig.verbose_name` when available, otherwise the app label.
- Model display names come from `verbose_name_plural`, then `verbose_name`, then model name.
- Model descriptions come from `db_table_comment` when present.

If accounts are registered, the navbar includes an `accounts` group with links for:

- login
- signup
- password change

Logout is available in the dropdown form but is not represented as a sidebar entry.

### 14.2 Sidebar Navigation

Sidebar behavior is controlled by `Config.sidebar` and an optional custom structure.

`site.set_sidebar_navigation(structure)` expects a dictionary mapping group names to lists of model identifiers.

Accepted model identifiers:

- Django model classes
- strings of the form `app_label.ModelName`

Sidebar modes:

- If no custom structure is set, the sidebar is derived from all registered models grouped by app verbose name.
- If a custom structure is set, only listed models are shown.
- Invalid identifiers are skipped.
- Unregistered models are skipped.

Auth-aware behavior:

- If auth is required and the request user is anonymous, model links are hidden.
- Account links are not shown in the sidebar.

## 15. Accounts Subsystem

### 15.1 Login

Uses Django's `LoginView` with package metadata injected into context.

### 15.2 Signup

Uses Django's `UserCreationForm`.

Behavior:

- On success, creates the user.
- Immediately logs the user in.
- Redirects to `LOGIN_REDIRECT_URL` or `/`.
- On validation failure, re-renders the form template with errors.

### 15.3 Logout

Uses Django's `LogoutView` subclass with `next_page = '/'`.

Behavior defined by tests:

- GET logout must return 405 on Django 5.x.
- Logout is performed via POST form with CSRF token.
- Successful logout redirects to `/`.

### 15.4 Password Flows

The package exposes password change and password reset views using Django auth view subclasses and package templates.

## 16. Security Requirements and Guarantees

The implementation and tests define the following security properties.

### 16.1 Safe Redirects

POST flows use `_safe_redirect(request, fallback)`.

Guarantee:

- `HTTP_REFERER` is only used when it points to the same host.
- Otherwise the redirect falls back to a safe internal URL.

### 16.2 Action Dispatch Whitelisting

Custom actions are only dispatched when both conditions hold:

- The action name is explicitly declared in `toolbar_button` or `inline_button`.
- The resolved attribute is callable.

Undeclared or non-callable attributes are ignored and logged instead of executed.

### 16.3 Explicit Form Fields

Generated forms never default to `fields = "__all__"`.

This prevents accidental overexposure of model fields.

### 16.4 Object Lookup Scoping

Sensitive object retrieval paths use `get_queryset(request)` rather than unconstrained model manager access. This is the package's core hook for preventing IDOR-style access when users provide their own scoped queryset implementation.

### 16.5 CSRF

Mutating operations are rendered as POST forms and rely on Django's CSRF middleware and `{% csrf_token %}` in templates.

## 17. Unsupported ModelAdmin Surface

`NotImplementedMixin` intentionally rejects many Django Admin concepts, including but not limited to:

- `actions`
- `ordering`
- `fieldsets`
- `inlines`
- `autocomplete_fields`
- `list_editable`
- `prepopulated_fields`
- `save_model`
- `delete_model`
- `add_view`
- `change_view`
- `delete_view`

Where helpful, error messages point users toward the nearest supported alternative, such as `sortable_by`, `readonly_fields`, proxy model hooks, or custom forms.

## 18. Packaging Rules

Packaging behavior from `setup.py`:

- Project name: `django-fast-frontend`
- Version: `0.4.1`
- Long description source: `README.md`
- `include_package_data=True`
- `find_packages(exclude=[...])` excludes `app`, `app2`, and `project`

## 19. Test Coverage Expectations

The repository currently verifies these areas explicitly:

- logout behavior and POST-only flow
- pagination ordering fallback
- security around form fields, action dispatch, safe redirects, and post fallback response
- sidebar structure and auth-aware behavior
- integration auth access through demo app routes

## 20. Known Implementation Realities and Documentation Mismatches

These points are part of the current-state spec because they affect real usage.

### 20.1 README Mentions `FRONTEND_AUTHENTICATION`, Code Does Not

The package does not read a `FRONTEND_AUTHENTICATION` setting. Auth availability is inferred from Django auth backends plus the presence of the `account_login` URL name.

### 20.2 `register(..., site=...)` Does Not Support Alternate Sites

Although the decorator accepts a `site` parameter, the implementation imports and uses the default singleton site directly.

### 20.3 Empty `ModelFrontend` Subclasses Are Browseable but Not Fully Editable

An empty subclass can still show list data because list queries fall back to all model fields, but generated forms have no fields unless `fields` or `list_display` is set.

### 20.4 The Package Is Admin-Like, Not Admin-Compatible

Most advanced `ModelAdmin` APIs are intentionally unsupported and raise `NotImplementedError`.

### 20.5 Auto URL Registration Mutates Root URLconf at Startup

When `FRONTEND_AUTO_URL` is enabled, the package mutates `ROOT_URLCONF.urlpatterns` during app startup. This is supported behavior, but it should not be combined with manual inclusion of the same frontend URLs.

## 21. Recommended Usage Pattern

Canonical model frontend declaration:

```python
import frontend
from myapp.models import Author


@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ("name", "title")
    list_display = ("name", "title")
    search_fields = ("name", "title")
    list_filter = ("title",)
    sortable_by = ("name", "title")
    add_permission = True
    change_permission = True
    delete_permission = True

    def get_queryset(self, request=None):
        queryset = super().get_queryset(request)
        if request and not request.user.is_superuser:
            queryset = queryset.filter(owner=request.user)
        return queryset
```

Project wiring:

```python
from django.urls import path
import frontend


urlpatterns = [
    path("accounts/", frontend.accounts.urls),
    path("", frontend.site.urls),
]
```

## 22. Acceptance Criteria for Compatibility

A future version remains compatible with this spec if all of the following remain true unless a breaking change is intentionally announced:

- Public exports in `frontend/__init__.py` remain available.
- The main URL schema remains usable.
- `@frontend.register(Model)` continues to register model frontends.
- `ModelFrontend.get_queryset(request)` remains the row-level authorization hook.
- POST custom actions continue to require explicit declaration and callable validation.
- Generated forms continue to avoid `__all__` defaults.
- Logout remains POST-only and redirects to `/` by default.
- Unordered querysets continue to be normalized before pagination.
