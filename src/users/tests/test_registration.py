import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
def test_registration_success(client):
    """
    Test success user registration.
    :param client:
    :return:
    """
    url = reverse("register")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "@Test123",
        "password2": "@Test123",
    }

    response = client.post(url, data)

    assert response.status_code == 302, f"Expected 302, got {response.status_code}. Errors: {response.content.decode()}"
    assert "Location" in response.headers, f"Headers: {response.headers}"
    assert response.headers["Location"] == reverse("home")

    assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_registration_password_mismatch(client):
    """
    Test mismatch user password.
    :param client:
    :return:
    """
    url = reverse("register")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "@Test123",
        "password2": "@Test1234",
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert "The two password fields didn’t match." in response.content.decode()

    assert not User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_registration_existing_username(client):
    """
    Test register with an existing name.
    :param client:
    :return:
    """
    User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="@Test123",
    )

    url = reverse("register")
    data = {
        "username": "testuser",
        "email": "test2@example.com",
        "password1": "@Test123",
        "password2": "@Test123",
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert ("A user with that username already exists." in
            response.content.decode())


@pytest.mark.django_db
def test_registration_existing_email(client):
    """
    Test register with an existing email.
    :param client:
    :return:
    """
    User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="@Test123",
    )

    url = reverse("register")
    data = {
        "username": "testuser2",
        "email": "test@example.com",
        "password1": "@Test123",
        "password2": "@Test123",
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert ("Этот email уже зарегистрирован." in
            response.content.decode())
