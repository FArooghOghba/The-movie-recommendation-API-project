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
def test_movie_without_cast_crew() -> MovieFactory:
    """
    Fixture that creates a test movies.

    This fixture uses the MovieFactory to create a test movie
    and returns the created movie. The test movie can be used in tests that
    require a movie objects.

    :return: A test movie objects.
    """

    test_movie = MovieFactory.create()
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


@pytest.fixture
def three_test_movies() -> QuerySet[MovieFactory]:
    """
    Fixture that creates a batch of three test movies.

    This fixture uses the MovieFactory to create a batch of three test movies
    and yields the created movies. The test movies can be used in tests that
    require multiple movie objects.

    :return: A list of three test movie objects.
    """

    test_movies = MovieFactory.create_batch(3)
    yield test_movies


@pytest.fixture
def test_movie_with_cast_crew_role_and_two_user_ratings_and_reviews(
        test_movie_without_cast_crew, first_test_user, second_test_user,
        first_test_cast, first_test_crew, first_test_role, second_test_role,
        first_test_rating, second_test_rating,
        first_test_review, second_test_review
) -> None:

    """
    A fixture that creates a test movie with cast, crew, role, and two user ratings.

    This fixture creates a test movie with cast, crew, role, and two user ratings.
    It adds a rating for the first test user and the second test user to
    the test movie.
    It also creates a role for the cast member and the crew member in the test movie.

    :param test_movie_without_cast_crew: A fixture providing a test movie object
    without cast and crew roles.
    :param first_test_user: A fixture providing the first test user object.
    :param second_test_user: A fixture providing the second test user object.
    :param first_test_cast: A fixture providing the first test cast object.
    :param first_test_crew: A fixture providing the first test crew object.
    :param first_test_role: A fixture providing the first test role object.
    :param second_test_role: A fixture providing the second test role object.
    :param first_test_rating: A fixture providing the first test rating object.
    :param second_test_rating: A fixture providing the second test rating object.
    :param first_test_review: A fixture providing the first test review object.
    :param second_test_review: A fixture providing the second test review object.
    :return: None
    """

    # creating rating for the first test user in a first test movie.
    first_test_rating.user = first_test_user
    first_test_rating.movie = test_movie_without_cast_crew
    first_test_rating.save()

    # creating rating for the second test user in a first test movie.
    second_test_rating.user = second_test_user
    second_test_rating.movie = test_movie_without_cast_crew
    second_test_rating.save()

    # creating review for the first test user in a first test movie.
    first_test_review.user = first_test_user
    first_test_review.movie = test_movie_without_cast_crew
    first_test_review.save()

    # creating review for the second test user in a first test movie.
    second_test_review.user = second_test_user
    second_test_review.movie = test_movie_without_cast_crew
    second_test_review.save()

    # creating a role for cast member in the first test movie.
    first_test_role.movie = test_movie_without_cast_crew
    first_test_role.cast_crew = first_test_cast
    first_test_role.save()

    # creating a role for crew member in the first test movie.
    second_test_role.movie = test_movie_without_cast_crew
    second_test_role.cast_crew = first_test_crew
    second_test_role.save()

    test_movie_without_cast_crew.cast_crew.add(first_test_cast, first_test_crew)


@pytest.fixture
def test_movie_with_cast_crew_role(
    test_movie_without_cast_crew, first_test_role, second_test_role,
    first_test_cast, first_test_crew
) -> None:

    """
     A fixture that creates a test movie with cast, crew, and role.

    This fixture creates a test movie with cast, crew, and role.
    It creates a role for the cast member and the crew member in the test movie.

    :param test_movie_without_cast_crew: A fixture providing a test movie
    object without cast and crew roles.
    :param first_test_cast: A fixture providing the first test cast object.
    :param first_test_crew: A fixture providing the first test crew object.
    :param first_test_role: A fixture providing the first test role object.
    :param second_test_role: A fixture providing the second test role object.
    :return: None
    """

    # creating a role for cast member in the first test movie.
    first_test_role.movie = test_movie_without_cast_crew
    first_test_role.cast_crew = first_test_cast
    first_test_role.save()

    # creating a role for crew member in the first test movie.
    second_test_role.movie = test_movie_without_cast_crew
    second_test_role.cast_crew = first_test_crew
    second_test_role.save()

    test_movie_without_cast_crew.cast_crew.add(first_test_crew, first_test_cast)
