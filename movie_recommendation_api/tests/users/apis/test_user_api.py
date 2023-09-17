"""
Tests for the user API.
"""

import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status

import json


pytestmark = pytest.mark.django_db

CREATE_USER_URL = reverse('api:users:register')


# ___ Test the public features of the user RegisterAPI for creating user. ___ #

def test_register_for_create_user_successful(
    api_client, first_test_user_payload
) -> None:
    """
    Test the successful creation of a user via the RegisterAPI.
    :param api_client: (Client): The Django test client
           used to make HTTP requests to the API.
    :param first_test_user_payload: (dict): A fixture that provides a
           pre-configured user payload for testing.
    :return: None: This test does not return any value.
    """

    response = api_client.post(
        path=CREATE_USER_URL,
        data=first_test_user_payload
    )
    assert response.status_code == status.HTTP_201_CREATED

    test_user = get_user_model().objects.get(email=first_test_user_payload['email'])
    assert test_user.check_password(first_test_user_payload['password']) is True
    assert 'password' not in response.data

    response_content = json.loads(response.content)
    token = response_content['token']
    assert 'access_token' in token
    assert 'refresh_token' in token


def test_register_for_create_user_with_existing_email_return_error(
    api_client, create_test_user, first_test_user_payload
) -> None:
    """
    Test error returned if user with email exists via the RegisterAPI.
    :param api_client: (Client): The Django test client
           used to make HTTP requests to the API.
    :param create_test_user: (BaseUser): A fixture that
           provides test user for testing.
    :param first_test_user_payload: (dict): A fixture that
           provides a pre-configured user payload for testing.
    :return: None: This test does not return any value.
    """

    create_test_user(**first_test_user_payload)

    response = api_client.post(
        path=CREATE_USER_URL,
        data=first_test_user_payload
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_for_create_user_with_existing_username_return_error(
    api_client, create_test_user, first_test_user_payload
) -> None:
    """
    Test error returned if user with username exists via the RegisterAPI.
    :param api_client: (Client): The Django test client
           used to make HTTP requests to the API.
    :param create_test_user: (BaseUser): A fixture that
           provides test user for testing.
    :param first_test_user_payload: (dict): A fixture that
           provides a pre-configured user payload for testing.
    :return: None: This test does not return any value.
    """

    first_test_user_payload['email'] = 'test_email@example.com'
    create_test_user(**first_test_user_payload)

    response = api_client.post(
        path=CREATE_USER_URL,
        data=first_test_user_payload
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    'password, error',
    [
        ('test_password', "password must include number"),
        ('13?1_54??.', "password must include letter"),
        ('test0password', "password must include special char"),
        ('test_pas5', 'Ensure this value has at least 10 characters (it has 9).'),
    ],
)
def test_register_for_validation_password_error(
    password, error, api_client, first_test_user_payload
) -> None:
    """
    Test an error is returned if password is less than 5 chars via the RegisterAPI.
    :param api_client: (Client): The Django test client
           used to make HTTP requests to the API.
    :param first_test_user_payload: (dict): A fixture that
           provides a pre-configured user payload for testing.
    :return: None: This test does not return any value.
    """

    first_test_user_payload['password'] = password

    response = api_client.post(
        path=CREATE_USER_URL,
        data=first_test_user_payload
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_error = json.loads(response.content)['detail']['password']
    assert error in response_error

    user_exists = get_user_model().objects.filter(
        email=first_test_user_payload['email']
    ).exists()
    assert user_exists is False
