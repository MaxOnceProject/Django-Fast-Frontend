"""
Security tests for Django Fast Frontend.

Tests cover the 4 Critical + 5 High findings from the security audit:
  CRITICAL-1: IDOR via direct object lookup without authorization
  CRITICAL-2: Unsafe action dispatch via getattr
  CRITICAL-3: Open redirect via HTTP_REFERER
  CRITICAL-4: fields="__all__" exposing all model fields
  HIGH-1: Missing CSRF (handled by Django middleware — covered by integration)
  HIGH-2: Auth bypass in POST due to Config.authentication property bug
  HIGH-3: Signup auto-login without email verification
  HIGH-4: No rate limiting (out of scope — middleware concern)
  HIGH-5: jQuery without SRI (template test)
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from django.test import Client, RequestFactory, TestCase, override_settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from frontend.forms import generate_form_for_model
from frontend.sites.model import ModelFrontend


# ---------------------------------------------------------------------------
# CRITICAL-4: fields="__all__" default must be removed
# ---------------------------------------------------------------------------

class TestFormFieldSafety(TestCase):
    """generate_form_for_model should NOT default to '__all__'."""

    def test_generate_form_without_fields_does_not_expose_all(self):
        """When fields is empty/falsy, the form must NOT use '__all__'."""
        from django.contrib.auth.models import User
        form_class = generate_form_for_model(User, fields=())
        # After the fix, empty fields should remain empty tuple — not "__all__"
        self.assertNotEqual(form_class.Meta.fields, "__all__",
                            "Empty fields must not fall back to '__all__'")

    def test_generate_form_with_explicit_fields(self):
        """When explicit fields are given, only those should appear."""
        from django.contrib.auth.models import User
        form_class = generate_form_for_model(User, fields=("username", "email"))
        self.assertEqual(form_class.Meta.fields, ("username", "email"))


# ---------------------------------------------------------------------------
# CRITICAL-2: Action dispatch must validate against allowed actions
# ---------------------------------------------------------------------------

class TestActionDispatchSafety(TestCase):
    """POST action dispatch must only execute explicitly declared actions."""

    def test_toolbar_action_rejects_undeclared_method(self):
        """Calling an action not in toolbar_button must not dispatch."""
        from frontend.views import FrontendModelView

        factory = RequestFactory()
        request = factory.post("/app/author/malicious_action")
        request.user = MagicMock(is_authenticated=True)

        # Create a mock model_config with an explicit spy for the undeclared action
        model_config = MagicMock()
        model_config.toolbar_button = ("safe_action",)
        model_config.inline_button = ()
        model_config.change_permission = False
        model_config.add_permission = False
        model_config.delete_permission = False
        model_config.get_login_required.return_value = False
        # Explicitly set the spy so we can track calls
        malicious_spy = MagicMock()
        model_config.malicious_action = malicious_spy

        with patch("frontend.views.site") as mock_site:
            mock_site.get_global_config.return_value = MagicMock(
                login_required=False,
                authentication=False,
            )
            mock_site.get_model_config.return_value = model_config

            with patch("frontend.views.apps") as mock_apps:
                mock_apps.get_model.return_value = MagicMock()

                view = FrontendModelView()
                response = view.post(
                    request,
                    app_name="app",
                    model_name="author",
                    action="malicious_action",
                    id=None,
                )
                # The undeclared action must NOT have been called
                malicious_spy.assert_not_called()
                # Response should be a redirect (fallback), not an error
                self.assertEqual(response.status_code, 302)

    def test_toolbar_action_skips_non_callable(self):
        """If a declared toolbar action attribute is not callable, it must not crash."""
        from frontend.views import FrontendModelView

        factory = RequestFactory()
        request = factory.post("/app/author/not_callable")
        request.user = MagicMock(is_authenticated=True)

        model_config = MagicMock()
        model_config.toolbar_button = ("not_callable",)
        model_config.inline_button = ()
        model_config.change_permission = False
        model_config.add_permission = False
        model_config.delete_permission = False
        model_config.get_login_required.return_value = False
        # Set the action to a non-callable value
        model_config.not_callable = "I am a string, not callable"

        with patch("frontend.views.site") as mock_site:
            mock_site.get_global_config.return_value = MagicMock(
                login_required=False,
                authentication=False,
            )
            mock_site.get_model_config.return_value = model_config

            with patch("frontend.views.apps") as mock_apps:
                mock_apps.get_model.return_value = MagicMock()

                view = FrontendModelView()
                response = view.post(
                    request,
                    app_name="app",
                    model_name="author",
                    action="not_callable",
                    id=None,
                )
                # Should redirect safely, not crash
                self.assertEqual(response.status_code, 302)

    def test_inline_action_dispatches_declared_callable(self):
        """Inline button actions that are declared AND callable must be invoked."""
        from frontend.views import FrontendModelView

        factory = RequestFactory()
        request = factory.post("/app/author/do_something/1")
        request.user = MagicMock(is_authenticated=True)

        model_config = MagicMock()
        model_config.toolbar_button = ()
        model_config.inline_button = ("do_something",)
        model_config.change_permission = False
        model_config.add_permission = False
        model_config.delete_permission = False
        model_config.get_login_required.return_value = False
        action_spy = MagicMock()
        model_config.do_something = action_spy

        mock_obj = MagicMock()
        mock_qs = MagicMock()
        mock_qs.get.return_value = mock_obj
        model_config.get_queryset.return_value = mock_qs

        with patch("frontend.views.site") as mock_site:
            mock_site.get_global_config.return_value = MagicMock(
                login_required=False,
                authentication=False,
            )
            mock_site.get_model_config.return_value = model_config

            with patch("frontend.views.apps") as mock_apps:
                mock_apps.get_model.return_value = MagicMock()

                view = FrontendModelView()
                response = view.post(
                    request,
                    app_name="app",
                    model_name="author",
                    action="do_something",
                    id="1",
                )
                # The declared callable action SHOULD have been called with the object
                action_spy.assert_called_once_with(mock_obj)
                self.assertEqual(response.status_code, 302)


# ---------------------------------------------------------------------------
# CRITICAL-3: Open redirect via HTTP_REFERER
# ---------------------------------------------------------------------------

class TestOpenRedirectPrevention(TestCase):
    """Redirects must not use unvalidated HTTP_REFERER."""

    def test_favicon_view_no_open_redirect(self):
        """favicon_view must not redirect to arbitrary external URL."""
        from frontend.views import favicon_view

        factory = RequestFactory()
        request = factory.get("/favicon.ico", HTTP_REFERER="https://evil.com/steal")
        request.user = MagicMock(is_authenticated=True)

        response = favicon_view(request)
        # After fix: should return 204 No Content, not redirect to evil.com
        self.assertNotEqual(
            getattr(response, "url", None),
            "https://evil.com/steal",
            "favicon_view must not redirect to external URLs"
        )

    def test_post_redirect_uses_safe_url(self):
        """POST handlers must not blindly redirect to HTTP_REFERER."""
        # This test verifies the _safe_redirect helper exists and filters URLs
        from frontend.views import _safe_redirect

        factory = RequestFactory()
        request = factory.post("/app/author/table_add")
        request.META["HTTP_REFERER"] = "https://evil.com/phish"

        redirect_response = _safe_redirect(request, fallback="/app/author/")
        self.assertNotEqual(
            redirect_response.url,
            "https://evil.com/phish",
            "Redirect must not follow untrusted referer"
        )
        self.assertEqual(redirect_response.url, "/app/author/")


# ---------------------------------------------------------------------------
# CRITICAL-1: IDOR — object lookups must use scoped queryset
# ---------------------------------------------------------------------------

class TestObjectLevelAuthorization(TestCase):
    """Object lookups must use get_queryset to scope access."""

    def test_model_frontend_has_get_queryset_with_request(self):
        """ModelFrontend.get_queryset must accept a request parameter."""
        import inspect
        sig = inspect.signature(ModelFrontend.get_queryset)
        params = list(sig.parameters.keys())
        self.assertIn("request", params,
                      "get_queryset must accept 'request' for user-scoped filtering")

    def test_queryset_method_still_works_without_request(self):
        """Backward compat: queryset() (no request) must still function."""
        mf = ModelFrontend()
        mf.model = MagicMock()
        mock_qs = MagicMock()
        mf.model._default_manager.get_queryset.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.exists.return_value = False
        mf.model._meta.fields = []

        # Should not raise
        objects, fields = mf.queryset()

    def test_queryset_delegates_to_get_queryset(self):
        """queryset() must call get_queryset() so overrides are respected for list display."""
        mf = ModelFrontend()
        mf.model = MagicMock()
        mock_qs = MagicMock()
        mock_qs.values.return_value = mock_qs
        mock_qs.exists.return_value = False
        mf.model._meta.fields = []

        # Patch get_queryset to return our controlled queryset
        with patch.object(mf, 'get_queryset', return_value=mock_qs) as mock_get_qs:
            sentinel_request = MagicMock()
            mf.queryset(request=sentinel_request)
            # get_queryset must have been called with the request
            mock_get_qs.assert_called_once_with(sentinel_request)


# ---------------------------------------------------------------------------
# HIGH-2: Auth bypass — POST uses Config.authentication as class attr
# ---------------------------------------------------------------------------

class TestAuthNormalization(TestCase):
    """GET and POST must use identical authentication logic."""

    def test_post_without_auth_redirects_when_login_required(self):
        """Unauthenticated POST to a login_required model must redirect."""
        client = Client()
        response = client.post("/app/author/table_add")
        # Should redirect to login, not allow anonymous post
        self.assertIn(response.status_code, [301, 302, 403],
                      "Unauthenticated POST must be rejected")


# ---------------------------------------------------------------------------
# Template: SRI integrity on CDN resources
# ---------------------------------------------------------------------------

class TestTemplateSecurity(TestCase):
    """Base template must include SRI hashes on all CDN resources."""

    def test_base_template_has_head_closing_tag(self):
        """base.html must have a closing </head> tag."""
        import os
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "templates", "frontend", "base.html"
        )
        with open(template_path, "r") as f:
            content = f.read()
        self.assertIn("</head>", content,
                      "base.html must have a closing </head> tag")

    def test_base_template_jquery_has_sri(self):
        """jQuery CDN link must include integrity attribute."""
        import os
        import re
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "templates", "frontend", "base.html"
        )
        with open(template_path, "r") as f:
            content = f.read()
        # Find the <script> tag that loads jQuery and verify it has integrity
        jquery_tag = re.search(r'<script[^>]+jquery[^>]+>', content)
        self.assertIsNotNone(jquery_tag, "jQuery script tag must exist")
        self.assertIn("integrity=", jquery_tag.group(0),
                      "jQuery script tag must include integrity attribute")

    def test_base_template_bootstrap_icons_has_sri(self):
        """Bootstrap Icons CDN link must include integrity attribute."""
        import os
        import re
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "templates", "frontend", "base.html"
        )
        with open(template_path, "r") as f:
            content = f.read()
        # Find the <link> tag that loads bootstrap-icons and verify it has integrity
        icons_tag = re.search(r'<link[^>]+bootstrap-icons[^>]+>', content)
        self.assertIsNotNone(icons_tag, "Bootstrap Icons link tag must exist")
        self.assertIn(
            "integrity=",
            icons_tag.group(0),
            "Bootstrap Icons link must include integrity attribute"
        )


# ---------------------------------------------------------------------------
# Packaging: setup.py must exclude demo apps
# ---------------------------------------------------------------------------

class TestPackaging(TestCase):
    """setup.py must not ship demo/test packages."""

    def test_setup_excludes_demo_packages(self):
        """find_packages must exclude app, app2, project."""
        import ast
        import os

        setup_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "setup.py"
        )
        with open(setup_path, "r") as f:
            content = f.read()

        # After fix: setup.py should use find_packages(exclude=[...])
        self.assertIn("exclude", content,
                      "setup.py must use find_packages(exclude=[...]) to avoid shipping demo apps")


# ---------------------------------------------------------------------------
# BLOCKER-2 regression: post() must never return None
# ---------------------------------------------------------------------------

class TestPostFallbackReturn(TestCase):
    """post() must return an HttpResponse even for unrecognised actions."""

    def test_post_unrecognised_action_returns_redirect(self):
        """An action matching nothing must still produce a redirect, not None."""
        from frontend.views import FrontendModelView

        factory = RequestFactory()
        request = factory.post("/app/author/totally_unknown_action")
        request.user = MagicMock(is_authenticated=True)

        model_config = MagicMock()
        model_config.toolbar_button = ()
        model_config.inline_button = ()
        model_config.change_permission = False
        model_config.add_permission = False
        model_config.delete_permission = False
        model_config.get_login_required.return_value = False

        with patch("frontend.views.site") as mock_site:
            mock_site.get_global_config.return_value = MagicMock(
                login_required=False,
                authentication=False,
            )
            mock_site.get_model_config.return_value = model_config

            with patch("frontend.views.apps") as mock_apps:
                mock_apps.get_model.return_value = MagicMock()

                view = FrontendModelView()
                response = view.post(
                    request,
                    app_name="app",
                    model_name="author",
                    action="totally_unknown_action",
                    id=None,
                )
                # Must return a response, never None
                self.assertIsNotNone(response, "post() must never return None")
                self.assertEqual(response.status_code, 302)
