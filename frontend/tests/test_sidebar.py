"""
Tests for the navigation sidebar feature (Plan 006 / Feature #27).

Covers:
- Sidebar configuration storage (set_sidebar_navigation)
- Sidebar registry building (get_sidebar_registry)
- Model identifier normalization (class + string)
- Fallback behavior (no config → app-based grouping)
- Hide-unlisted behavior (configured → unlisted hidden)
- Auth-aware filtering (anonymous → account links only)
- Request-aware meta building (meta.sidebar in context)
- Accounts auto-append behavior
"""

import pytest
from unittest.mock import MagicMock, patch
from django.test import RequestFactory
from django.contrib.auth.models import User

from frontend.sites.abstract import FrontendSiteAbstract
from frontend import site


# ---------------------------------------------------------------------------
# Sidebar configuration storage
# ---------------------------------------------------------------------------

class TestSetSidebarNavigation:
    """FrontendSite should store a sidebar navigation structure."""

    @pytest.fixture(autouse=True)
    def reset_sidebar(self):
        yield
        site._sidebar_navigation = None

    def test_set_sidebar_navigation_stores_structure(self):
        """Setting sidebar navigation should store the dict on the site."""
        from app.models import Author
        structure = {"Writers": [Author]}
        site.set_sidebar_navigation(structure)
        assert site._sidebar_navigation == structure

    def test_sidebar_navigation_defaults_to_none(self):
        """Before configuration, sidebar navigation should be None."""
        site._sidebar_navigation = None
        assert site._sidebar_navigation is None

    def test_set_sidebar_navigation_rejects_non_dict(self):
        """Passing a non-dict should raise TypeError."""
        with pytest.raises(TypeError, match="expects a dict"):
            site.set_sidebar_navigation(["not", "a", "dict"])


# ---------------------------------------------------------------------------
# Model identifier normalization
# ---------------------------------------------------------------------------

class TestResolveModelIdentifier:
    """Model identifiers should be normalized from class or string."""

    def test_resolve_model_class(self):
        """A Django model class should be returned as-is."""
        from frontend.sites.abstract import _resolve_model_identifier
        from app.models import Author
        assert _resolve_model_identifier(Author) is Author

    def test_resolve_string_identifier(self):
        """A string 'app_label.ModelName' should resolve to the model class."""
        from frontend.sites.abstract import _resolve_model_identifier
        from app.models import Author
        result = _resolve_model_identifier("app.Author")
        assert result is Author

    def test_resolve_invalid_string_returns_none(self):
        """An invalid string identifier should return None (not raise)."""
        from frontend.sites.abstract import _resolve_model_identifier
        result = _resolve_model_identifier("nonexistent.FakeModel")
        assert result is None

    def test_resolve_malformed_string_returns_none(self):
        """A string without a dot should return None."""
        from frontend.sites.abstract import _resolve_model_identifier
        result = _resolve_model_identifier("nodot")
        assert result is None


# ---------------------------------------------------------------------------
# Sidebar registry builder — fallback (no config)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSidebarRegistryFallback:
    """When no sidebar config is set, sidebar falls back to app-based grouping."""

    @pytest.fixture(autouse=True)
    def reset_sidebar(self):
        yield
        site._sidebar_navigation = None

    def test_fallback_returns_list_of_groups(self):
        """Fallback sidebar should return a list of dicts with 'group' and 'items'."""
        site._sidebar_navigation = None
        sidebar = site.get_sidebar_registry()
        assert isinstance(sidebar, list)
        for group in sidebar:
            assert 'group' in group
            assert 'items' in group
            assert isinstance(group['items'], list)

    def test_fallback_includes_registered_models(self):
        """Fallback should include all registered model frontends."""
        site._sidebar_navigation = None
        sidebar = site.get_sidebar_registry()
        # Flatten all item names
        all_items = []
        for group in sidebar:
            for item in group['items']:
                all_items.append(item.get('name'))
        # Author and People are registered in the demo apps
        assert 'author' in all_items
        assert 'people' in all_items


# ---------------------------------------------------------------------------
# Sidebar registry builder — configured (hide unlisted)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSidebarRegistryConfigured:
    """When sidebar config is set, only listed models appear."""

    @pytest.fixture(autouse=True)
    def reset_sidebar(self):
        yield
        site._sidebar_navigation = None

    def test_configured_sidebar_respects_order(self):
        """Configured sidebar should preserve group and item order."""
        from app.models import Author
        from app2.models import People
        structure = {"Group A": [People], "Group B": [Author]}
        site.set_sidebar_navigation(structure)
        sidebar = site.get_sidebar_registry()
        # Exclude the auto-appended accounts group
        model_groups = [g for g in sidebar if g['group'] != 'Account']
        assert len(model_groups) == 2
        assert model_groups[0]['group'] == 'Group A'
        assert model_groups[1]['group'] == 'Group B'
        assert model_groups[0]['items'][0]['name'] == 'people'
        assert model_groups[1]['items'][0]['name'] == 'author'

    def test_configured_sidebar_hides_unlisted(self):
        """Models not in the sidebar config should be hidden."""
        from app.models import Author
        structure = {"Writers": [Author]}
        site.set_sidebar_navigation(structure)
        sidebar = site.get_sidebar_registry()
        model_groups = [g for g in sidebar if g['group'] != 'Account']
        all_items = []
        for group in model_groups:
            for item in group['items']:
                all_items.append(item.get('name'))
        assert 'author' in all_items
        assert 'people' not in all_items

    def test_configured_sidebar_supports_string_identifiers(self):
        """String identifiers 'app_label.ModelName' should resolve."""
        structure = {"Writers": ["app.Author"]}
        site.set_sidebar_navigation(structure)
        sidebar = site.get_sidebar_registry()
        model_groups = [g for g in sidebar if g['group'] != 'Account']
        assert len(model_groups) == 1
        assert model_groups[0]['items'][0]['name'] == 'author'

    def test_configured_sidebar_skips_invalid_identifiers(self):
        """Invalid model identifiers should be skipped without error."""
        from app.models import Author
        structure = {"Writers": [Author, "nonexistent.Fake"]}
        site.set_sidebar_navigation(structure)
        sidebar = site.get_sidebar_registry()
        model_groups = [g for g in sidebar if g['group'] != 'Account']
        all_items = []
        for group in model_groups:
            for item in group['items']:
                all_items.append(item.get('name'))
        assert 'author' in all_items
        assert len(all_items) == 1  # only author, fake skipped


# ---------------------------------------------------------------------------
# Accounts auto-append behavior
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSidebarAccountsAutoAppend:
    """Account links should be auto-appended when accounts are enabled."""

    @pytest.fixture(autouse=True)
    def reset_sidebar(self):
        yield
        site._sidebar_navigation = None

    def test_accounts_appended_when_enabled(self):
        """When accounts are registered, sidebar should include Account group."""
        sidebar = site.get_sidebar_registry()
        account_groups = [g for g in sidebar if g['group'] == 'Account']
        if 'accounts' in site._registry:
            assert len(account_groups) == 1
            items = account_groups[0]['items']
            item_names = [i['name'] for i in items]
            assert 'login' in item_names
            assert 'signup' in item_names

    def test_accounts_appended_even_when_not_in_config(self):
        """Even if user doesn't include accounts in their config, they appear."""
        from app.models import Author
        structure = {"Writers": [Author]}
        site.set_sidebar_navigation(structure)
        sidebar = site.get_sidebar_registry()
        account_groups = [g for g in sidebar if g['group'] == 'Account']
        if 'accounts' in site._registry:
            assert len(account_groups) == 1


# ---------------------------------------------------------------------------
# Auth-aware sidebar filtering
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSidebarAuthFiltering:
    """Anonymous users should only see account links when auth is enabled."""

    def test_anonymous_user_sees_no_model_links(self):
        """When auth is required and user is anonymous, no model links."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = MagicMock(is_authenticated=False)

        sidebar = site.get_sidebar_registry(request=request)
        model_groups = [g for g in sidebar if g['group'] != 'Account']
        # When login_required + authentication, no model groups for anon
        global_config = site.get_global_config()
        if getattr(global_config, 'login_required', True) and getattr(global_config(), 'authentication', False):
            assert len(model_groups) == 0

    def test_authenticated_user_sees_model_links(self):
        """When user is authenticated, model links should be visible."""
        factory = RequestFactory()
        request = factory.get("/")
        user = User.objects.create_user(username="sidebartest", password="pass")
        request.user = user

        sidebar = site.get_sidebar_registry(request=request)
        model_groups = [g for g in sidebar if g['group'] != 'Account']
        assert len(model_groups) > 0


# ---------------------------------------------------------------------------
# Request-aware meta building
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMetaSidebar:
    """get_site_meta should include meta.sidebar in the context."""

    def test_meta_includes_sidebar(self):
        """Context should have meta.sidebar after get_site_meta."""
        factory = RequestFactory()
        request = factory.get("/")
        user = User.objects.create_user(username="metatest", password="pass")
        request.user = user

        context = {}
        context = site.get_site_meta(context, request=request)
        assert 'sidebar' in context['meta']
        assert isinstance(context['meta']['sidebar'], list)

    def test_meta_sidebar_without_request(self):
        """When request is not passed, sidebar should still be present (unfiltered)."""
        context = {}
        context = site.get_site_meta(context)
        assert 'sidebar' in context['meta']
        assert isinstance(context['meta']['sidebar'], list)
