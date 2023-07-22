import pytest

from django.urls import reverse

from rest_framework import status


pytestmark = pytest.mark.django_db

MOVIE_LIST_URL = reverse('api:movie:list')


def test_get_movie_by_filter_title_and_synopsis_field(
    api_client, django_db_reset_sequences, five_test_movies
) -> None:

    """
    Test the API endpoint for filtering movies by title and synopsis.

    This test verifies that the movie list endpoint correctly filters movies
    based on search criteria in both the movie title and synopsis. It creates
    five test movie objects, modifies the title and synopsis of some movies
    to include the search term, and then performs a search using the API client.
    The test expects that the API response will contain movies that match
    the search term in either the title or synopsis or both.

    :param api_client: A fixture providing the Django test client for API requests.
    :param django_db_reset_sequences: A fixture that resets database sequences to
    prevent primary key conflicts.
    :param five_test_movies: A fixture providing five test movie objects.

    :return: None
    """

    # Get the test movie objects
    first_test_movie, \
        second_test_movie, \
        third_test_movie, \
        forth_test_movie, \
        fifth_test_movie = five_test_movies

    # Modify the title and synopsis of certain movies to include
    # the search term 'star'.

    first_test_movie.title = "Star Trek"
    first_test_movie.save()

    third_test_movie.synopsis = "Star Wars"
    third_test_movie.save()

    fifth_test_movie.title = "Stardust"
    fifth_test_movie.synopsis = "This is Stardust movie."
    fifth_test_movie.save()

    filter_params = {'search': 'star'}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3

    response_movie_ids = {
        test_movie['id'] for test_movie in response.data['results']
    }
    # Assert that the response contains the correct movie IDs for movies
    # matching the search term.
    assert response_movie_ids == {
        first_test_movie.id, third_test_movie.id, fifth_test_movie.id
    }
