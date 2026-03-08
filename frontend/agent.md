<!-- managed-by: blitz -->
## Read First
See `/agent.md` for project scope and architecture.

## Responsibilities
Core library distributed as PyPI package `django-fast-frontend`. Provides: site registry, `ModelFrontend`
extension point, HTTP views for list/detail/CRUD, form generation, accounts (login/signup/password),
URL routing, and templatetags. Also owns the Django 5.x logout compatibility flow and unordered
pagination fallback. All subdirectories here are distributed together.

## Boundaries
- **May change**: `ModelFrontend` attributes/methods, template HTML, CSS, search/filter/sort, form logic
- **Must not break**: public API (`frontend/__init__.py` re-exports), URL schema `/<app>/<model>/<action>/<id>`, `@register` decorator signature, `get_queryset(request)` signature
- **Out of scope**: `app/`, `app2/`, `project/` — those are the demo harness, not this package

## Key Files
| File | Role | Key Exports |
|---|---|---|
| `frontend/__init__.py` | Public API entry | `site`, `FrontendSite`, `ModelFrontend`, `Config`, `AccountFrontend`, `register`, `action` |
| `frontend/frontend.py` | Default site config; registers `Config` + optionally `AccountFrontend` at import (20 lines) | `Frontend` |
| `frontend/accounts.py` | Account URL site; provides password reset flow URLs (15 lines) | `AccountSite`, `site` |
| `frontend/sites/abstract.py` | Base registry + rendering (266 lines) | `FrontendAbstract`, `FrontendSiteAbstract.__init__()`, `.urls`, `.register()`, `.unregister()`, `.autodiscover_modules()`, `.get_global_config()`, `.get_navbar_registry()`, `.set_sidebar_navigation()`, `.get_sidebar_registry()`, `.get_site_meta()`, `.http_response()`, `_resolve_model_identifier()` |
| `frontend/sites/model.py` | ModelFrontend base class; filter/sort/search/pagination with unordered-QuerySet fallback plus action label metadata resolution and readonly display layout for non-editable configured fields | `ModelFrontend.get_queryset()`, `.queryset()`, `.get_form()`, `.get_form_fields()`, `.get_non_editable_fields()`, `.get_form_layout()`, `.get_readonly_field_value()`, `.get_pagination()`, `.get_search_results()`, `.get_filter_results()`, `.get_sort_results()`, `.get_filter_options()`, `.get_filter_args()`, `.get_action_label()`, `.get_toolbar_actions()`, `.get_inline_actions()`, `.has_*_permission()` |
| `frontend/sites/site.py` | Singleton registry; `FRONTEND_SITE_CLASS` override support (79 lines) | `FrontendSite.register_config()`, `.register_accounts()`, `.get_model_config()`, `.get_navbar_registry_by_app()`, `.http_home_response()`, `.http_model_response()`, `.http_login_redirect()`, `.get_cards()`, `site` |
| `frontend/sites/config.py` | Global site config (27 lines) | `Config`, `Config.sidebar` attribute, `Config.authentication` property |
| `frontend/sites/account.py` | AccountFrontend base class (12 lines) | `AccountFrontend` |
| `frontend/sites/decorators.py` | Public decorators for registration and action metadata | `register`, `action` |
| `frontend/sites/mixin.py` | NotImplemented guard for unsupported Admin attrs (243 lines) | `NotImplementedMixin` — 30+ properties/methods raising `NotImplementedError` |
| `frontend/views.py` | All HTTP views incl. safe redirects, logout POST compatibility, and password reset/change (394 lines) | `_safe_redirect()`, `favicon_view()`, `FrontendModelView._check_global_auth()`, `._check_model_auth()`, `.get()`, `.post()`, `FrontendAbstractView`, `FrontendLoginView`, `FrontendSignUpView.post()`, `FrontendLogoutView`, `FrontendPassword*View` (6 views) |
| `frontend/forms.py` | Dynamic ModelForm factory (45 lines) | `FrontendModelForm`, `generate_form_for_model()` |
| `frontend/apps.py` | AppConfig + autodiscovery + `FRONTEND_AUTO_URL` injection (47 lines) | `FrontendConfig.ready()` |
| `frontend/urls.py` | URL patterns incl. full password reset flow (26 lines) | `urlpatterns`, `urlpatterns_account` |
| `frontend/templatetags/django_fast_frontend.py` | Custom template filters (14 lines) | `split`, `label` filters |
| `frontend/tests/test_logout.py` | Logout regression tests for POST-only flow, redirect target, and base template form | `TestLogoutView`, `TestLogoutViewNextPage`, `TestLogoutTemplate` |
| `frontend/tests/test_pagination.py` | Pagination regression tests for unordered QuerySets and `?page=` handling | `TestGetPaginationOrdering` |
| `frontend/tests/test_security.py` | Security unit tests (407 lines) | `TestFormFieldSafety`, `TestActionDispatchSafety`, `TestOpenRedirectPrevention`, `TestObjectLevelAuthorization`, `TestAuthNormalization`, `TestTemplateSecurity`, `TestPackaging`, `TestPostFallbackReturn` |
| `frontend/tests/test_sidebar.py` | Sidebar unit tests | `TestSetSidebarNavigation`, `TestResolveModelIdentifier`, `TestSidebarRegistryFallback`, `TestSidebarRegistryConfigured`, `TestSidebarAccountsAutoAppend`, `TestFrontendSidebarSetting`, `TestSidebarAuthFiltering`, `TestMetaSidebar` |

## ModelFrontend Attributes
| Attribute | Type | Default | Description |
|---|---|---|---|
| login_required | bool | True | Require authentication |
| fields | tuple | follows `list_display` (default `()`) | Form fields; declare explicitly for new subclasses and never use `"__all__"` |
| list_display | tuple | () | Columns in list view |
| search_fields | tuple | () | Searchable fields |
| list_filter | tuple | () | Filterable fields |
| sortable_by | tuple | () | Sortable fields |
| list_per_page | int | 100 | Pagination size |
| cards | bool | False | Card vs table display |
| view_permission | bool | True | Allow viewing |
| add_permission | bool | False | Allow creating |
| change_permission | bool | False | Allow editing |
| delete_permission | bool | False | Allow deleting |
| readonly_fields | tuple | () | Editable fields that should render readonly in forms; configured model fields that are already non-editable render as display-only values on change pages |
| toolbar_button | tuple | () | Toolbar action methods |
| inline_button | tuple | () | Per-row action methods |
| description | str | "" | Model frontend description |

Action labels are resolved from action metadata first (`short_description`, typically set via `@frontend.action(description=...)`) and otherwise fall back to the action name with underscores replaced by spaces and title casing applied.

## Internal Call Chain
```
FrontendConfig.ready() → site.autodiscover_modules() → import {app}.frontend → @register stores in _registry

GET request → FrontendModelView.get()
  → _check_global_auth() → site.get_model_config(model)
  → model_config.get_form() filters configured fields down to editable model fields
  → model_config.get_form_layout(form, obj) re-inserts configured non-editable fields as readonly display rows on change pages
  → model_config.queryset() → search → filter → sort → pagination
  → site.http_model_response() → render frontend/site.html

POST request → FrontendModelView.post()
  → auth checks → get_model_config()
  → table_add/change/delete → form.save() / object.delete()
  → toolbar/inline: validate action in declared tuple → getattr(config, action)()
  → _safe_redirect(request)
```

## Dependencies
- Internal: `frontend/sites/` ← `frontend/views.py` ← `frontend/urls.py` ← `frontend/__init__.py`
- External: `django>=4.2`, `django_bootstrap5>=26.2`

## Change Guidance
- New `ModelFrontend` attribute → `sites/model.py` class body
- New URL pattern → `frontend/urls.py`
- New view → extend in `frontend/views.py` + add corresponding security test
- Logout behavior change → update `frontend/views.py`, `frontend/templates/frontend/base.html`, and `frontend/tests/test_logout.py`
- Pagination behavior change → update `frontend/sites/model.py` and `frontend/tests/test_pagination.py`
- Changed public export → `frontend/__init__.py`
