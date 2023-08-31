import pytest

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.movie.selectors import get_movie_list
from movie_recommendation_api.movie.serializers.movie_list_serializers import (
    MovieOutPutModelSerializer
)


pytestmark = pytest.mark.django_db

MOVIE_LIST_URL = reverse('api:movie:list')


@pytest.mark.parametrize(
    'release_date_filter', [
        'release_date_before',
        'release_date_after',
    ]
)
def test_get_movies_by_filter_wrong_release_date_return_error(
    api_client, five_test_movies, release_date_filter
) -> None:

    """
    Test that when an invalid release date is provided as a filter,
    the API returns an error.

    :param api_client: The API client used to make requests.
    :param five_test_movies: A list of five test movies.
    :param release_date_filter: The release date filter to use
    (either 'release_date_before' or 'release_date_after').
    :return: None
    """

    release_dates = [
        '2010-10-21', '2015-01-11', '2017-11-01', '2020-01-01', '2028-05-18'
    ]

    # Set the release dates for the test movies
    for index, obj in enumerate(five_test_movies):
        obj.release_date = release_dates[index]
        obj.save()

    release_date = 'wrong_date'
    filter_params = {release_date_filter: release_date}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    'date, result_count', [
        ('2018-01-01', 3),
        ('2008-01-01', 0),
        ('2028-01-01', 4),
        ('2030-01-01', 5),
        ('2020-01-01', 4),
        ('', 5),
    ]
)
def test_get_movies_by_filter_release_date_before_should_success(
    api_request, api_client, five_test_movies, date, result_count
) -> None:

    """
    Test that when a valid release date is provided as a filter,
    the API returns the correct number of results.

    :param api_request: The API request object.
    :param api_client: The API client used to make requests.
    :param five_test_movies: A list of five test movies.
    :param date: The release date to use as a filter.
    :param result_count: The expected number of results returned by the API.
    :return: None
    """

    release_dates = [
        '2010-10-21', '2015-01-11', '2017-11-01', '2020-01-01', '2028-05-18'
    ]

    # Set the release dates for the test movies
    for index, obj in enumerate(five_test_movies):
        obj.release_date = release_dates[index]
        obj.save()

    release_date_before = date
    filter_params = {'release_date_before': release_date_before}

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    # Ensure a successful response and correct number of results
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == result_count

    # If a date was provided, ensure that all returned movies have
    # a release date before the provided date
    if not date == '':
        for movie in response.data['results']:
            assert movie['release_date'] <= release_date_before

    # Ensure that the filtered movies match the expected results
    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data


@pytest.mark.parametrize(
    'date, result_count', [
        ('2018-01-01', 2),
        ('2008-01-01', 5),
        ('2028-01-01', 1),
        ('2030-01-01', 0),
        ('2020-01-01', 2),
        ('', 5),
    ]
)
def test_get_movies_by_filter_release_date_after_should_success(
    api_request, api_client, five_test_movies, date, result_count
) -> None:

    """
    Test that when a valid release date is provided as a filter,
    the API returns the correct number of results.

    :param api_request: The API request object.
    :param api_client: The API client used to make requests.
    :param five_test_movies: A list of five test movies.
    :param date: The release date to use as a filter.
    :param result_count: The expected number of results returned by the API.
    :return: None
    """

    release_dates = [
        '2010-10-21', '2015-01-11', '2017-11-01', '2020-01-01', '2028-05-18'
    ]

    # Set the release dates for the test movies
    for index, obj in enumerate(five_test_movies):
        obj.release_date = release_dates[index]
        obj.save()

    release_date_after = date
    filter_params = {'release_date_after': release_date_after}

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    # Ensure a successful response and correct number of results
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == result_count

    # Ensure that all returned movies have a release date after the provided date
    for movie in response.data['results']:
        assert movie['release_date'] >= release_date_after

    # Ensure that the filtered movies match the expected results
    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data


@pytest.mark.parametrize(
    'first_date, second_date, result_count', [
        ('2014-01-01', '2021-01-01', 3),
        ('2008-01-01', '2030-01-01', 5),
        ('2016-01-01', '2020-01-01', 2),
        ('2030-01-01', '2031-01-01', 0),
        ('2002-01-01', '2009-01-01', 0),
        ('', '', 5),
    ]
)
def test_get_movies_by_filter_release_date_range_should_success(
    api_request, api_client, five_test_movies, first_date, second_date, result_count
) -> None:

    """
    Test that when a valid range of release dates is provided as a filter,
    the API returns the correct number of results.

    :param api_request: The API request object.
    :param api_client: The API client used to make requests.
    :param five_test_movies: A list of five test movies.
    :param first_date: The first release date to use as a filter.
    :param second_date: The second release date to use as a filter.
    :param result_count: The expected number of results returned by the API.
    :return: None
    """

    release_dates = [
        '2010-10-21', '2015-01-11', '2017-11-01', '2020-01-01', '2028-05-18'
    ]

    # Set the release dates for the test movies
    for index, obj in enumerate(five_test_movies):
        obj.release_date = release_dates[index]
        obj.save()

    release_date_after = first_date
    release_date_before = second_date
    filter_params = {
        'release_date_after': release_date_after,
        'release_date_before': release_date_before,
    }

    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    # Ensure a successful response and correct number of results
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == result_count

    # If dates were provided, ensure that all returned movies have
    # a release date within the provided range
    if not first_date == '':
        for movie in response.data['results']:
            assert release_date_after <= movie['release_date'] <= release_date_before

    # Ensure that the filtered movies match the expected results
    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data
