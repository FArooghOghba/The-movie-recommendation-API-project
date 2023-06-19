"""
Tests for the user API.
"""

import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status


pytestmark = pytest.mark.django_db

CREATE_USER_URL = reverse('user:create')


# ___ Test the public features of the user RegisterAPI for creating user. ___ #

def test_create_user_success(api_client, first_test_user) -> None:
    """
    Test the successful creation of a user via the RegisterAPI.
    :param api_client: (Client): The Django test client
           used to make HTTP requests to the API.
    :param first_test_user: (BaseUserFactory): A fixture that
           provides a pre-configured user payload for testing.
    :return: None: This test does not return any value.
    """

    test_user_payload = first_test_user.create_payload()
    response = api_client.post(
        path=CREATE_USER_URL,
        data=test_user_payload
    )
    assert response.status_code == status.HTTP_201_CREATED

    test_user = get_user_model().objects.get(email=test_user_payload['email'])
    assert test_user.check_password(test_user_payload['password']) is True
    assert 'password' not in response.data


def test_create_user_with_existing_email_return_error(api_client, create_test_user, first_test_user) -> None:
    """
    Test error returned if user with email exists via the RegisterAPI.
    :param api_client: (Client): The Django test client
           used to make HTTP requests to the API.
    :param create_test_user: (BaseUser): A fixture that
           provides test user for testing.
    :param first_test_user: (BaseUserFactory): A fixture that
           provides a pre-configured user payload for testing.
    :return: None: This test does not return any value.
    """

    test_user_payload = first_test_user.create_payload()
    create_test_user(**test_user_payload)

    response = api_client.post(
        path=CREATE_USER_URL,
        data=test_user_payload
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user_with_existing_username_return_error(api_client, create_test_user, first_test_user) -> None:
    """
    Test error returned if user with username exists via the RegisterAPI.
    :param api_client: (Client): The Django test client
           used to make HTTP requests to the API.
    :param create_test_user: (BaseUser): A fixture that
           provides test user for testing.
    :param first_test_user: (BaseUserFactory): A fixture that
           provides a pre-configured user payload for testing.
    :return: None: This test does not return any value.
    """

    test_user_payload = first_test_user.create_payload()
    test_user_payload['email'] = 'test_email@example.com'
    create_test_user(**test_user_payload)

    response = api_client.post(
        path=CREATE_USER_URL,
        data=test_user_payload
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user_with_short_pass_return_error(api_client, first_test_user) -> None:
    """
    Test an error is returned if password is less than 5 chars via the RegisterAPI.
    :param api_client: (Client): The Django test client
           used to make HTTP requests to the API.
    :param first_test_user: (BaseUserFactory): A fixture that
           provides a pre-configured user payload for testing.
    :return: None: This test does not return any value.
    """

    test_user_payload = first_test_user.create_payload()
    test_user_payload['password'] = 'te'

    response = api_client.post(
        path=CREATE_USER_URL,
        data=test_user_payload
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    user_exists = get_user_model().objects.filter(
        email=test_user_payload['email']
    ).exists()
    assert user_exists is False
