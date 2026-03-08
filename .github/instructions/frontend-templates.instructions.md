---
applyTo: "frontend/templates/**"
---
<!-- managed-by: blitz -->

## Context
Read `agent.md` for project scope. Templates have no local `agent.md` — all template knowledge is in this file.

## Scope
HTML templates rendered by `FrontendSite.http_response()`. Uses Django template engine with `django_bootstrap5`.

## Template Hierarchy
```
frontend/base.html              ← base layout (navbar, sidebar, Bootstrap 5, CSS blocks)
  → frontend/home.html          ← home/app landing page (renders _cards.html)
  → frontend/site.html          ← model list/detail (renders all partials below)
      _table.html               ← tabular row display
      _cards.html               ← card grid display
      _toolbar.html             ← toolbar actions (toolbar_button)
      _search.html              ← search bar
      _filter_sort.html         ← filter and sort controls (list_filter, sortable_by)
      _form.html                ← add/change/delete form
      _pagination.html          ← page controls
accounts/form.html              ← login/signup/password forms (extends base.html)
```

## Layout
`base.html`: Bootstrap grid — sidebar `col-md-3/col-lg-2` (navigation) + content `col-md-9/col-lg-10`
(`{% block content %}`). Mobile (< md): sidebar stacks above content.

## Custom Tags & Filters
Load with `{% load django_fast_frontend %}`. Defined in `frontend/templatetags/django_fast_frontend.py`.

## Context Variables (from `get_site_meta()`)
| Key | Type | Purpose |
|---|---|---|
| `meta.brand` | str | Site brand name |
| `meta.logo` | str | Logo image path |
| `meta.css` | str | Custom CSS file path |
| `meta.navbar` | list | Top-level nav items |
| `meta.sidebar` | list | Sidebar navigation groups (list of `{"group": str, "items": [...]}` dicts); empty list when `FRONTEND_SIDEBAR = False` |

## DO / NEVER
- **DO** extend `frontend/base.html` for all frontend pages
- **DO** use `{% load django_fast_frontend %}` before using custom filters
- **DO** use `django_bootstrap5` tags for form rendering — do not write raw Bootstrap HTML for forms
- **NEVER** hardcode brand/logo/CSS values in templates — always use `{{ meta.* }}` context vars
- **NEVER** duplicate sidebar/navbar HTML — the base template owns it

## Testing
Templates are covered by integration tests in `app/tests/test_frontend.py`. Check response content with `assert b'Expected text' in response.content`.

## Gotchas
- Partial templates all prefixed with `_` (e.g., `_table.html`) — they are included via `{% include %}`, not extended
- `accounts/form.html` is shared for login, signup, and password change — action URL differs per view
