
import pytest

from django.contrib.auth import get_user_model

from movie_recommendation_api.users.models import BaseUser
from movie_recommendation_api.tests.factories.user_factories import (
    BaseUserFactory, ProfileFactory
)

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


@pytest.fixture
def third_test_user() -> BaseUserFactory:
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
def first_test_user_profile() -> ProfileFactory:
    """
    Fixture for creating a test user profile instance.

    This fixture uses the `ProfileFactory` factory
    to create a test user profile instance.
    The created user profile can be used in tests
    to simulate a user profile with predefined
    attributes for testing various scenarios.
    :return: a test user profile instance
    """

    return ProfileFactory()


@pytest.fixture
def first_test_picture_payload() -> dict:
    """
    Fixture for creating a test user profile picture instance.

    This fixture uses the `ProfileFactory` factory
    to create a test user profile picture instance.
    The created picture can be used in tests to simulate
    a picture with predefined attributes for testing various scenarios.

    :return: a dict test user profile picture payload
    """

    return ProfileFactory.create_image_file_payload()
