import pytest

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
