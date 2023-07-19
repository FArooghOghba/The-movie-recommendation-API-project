import pytest

from django.urls import reverse

from rest_framework import status


pytestmark = pytest.mark.django_db

MOVIE_LIST_URL = reverse('api:movie:list')


@pytest.mark.parametrize(
    'genres_filter, expected_movie_ids', [
        ('first_test_genre', {1, 2, 4, 5}),
        ('third_test_genre', {2, 3, 5}),
        ('second_test_genre, third_test_genre', {3, 5}),
        ('first_test_genre, second_test_genre, third_test_genre', {5}),
        ('', {1, 2, 3, 4, 5}),
    ]
)
def test_get_movie_by_filter_exact_genre_title(
    api_client, first_test_genre, second_test_genre, third_test_genre,
    five_test_movies, genres_filter, expected_movie_ids, request
) -> None:

    """
    Test the movie list endpoint with genre filtering.

    This test verifies that the movie list endpoint correctly filter
     movies based on genre titles.

    :param api_client: (APIClient): An instance of the Django REST Framework's
    APIClient.
    :param first_test_genre: A fixture providing the first test genre object.
    :param second_test_genre: A fixture providing the second test genre object.
    :param third_test_genre: A fixture providing the third test genre object.
    :param five_test_movies: (pytest fixture): A fixture that creates five test
     movies in the database.
    :param genres_filter: (str): A comma-separated string of genre fixture names
    to be used for filtering movies.
    :param expected_movie_ids: (set): The set of expected movie IDs that should be
    returned after filtering.
    :param request: (fixture request): Pytest fixture to access the requesting
    test context.
    :return: None
    """

    test_genres_filter = genres_filter

    # If genres_filter is provided, convert fixture names to genre titles
    if genres_filter:
        filters = []
        split_test_genres = genres_filter.split(',')
        for genre in split_test_genres:
            # Get the genre object from the fixture name and add its title
            # to the filters list
            get_test_genre_fixture = request.getfixturevalue(genre.strip())
            filters.append(get_test_genre_fixture.title)

        # Combine the genre titles to form the final genre filter string
        test_genres_filter = ','.join(filters)

    # Get the test movie objects
    first_test_movie,\
        second_test_movie,\
        third_test_movie,\
        forth_test_movie,\
        fifth_test_movie = five_test_movies

    first_test_movie.genre.add(first_test_genre, second_test_genre)
    second_test_movie.genre.add(first_test_genre, third_test_genre)
    third_test_movie.genre.add(second_test_genre, third_test_genre)
    forth_test_movie.genre.add(first_test_genre)
    fifth_test_movie.genre.add(first_test_genre, second_test_genre, third_test_genre)

    filter_params = {'genre__title': test_genres_filter}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_200_OK

    expected_movies = expected_movie_ids
    response_movie_ids = {movie['id'] for movie in response.data['results']}

    assert response_movie_ids == expected_movies


def test_get_movie_by_filter_partial_genre_title(
    api_client, three_test_movies, first_test_genre, second_test_genre
) -> None:

    """
    Test partial filtering of movies by genre title.

    This test verifies that the movie list endpoint correctly filters movies
    based on the first three characters of the genre title. It creates three
    test movies and assigns genres to them. Then, it applies the partial
    filtering using the `genre__title` field with the first three characters
    of the `first_test_genre` title.

    The test expects that only `first_test_movie` and `third_test_movie` should
    be included in the response, as they have genres whose titles start with the
    provided filter. The response is then compared with the expected set of
    movie IDs.

    Raises:
        AssertionError: If the test assertions fail.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param three_test_movies: A fixture that creates three test
    movies in the database.
    :param first_test_genre: A fixture that creates the first
    test genre in the database.
    :param second_test_genre: A fixture that creates the second
    test genre in the database.
    :return: None
    """

    first_test_movie, \
        second_test_movie, \
        third_test_movie = three_test_movies

    first_test_movie.genre.add(first_test_genre, second_test_genre)
    second_test_movie.genre.add(second_test_genre)
    third_test_movie.genre.add(first_test_genre)

    # Apply the partial filtering using the first three characters of the genre title
    partial_genre_title = first_test_genre.title[:3]
    filter_params = {'genre__title': partial_genre_title}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_200_OK

    expected_movies = {first_test_movie.id, third_test_movie.id}
    response_movie_ids = {movie['id'] for movie in response.data['results']}

    assert response_movie_ids == expected_movies


def test_get_movie_by_filter_genre_title_more_than_limit_should_return_error(
        api_client, first_test_movie, first_test_genre, second_test_genre,
        third_test_genre, forth_test_genre, fifth_test_genre
) -> None:

    """
    Test filtering movies by genre title with more than the allowed limit.

    This test verifies that when the client attempts to filter movies by
    genre title with more than the allowed limit (in this case, more than 4 genres),
    the API responds with a 'HTTP 400 Bad Request' error and provides an appropriate
    error message.

    The test constructs a comma-separated string of genre titles exceeding the limit
    and includes it in the filter_params. It then makes a GET request to the movie
    list endpoint with the provided filters. The test expects the API to respond with
    an HTTP 400 status code and an error message indicating that the client cannot
    add more than 4 genres.

    Raises:
        AssertionError: If the test assertions fail.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture that creates the first test
    movie in the database.
    :param first_test_genre: A fixture that creates the first test
    genre in the database.
    :param second_test_genre: A fixture that creates the second test
    genre in the database.
    :param third_test_genre: A fixture that creates the third test
    genre in the database.
    :param forth_test_genre: A fixture that creates the forth test
    genre in the database.
    :param fifth_test_genre: A fixture that creates the fifth test
    genre in the database.
    :return: None
    """

    # Apply genre title with more than the allowed limit
    more_than_limit_genre_title = f'{first_test_genre.title}, ' \
                                  f'{second_test_genre.title}, ' \
                                  f'{third_test_genre.title}, ' \
                                  f'{forth_test_genre.title}, ' \
                                  f'{fifth_test_genre.title}'
    filter_params = {'genre__title': more_than_limit_genre_title}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check the error message in the response data
    expected_error_message = "Filter Error - You cannot add more than 4 genres"
    assert response.data["detail"] == expected_error_message
