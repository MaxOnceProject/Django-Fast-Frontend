<!-- managed-by: blitz -->
## Read First
See `/agent.md` for project scope and architecture.

## Responsibilities
Full-featured demo app (`app/`) showing how to use `django-fast-frontend`. Not distributed in
the PyPI package. Demonstrates the full feature set: search, filter, sort, sidebar, cards, CSS
themes, toolbar/inline buttons, custom actions, and per-model `login_required` overrides.

## Boundaries
- **May change**: model fields, frontend config attributes, CSS themes, test scenarios
- **Must stay aligned**: demo patterns must reflect actual library conventions — these are canonical usage examples
- **Out of scope**: `frontend/` (core library), `app2/` (minimal demo), `project/` (Django project config)

## Key Files
| File | Role | Key Exports |
|---|---|---|
| `app/admin.py` | Django Admin mirror for the demo model | `AuthorAdmin` |
| `app/models.py` | `Author` model (name, title, birth_date, created_at) used to demo non-editable field rendering on change pages | `Author` |
| `app/frontend.py` | Full-featured `AuthorFrontend` — search, filter, sort, cards, toolbar/inline buttons, add/change forms, readonly non-editable field display, and `login_required = False` | `AuthorFrontend`, `AuthorFrontend.everything()`, `.everything_everything()`, `.check()`, `.uncheck()` |
| `app/apps.py` | AppConfig (7 lines); `verbose_name = 'Content'` drives sidebar group label | `AppConfig` |
| `app/management/commands/seed_demo_data.py` | Deterministic demo-data seed command for Docker end-to-end browser runs | `Command.handle()` |
| `app/tests/test_frontend.py` | Integration tests: auth flow, CRUD, list/detail access, action labels, and readonly non-editable field rendering | `test_user_anonymous()`, `test_user_is_authenticated()`, `test_global_authentication_off()`, `test_change_page_renders_non_editable_fields_as_readonly_values()` |
| `app/tests/test_browser_ui.py` | Docker-native Playwright smoke tests against a live seeded Django server with saved screenshots | `test_login_navigation_and_logout()`, `test_list_search_and_sort()`, `test_add_and_change_author()` |
| `app/static/css/` | Custom theme CSS variants: blue, purple, rgb | Static assets |

## Registration Pattern (canonical example)
```python
import frontend
from app.models import Author

@frontend.register(Author)
class AuthorFrontend(frontend.ModelFrontend):
    fields = ('name', 'title', 'created_at')
    login_required = False
    list_display = ('name', 'title')
    readonly_fields = ('created_at',)
    add_permission = True
    change_permission = True
    search_fields = ('name', 'title', 'birth_date')
    list_filter = ('name', 'title')
    sortable_by = ('name', 'title')
```

## Test Pattern
```python
@pytest.mark.django_db
def test_something(client):
    user = User.objects.create_user(username='u', password='p')
    client.login(username='u', password='p')
    response = client.get('/')
    assert response.status_code == 200
```
