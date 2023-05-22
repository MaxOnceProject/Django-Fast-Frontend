import pytest
from django.contrib.auth.models import User
from django.test import Client

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
