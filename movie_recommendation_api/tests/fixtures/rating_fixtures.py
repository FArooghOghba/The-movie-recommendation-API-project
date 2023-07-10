import pytest

from movie_recommendation_api.tests.factories.movie_factories import RatingFactory


@pytest.fixture
def first_test_rating():
    """
    Fixture for creating a test rating.

    This fixture creates and returns a test rating object using
    the `RatingFactory` factory.

    :return: Rating: A test rating object.
    """
    return RatingFactory()


@pytest.fixture
def second_test_rating():
    """
    Fixture for creating a test rating.

    This fixture creates and returns a test rating object using
    the `RatingFactory` factory.

    :return: Rating: A test rating object.
    """
    return RatingFactory()
