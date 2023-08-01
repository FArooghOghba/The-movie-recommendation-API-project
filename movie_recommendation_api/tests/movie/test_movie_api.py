import pytest
from django.db.models.aggregates import Avg

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.movie.models import Movie
from movie_recommendation_api.movie.selectors import get_movie_list
from movie_recommendation_api.movie.serializers import (
    MovieDetailOutPutModelSerializer, MovieOutPutModelSerializer
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


def test_get_movie_detail_should_success(api_client, first_test_movie) -> None:
    """
    Test retrieving details of a specific movie successfully.

    This test verifies that when requesting the details of a specific movie,
    the API returns the movie details with the expected data.

    :param api_client: A fixture providing the Django test client for API requests.
    :param first_test_movie: A fixture providing the first test movie object.
    :return: None
    """

    url = movie_detail_url(movie_slug=first_test_movie.slug)
    response = api_client.get(path=url)

    first_test_movie.avg_rating = first_test_movie.movie_ratings.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating']
    test_movie_output_serializer = MovieDetailOutPutModelSerializer(first_test_movie)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == test_movie_output_serializer.data


def test_get_nonexistent_movie_detail_should_return_error(api_client) -> None:
    """
    Test retrieving details of a nonexistent movie.

    This test verifies that when requesting the details of a movie
    that does not exist, the API returns a not found error.

    :param api_client: A fixture providing the Django test client for API requests.
    :return: None
    """

    url = movie_detail_url(movie_slug='nonexistent-slug')
    response = api_client.get(path=url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_post_rate_to_movie_should_success(
    api_client, first_test_movie, first_test_user
) -> None:
    """
    Test that a user can successfully rate a movie through the API.

    This test ensures that an authorized user can post a valid rating for a movie.
    The user's authentication is forced using the 'api_client.force_authenticate()'
    method, and the 'api_client.post()' method is used to post the rating.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :param first_test_user: A fixture providing the first test user object.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    url = movie_detail_url(movie_slug=first_test_movie.slug)
    payload = {'rate': 7}

    response = api_client.post(path=url, data=payload)
    assert response.status_code == status.HTTP_201_CREATED


def test_post_rate_to_movie_with_unauthorized_user_should_error(
    api_client, first_test_movie
) -> None:
    """
    Test that an unauthorized user cannot rate a movie and receives an error.

    This test verifies that an unauthenticated user receives
    a 401 Unauthorized status when trying to post a rating for a movie.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :return: None
    """

    url = movie_detail_url(movie_slug=first_test_movie.slug)
    payload = {'rate': 7}

    response = api_client.post(path=url, data=payload)
    print(response.content)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    'wrong_rate', (
        'wrong rate',
        5.5,
        '',
        ' ',
    )
)
def test_post_rate_to_movie_with_wrong_data_should_error(
    api_client, first_test_movie, first_test_user, wrong_rate
) -> None:
    """
     Test that posting a rating with wrong data returns a 400 Bad Request error.

    This parameterized test checks various cases where the provided rate data
    is invalid, such as wrong rate format, non-integer rate, empty string,
    or whitespace.

    The test ensures that the API returns a 400 Bad Request status for each
    nvalid case.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :param first_test_user: A fixture providing the first test user object.
    :param wrong_rate: A parameter representing invalid rate values.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    url = movie_detail_url(movie_slug=first_test_movie.slug)
    payload = {'rate': wrong_rate}

    response = api_client.post(path=url, data=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
