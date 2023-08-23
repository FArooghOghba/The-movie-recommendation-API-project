import pytest
from django.db.models import QuerySet

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


@pytest.fixture
def five_test_ratings() -> QuerySet[RatingFactory]:
    """
    Fixture that creates a batch of five test movies.

    This fixture uses the MovieFactory to create a batch of five test movies
    and yields the created movies. The test movies can be used in tests that
    require multiple movie objects.

    :return: A list of five test movie objects.
    """

    test_ratings = RatingFactory.create_batch(5)
    yield test_ratings
