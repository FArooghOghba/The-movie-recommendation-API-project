import pytest

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.movie.models import Movie
from movie_recommendation_api.movie.selectors import get_movie_list
from movie_recommendation_api.movie.serializers import (
    MovieOutPutModelSerializer
)


pytestmark = pytest.mark.django_db

MOVIE_LIST_URL = reverse('api:movie:list')


def movie_detail_url(movie_slug: str) -> str:
    """
    Generate the URL for the movie detail API endpoint based on the movie slug.

    This function takes a movie slug as input and generates the URL for the
    movie detail API endpoint by using the `reverse` function provided by Django's
    URL resolver. The movie slug is included as a parameter in the URL.

    :param movie_slug: The slug of the movie.
    :return: The URL for the movie detail API endpoint.
    """
    return reverse(viewname='api:movie:detail', args=[movie_slug])


def test_get_zero_movie_should_return_empty_movie_list(api_client) -> None:
    """
    Test retrieving movie list when there are no movies available.

    This test verifies that when there are no movies in the database,
    the API returns an empty list of movies.

    :param api_client: A fixture providing the Django test client for API requests.
    :return: None
    """

    response = api_client.get(path=MOVIE_LIST_URL)
    assert response.status_code == status.HTTP_200_OK

    test_movies = Movie.objects.all()
    test_movie_output_serializer = MovieOutPutModelSerializer(test_movies, many=True)
    assert response.data['results'] == test_movie_output_serializer.data


def test_get_five_movies_should_return_success(
    api_client, api_request, five_test_movies
) -> None:

    """
    Test retrieving a list of five movies successfully.

    This test verifies that when there are five movies available in the database,
    the API returns the list of movies with the expected data.

    :param api_client: A fixture providing the Django test client for API requests.
    :param api_request: A fixture providing the Django REST framework API request
           factory.
    :param five_test_movies: A fixture providing five test movie objects.
    :return: None
    """

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, request=request)
    assert response.status_code == status.HTTP_200_OK

    # Get the queryset for all movies, prefetching related genres,
    # and deferring unnecessary fields.
    # Annotate the queryset with average ratings and order it by 'id'
    test_movies_queryset = get_movie_list().order_by('id')

    test_movies_output_serializer = MovieOutPutModelSerializer(
        test_movies_queryset, many=True, context={'request': request}
    )
    assert response.data['results'] == test_movies_output_serializer.data


def test_get_movies_with_genres_title_should_return_success(
        api_client, first_test_movie, second_test_movie, third_test_movie
) -> None:

    """
    Test retrieving a list of movies with associated genres.

    This test verifies that the API successfully returns a list of movies with their
    corresponding genre titles. It creates multiple movies with various genres using
    the 'test_movies' fixture. The test then makes a GET request to the movie list
    endpoint and checks if the genres in the response match the expected genres for
    each movie.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :param third_test_movie: A fixture providing the third test movie object.
    :return: None
    """

    response = api_client.get(path=MOVIE_LIST_URL)
    assert response.status_code == status.HTTP_200_OK

    test_movies = (first_test_movie, second_test_movie, third_test_movie)

    for index, test_movie in enumerate(test_movies):
        genres = test_movie.genre.all()

        movie_genres_response = response.data['results'][index]['genres']
        assert movie_genres_response == [genre.title for genre in genres]
