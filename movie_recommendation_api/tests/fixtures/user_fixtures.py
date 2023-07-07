
import pytest

from django.contrib.auth import get_user_model

from movie_recommendation_api.users.models import BaseUser
from movie_recommendation_api.tests.factories.user_factories import BaseUserFactory

from typing import Callable


@pytest.fixture
def create_test_user(**params) -> Callable:
    """
    Fixture for creating and returning a new user.

    This fixture returns a callable function that can be used to create
    a new user with the provided parameters. The user is created using
    the `create_user` method of the user model specified in the project settings.

    :param params: Keyword arguments representing the user parameters
    (e.g., email, username, password).
    :return: Callable: A function that can be called to create a new user
    with the provided parameters.
    """

    def _create_test_user(**params) -> BaseUser:
        return get_user_model().objects.create_user(
            email=params['email'],
            username=params['username'],
            password=params['password']
        )

    return _create_test_user


@pytest.fixture
def first_test_user_payload() -> dict:
    """
    Fixture for creating a test user instance.

    This fixture uses the `BaseUserFactory` factory
    to create a test user instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.
    :return: a dict test user payload
    """

    return BaseUserFactory.create_payload()


@pytest.fixture
def first_test_user() -> BaseUserFactory:
    """
    Fixture for creating a test user instance.

    This fixture uses the `BaseUserFactory` factory
    to create a test user instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.
    :return: a test user instance
    """

    return BaseUserFactory()


@pytest.fixture
def second_test_user() -> BaseUserFactory:
    """
    Fixture for creating a test user instance.

    This fixture uses the `BaseUserFactory` factory
    to create a test user instance. The created user
    can be used in tests to simulate a user with predefined
    attributes for testing various scenarios.
    :return: a test user instance
    """

    return BaseUserFactory()
