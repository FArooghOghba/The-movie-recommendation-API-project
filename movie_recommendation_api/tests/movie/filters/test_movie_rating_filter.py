import pytest
from decimal import Decimal

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.movie.selectors import get_movie_list
from movie_recommendation_api.movie.serializers.movie_list_serializers import (
    MovieOutPutModelSerializer
)


pytestmark = pytest.mark.django_db

MOVIE_LIST_URL = reverse('api:movie:list')


@pytest.mark.parametrize(
    'rating_filter', [
        'min_rating',
        'max_rating',
    ]
)
def test_get_movies_by_filter_wrong_rating_return_error(
    api_request, api_client, five_test_ratings, rating_filter
) -> None:

    """
    Test that when an invalid rating is passed as a filter parameter,
    the API returns a 400 Bad Request error.

    :param api_request: The API request object.
    :param api_client: The API client object.
    :param five_test_ratings: A list of five test movie ratings.
    :param rating_filter: The rating filter to use
    (either 'min_rating' or 'max_rating').
    """

    # Set different ratings for test movies
    ratings = [6.5, 7.3, 7.9, 8.2, 9.1]

    for index, obj in enumerate(five_test_ratings):
        obj.rating = ratings[index]
        obj.save()

    # Specify the minimum rating for filtering
    rating = 'wrong_rate'
    filter_params = {rating_filter: rating}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    # Ensure a successful response and correct number of results
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    'rate, result_count', [
        (7.5, 3),
        (6.5, 5),
        (9.5, 0),
        (6, 5),
        ('', 5),
    ]
)
def test_get_movies_by_filter_min_rating_return_success(
    api_request, api_client, five_test_ratings, rate, result_count
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
    :param rate: The minimum rating to filter by.
    :param result_count: The expected number of results returned by the filter.
    :return: None
    """

    # Set different ratings for test movies
    ratings = [6.5, 7.3, 7.9, 8.2, 9.1]

    for index, obj in enumerate(five_test_ratings):
        obj.rating = ratings[index]
        obj.save()

    # Specify the minimum rating for filtering
    min_rating = rate
    filter_params = {'min_rating': min_rating}

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    # Ensure a successful response and correct number of results
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == result_count

    if not rate == '':
        for movie in response.data['results']:
            assert movie['rate'] >= min_rating

    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data


@pytest.mark.parametrize(
    'rate, result_count', [
        (8, 3),
        (6.5, 1),
        (9.5, 5),
        (6.0, 0),
        ('', 5),
    ]
)
def test_get_movies_by_filter_max_rating_return_success(
    api_request, api_client, five_test_ratings, rate, result_count
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
    :param rate: The maximum rating to filter by.
    :param result_count: The expected number of results returned by the filter.
    :return: None
    """

    # Set different ratings for test movies
    ratings = [6.5, 7.3, 7.9, 8.2, 9.1]

    for index, obj in enumerate(five_test_ratings):
        obj.rating = ratings[index]
        obj.save()

    # Specify the maximum rating for filtering
    max_rating = rate
    filter_params = {'max_rating': max_rating}

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    # Ensure a successful response and correct number of results
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == result_count

    if not rate == '':
        for movie in response.data['results']:
            assert movie['rate'] <= max_rating

    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data


@pytest.mark.parametrize(
    'min_rate, max_rate, result_count', [
        (6.5, 8, 2),
        (6.4, 8.5, 4),
        (9.5, 9.7, 0),
        (6.0, 6.2, 0),
        (9.0, 9.1, 1),
        (6.0, 9.5, 5),
        ('', '', 5),
    ]
)
def test_get_movies_by_filter_range_rating_return_success(
    api_request, api_client, five_test_ratings, min_rate, max_rate, result_count
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
    :param min_rate: The minimum rating to filter by.
    :param max_rate: The maximum rating to filter by.
    :param result_count: The expected number of results returned by the filter.
    :return: None
    """

    # Set different ratings for test movies
    ratings = [6.4, 7.3, 7.9, 8.2, 9.1]

    for index, obj in enumerate(five_test_ratings):
        obj.rating = ratings[index]
        obj.save()

    max_rating = max_rate
    min_rating = min_rate
    filter_params = {
        'max_rating': max_rating,
        'min_rating': min_rating
    }

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == result_count

    if not min_rate == '':
        for movie in response.data['results']:
            assert (
                Decimal(str(min_rating)) <= movie['rate'] <= Decimal(str(max_rating))
            )

    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data
