import pytest

from movie_recommendation_api.tests.factories.movie_factories import ReviewFactory


@pytest.fixture
def first_test_review():
    """
    Fixture for creating a test review.

    This fixture creates and returns a test review object using
    the `ReviewFactory` factory.

    :return: Review: A test review object.
    """
    return ReviewFactory()


@pytest.fixture
def second_test_review():
    """
    Fixture for creating a test review.

    This fixture creates and returns a test review object using
    the `ReviewFactory` factory.

    :return: Review: A test review object.
    """
    return ReviewFactory()
