import pytest
from django.contrib.admin.utils import display_for_field
from django.contrib.auth.models import User
from django.test import Client

from app.models import Author
from frontend import site


@pytest.mark.django_db
def test_user_anonymous():
    """
    Test if anonymous users get a redirect when accounts are activated.
    """

    client = Client()

    response = client.get("/")
    assert response.status_code == 302

    response = client.get("/app/")
    assert response.status_code == 302

    response = client.get("/app/author/")
    assert response.status_code == 302

@pytest.mark.django_db
def test_user_is_authenticated():
    """
    Test if authenticated users are able to access protected sites.
    """
    user_password = "top_secret"
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password=user_password
    )
    assert User.objects.get(username=user.username).username == 'testuser'

    client = Client()
    response_login = client.login(username=user.username, password=user_password)
    assert response_login

    response = client.get("/")
    assert response.status_code == 200

    response = client.get("/app/")
    assert response.status_code == 200

    response = client.get("/app/author/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_view_redirects_to_root_after_successful_authentication():
    user_password = "top_secret"
    User.objects.create_user(
        username="redirectuser",
        email="redirect@example.com",
        password=user_password,
    )

    client = Client()
    response = client.post(
        "/accounts/login/",
        {"username": "redirectuser", "password": user_password},
    )

    assert response.status_code == 302
    assert response["Location"] == "/"


@pytest.mark.django_db
def test_global_authentication_off():
    """
    Test if turning off login_required allows anonymous users to access protected sites.
    """
    global_config = site.get_global_config()
    global_config.login_required = False

    client = Client()

    response = client.get("/")
    assert response.status_code == 200

    response = client.get("/app/")
    assert response.status_code == 200

    response = client.get("/app/author/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_action_labels_are_rendered_from_metadata():
    """Configured action descriptions should be rendered instead of titleized method names."""
    user_password = "top_secret"
    user = User.objects.create_user(
        username="labeluser",
        email="label@example.com",
        password=user_password,
    )
    Author.objects.create(name="Ada", title="Dr")

    client = Client()
    assert client.login(username=user.username, password=user_password)

    response = client.get("/app/author/")

    assert response.status_code == 200
    assert b"Do Everything" in response.content
    assert b"Do Everything Twice" in response.content
    assert b"Mark As Checked" in response.content
    assert b"Mark As Unchecked" in response.content


@pytest.mark.django_db
def test_change_page_renders_non_editable_fields_as_readonly_values():
    user_password = "top_secret"
    user = User.objects.create_user(
        username="readonlyuser",
        email="readonly@example.com",
        password=user_password,
    )
    author = Author.objects.create(name="Ada", title="Dr")

    client = Client()
    assert client.login(username=user.username, password=user_password)

    response = client.get(f"/app/author/table_change/{author.id}")

    expected_created_at = display_for_field(
        author.created_at,
        Author._meta.get_field("created_at"),
        "-",
    )

    assert response.status_code == 200
    assert b'name="name"' in response.content
    assert b'name="title"' in response.content
    assert b'name="created_at"' not in response.content
    assert b"Created at" in response.content
    assert str(expected_created_at).encode() in response.content


@pytest.mark.django_db
def test_add_page_omits_non_editable_fields_from_generated_form():
    user_password = "top_secret"
    user = User.objects.create_user(
        username="addreadonlyuser",
        email="addreadonly@example.com",
        password=user_password,
    )

    client = Client()
    assert client.login(username=user.username, password=user_password)

    response = client.get("/app/author/table_add")

    assert response.status_code == 200
    assert b'name="name"' in response.content
    assert b'name="title"' in response.content
    assert b'name="created_at"' not in response.content
    assert b"Created at" not in response.content
