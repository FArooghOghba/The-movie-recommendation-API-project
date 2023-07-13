import pytest

from django.db.models import QuerySet

from movie_recommendation_api.tests.factories.movie_factories import MovieFactory


@pytest.fixture
def first_test_movie(
    first_test_genre, second_test_genre, first_test_crew, first_test_cast
) -> MovieFactory:

    """
    Fixture for creating the first test movie.

    This fixture creates a MovieFactory instance with the provided
    genre, crew, and cast. It returns the created movie object for
    testing purposes.

    :param first_test_genre: (fixture): The first test genre fixture.
    :param second_test_genre: (fixture): The second test genre fixture.
    :param first_test_crew: (fixture): The first test crew fixture.
    :param first_test_cast: (fixture): The first test cast fixture.
    :return: MovieFactory: The created movie object.
    """

    test_movie = MovieFactory.create(
        genre=[first_test_genre, second_test_genre],
        cast_crew=[first_test_crew, first_test_cast],
    )
    return test_movie


@pytest.fixture
def second_test_movie(
    first_test_genre, second_test_genre, first_test_crew,
    first_test_cast, second_test_cast
) -> MovieFactory:

    """
    Fixture for creating the second test movie.

    This fixture creates a MovieFactory instance with the provided
    genre, crew, and cast. It returns the created movie object for
    testing purposes.

    :param first_test_genre: (fixture): The first test genre fixture.
    :param second_test_genre: (fixture): The second test genre fixture.
    :param first_test_crew: (fixture): The first test crew fixture.
    :param first_test_cast: (fixture): The first test cast fixture.
    :param second_test_cast: (fixture): The second test cast fixture.
    :return: MovieFactory: The created movie object.
    """

    test_movie = MovieFactory.create(
        genre=[first_test_genre, second_test_genre],
        cast_crew=[first_test_crew, first_test_cast, second_test_cast],
    )
    return test_movie


@pytest.fixture
def third_test_movie(
    second_test_genre, third_test_genre, second_test_crew,
    first_test_cast, third_test_cast
) -> MovieFactory:

    """
    Fixture for creating the second test movie.

    This fixture creates a MovieFactory instance with the provided
    genre, crew, and cast. It returns the created movie object for
    testing purposes.

    :param second_test_genre: (fixture): The second test genre fixture.
    :param third_test_genre: (fixture): The third test genre fixture.
    :param second_test_crew: (fixture): The second test crew fixture.
    :param first_test_cast: (fixture): The first test cast fixture.
    :param third_test_cast: (fixture): The third test cast fixture.
    :return: MovieFactory: The created movie object.
    """

    test_movie = MovieFactory.create(
        genre=[second_test_genre, third_test_genre],
        cast_crew=[second_test_crew, first_test_cast, third_test_cast],
    )
    return test_movie


@pytest.fixture
def five_test_movies() -> QuerySet[MovieFactory]:
    """
    Fixture that creates a batch of five test movies.

    This fixture uses the MovieFactory to create a batch of five test movies
    and yields the created movies. The test movies can be used in tests that
    require multiple movie objects.

    :return: A list of five test movie objects.
    """

    test_movies = MovieFactory.create_batch(5)
    yield test_movies
