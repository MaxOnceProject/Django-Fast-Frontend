"""
Tests for FrontendLogoutView and base.html logout form.

Django 5.x LogoutView rejects GET requests (405 Method Not Allowed).
Logout must use HTTP POST with CSRF protection and redirect to '/' afterwards.
"""

import os
import re
import pytest
from django.test import Client, TestCase
from django.contrib.auth.models import User


TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "templates", "frontend", "base.html",
)


# ---------------------------------------------------------------------------
# View behaviour
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestLogoutView:
    """FrontendLogoutView must only accept POST and redirect to '/' on success."""

    def test_logout_get_returns_405(self):
        """GET /accounts/logout/ must return 405 Method Not Allowed."""
        response = Client().get("/accounts/logout/")
        assert response.status_code == 405

    def test_logout_post_unauthenticated_redirects(self):
        """Anonymous POST /accounts/logout/ must not raise (harmless no-op)."""
        response = Client().post("/accounts/logout/")
        assert response.status_code in (200, 302)

    def test_logout_post_logs_out_user(self):
        """After POST logout the session must no longer carry the auth key."""
        from django.contrib.auth import SESSION_KEY
        user = User.objects.create_user(username="logouttest", password="s3cr3t!")
        client = Client()
        client.login(username="logouttest", password="s3cr3t!")
        assert SESSION_KEY in client.session

        client.post("/accounts/logout/")

        assert SESSION_KEY not in client.session

    def test_logout_post_redirects_to_root(self):
        """POST /accounts/logout/ must redirect to '/' (next_page='/')."""
        user = User.objects.create_user(username="logoutredir", password="s3cr3t!")
        client = Client()
        client.login(username="logoutredir", password="s3cr3t!")
        response = client.post("/accounts/logout/")
        assert response.status_code == 302
        assert response["Location"] == "/"


class TestLogoutViewNextPage(TestCase):
    """FrontendLogoutView must declare next_page='/' at the class level."""

    def test_next_page_is_root(self):
        from frontend.views import FrontendLogoutView
        self.assertEqual(FrontendLogoutView.next_page, "/")


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------

class TestLogoutTemplate(TestCase):
    """base.html must use a POST form for logout, not a plain anchor."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with open(TEMPLATE_PATH) as fh:
            cls.content = fh.read()

    def test_logout_not_rendered_as_get_link(self):
        """There must be no plain <a href="...account_logout..."> logout link."""
        self.assertNotIn(
            "href=\"{% url 'account_logout' %}\"",
            self.content,
            "Logout must not use a GET anchor — GET logout is rejected by Django 5.x",
        )

    def test_logout_form_exists(self):
        """A <form> whose action resolves to account_logout must exist."""
        self.assertRegex(
            self.content,
            r'action=.*account_logout',
        )

    def test_logout_form_method_is_post(self):
        """The logout form must declare method=\"post\"."""
        form_match = re.search(r'<form[^>]+account_logout[^>]*>', self.content)
        self.assertIsNotNone(form_match, "Logout form tag must exist")
        self.assertIn('method="post"', form_match.group(0).lower())

    def test_logout_form_has_csrf_token(self):
        """The logout form must include {% csrf_token %}."""
        form_block = re.search(
            r'action=.*account_logout.*?</form>', self.content, re.DOTALL
        )
        self.assertIsNotNone(form_block, "Logout form block must exist")
        self.assertIn("{% csrf_token %}", form_block.group(0))
