import pytest

from movie_recommendation_api.tests.factories.movie_factories import GenreFactory


@pytest.fixture
def first_test_genre() -> GenreFactory:
    """
    Fixture for creating and returning a test genre.

    This fixture creates a test genre using the `GenreFactory()` method
    from the movie factories. The created genre is returned for use in tests.

    :return: Genre: A test genre object.
    """
    return GenreFactory()


@pytest.fixture
def second_test_genre() -> GenreFactory:
    """
    Fixture for creating and returning a test genre.

    This fixture creates a test genre using the `GenreFactory()` method
    from the movie factories. The created genre is returned for use in tests.

    :return: Genre: A test genre object.
    """
    return GenreFactory()


@pytest.fixture
def third_test_genre() -> GenreFactory:
    """
    Fixture for creating and returning a test genre.

    This fixture creates a test genre using the `GenreFactory()` method
    from the movie factories. The created genre is returned for use in tests.

    :return: Genre: A test genre object.
    """
    return GenreFactory()
