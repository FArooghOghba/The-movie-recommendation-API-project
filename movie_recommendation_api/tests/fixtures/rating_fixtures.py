import pytest

from movie_recommendation_api.tests.factories.movie_factories import RatingFactory


@pytest.fixture
def first_test_rating():

    return RatingFactory()


@pytest.fixture
def second_test_rating():

    return RatingFactory()
