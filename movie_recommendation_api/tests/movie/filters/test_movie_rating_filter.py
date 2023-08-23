import pytest

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.movie.selectors import get_movie_list
from movie_recommendation_api.movie.serializers import MovieOutPutModelSerializer


pytestmark = pytest.mark.django_db

MOVIE_LIST_URL = reverse('api:movie:list')


def test_get_movies_by_filter_min_rating_success(
    api_request, api_client, five_test_ratings
) -> None:

    """
    Test filtering movies by a minimum rating.

    This test case ensures that movies can be filtered by a minimum rating value.
    It sets different ratings for test movies, then sends a GET request to the
    movie list endpoint with a 'min_rating' filter. The test checks that the
    response contains only movies with ratings greater than the specified minimum.

    :param api_request: An instance of the Django test client.
    :param api_client: An instance of the API client.
    :param five_test_ratings: A fixture providing five test movie ratings.
    :return: None
    """

    # Set different ratings for test movies
    ratings = [6.4, 7.3, 7.9, 8.2, 9.1]

    for index, obj in enumerate(five_test_ratings):
        obj.rating = ratings[index]
        obj.save()

    # Specify the minimum rating for filtering
    min_rating = 7.5
    filter_params = {'min_rating': min_rating}

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    # Ensure a successful response and correct number of results
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3

    for movie in response.data['results']:
        assert movie['rate'] > min_rating

    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data


def test_get_movies_by_filter_max_rating_success(
    api_request, api_client, five_test_ratings
) -> None:

    """
    Test filtering movies by a maximum rating.

    This test case ensures that movies can be filtered by a maximum rating value.
    It sets different ratings for test movies, then sends a GET request to the
    movie list endpoint with a 'max_rating' filter. The test checks that the
    response contains only movies with ratings less than the specified maximum.

    :param api_request: An instance of the Django test client.
    :param api_client: An instance of the API client.
    :param five_test_ratings: A fixture providing five test movie ratings.
    :return: None
    """

    # Set different ratings for test movies
    ratings = [6.4, 7.3, 7.9, 8.2, 9.1]

    for index, obj in enumerate(five_test_ratings):
        obj.rating = ratings[index]
        obj.save()

    # Specify the maximum rating for filtering
    max_rating = 8.0
    filter_params = {'max_rating': max_rating}

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    # Ensure a successful response and correct number of results
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3

    for movie in response.data['results']:
        assert movie['rate'] < max_rating

    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data


def test_get_movies_by_filter_range_rating_success(
    api_request, api_client, five_test_ratings
) -> None:

    """
    Test filtering movies by a rating range.

    This test case ensures that movies can be filtered by a rating range defined
    by both minimum and maximum rating values. It sets different ratings for
    test movies, then sends a GET request to the movie list endpoint with
    'min_rating' and 'max_rating' filters. The test checks that the response
    contains only movies with ratings within the specified range.

    :param api_request: An instance of the Django test client.
    :param api_client: An instance of the API client.
    :param five_test_ratings: A fixture providing five test movie ratings.
    :return: None
    """

    # Set different ratings for test movies
    ratings = [6.4, 7.3, 7.9, 8.2, 9.1]

    for index, obj in enumerate(five_test_ratings):
        obj.rating = ratings[index]
        obj.save()

    max_rating = 8.0
    min_rating = 6.5
    filter_params = {
        'max_rating': max_rating,
        'min_rating': min_rating
    }

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2

    for movie in response.data['results']:
        assert min_rating < movie['rate'] < max_rating

    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data
