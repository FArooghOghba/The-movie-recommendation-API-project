"""
Coftest for tests
"""

import pytest

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from movie_recommendation_api.users.models import BaseUser
from movie_recommendation_api.tests.factories import BaseUserFactory

from typing import Callable
from datetime import datetime


@pytest.fixture
def api_client():
    """
    Fixture for creating an instance of the Django REST Framework's APIClient.
    :return: APIClient()
    """
    return APIClient()


@pytest.fixture
def time_tracker() -> str:
    """
    Fixture for tracking the runtime of a test or a block of code.

    This fixture captures the start time before executing the test or
    the block of code, and calculates the elapsed time after the execution.
    It then prints the runtime in seconds.
    :return:
    """
    tick = datetime.now()
    yield

    tock = datetime.now()
    diff = tock - tick
    print(f'\n runtime: {diff.total_seconds()}')


@pytest.fixture
def create_test_user(**params) -> Callable:
    """Create and return a new user."""

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

    This fixture uses the `BaseUserFactory` factory to create a test user instance.
    The created user can be used in tests to simulate a user with predefined attributes
    for testing various scenarios.
    :return: a dict test user payload
    """

    return BaseUserFactory.create_payload()
