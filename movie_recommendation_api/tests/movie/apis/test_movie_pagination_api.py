import pytest

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.movie.selectors import get_movie_list
from movie_recommendation_api.movie.serializers import MovieOutPutModelSerializer


pytestmark = pytest.mark.django_db

MOVIE_LIST_URL = reverse('api:movie:list')


@pytest.mark.parametrize('limit, offset, expected_count', [
    (2, 0, 2),  # First page with limit 2 and offset 0 should return 2 movies.
    (2, 2, 2),  # Second page with limit 2 and offset 2 should return 2 movies.
    (3, 2, 3),  # Second page with limit 3 and offset 2 should return 3 movie
    (10, 0, 5),  # Requesting all movies with limit 10 should return all 5 movies.
])
def test_get_movie_list_for_checking_pagination(
        api_client, api_request, five_test_movies,
        limit, offset, expected_count
) -> None:
    """
    Test the pagination feature of the movie list endpoint.

    This test case verifies that the movie list endpoint returns the expected
    number of movies based on the provided limit and offset parameters.

    Raises:
        AssertionError: If the test fails.

    :param api_client: (APIClient): An instance of the Django REST Framework's
    APIClient.
    :param api_request: (RequestFactory): An instance of Django's RequestFactory
    for creating test requests.
    :param five_test_movies: (pytest fixture): A fixture that creates five
    test movies in the database.
    :param limit: (int): The maximum number of movies to be returned per page.
    :param offset: (int): The starting position for fetching movies
    in the result set.
    :param expected_count: (int): The expected number of movies to be
    returned in the response.
    :return: None
    """

    request = api_request.get(path=MOVIE_LIST_URL)
    query_params = {'limit': limit, 'offset': offset}
    response = api_client.get(
        path=MOVIE_LIST_URL, request=request, data=query_params
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == expected_count

    # Get the queryset for all movies, prefetching related genres,
    # and deferring unnecessary fields.
    # Annotate the queryset with average ratings and order it by 'release_date'
    test_movies_queryset = get_movie_list().order_by('release_date')

    test_movies_output_serializer = MovieOutPutModelSerializer(
        test_movies_queryset, many=True, context={'request': request}
    )

    # Get the subset of movies based on the limit and offset from the serialized data
    expected_movies = test_movies_output_serializer.data[offset:offset + limit]
    assert response.data['results'] == expected_movies


@pytest.mark.parametrize('limit, offset, test_next_page, test_previous_page', [

    # First page with limit 2 and offset 0, should have next page.
    (2, 0, True, False),

    # Second page with limit 2 and offset 2, should have both next
    # and previous pages.
    (2, 2, True, True),

    # Second page with limit 3 and offset 2, should have previous page.
    (3, 2, False, True),

    # Requesting all movies with limit 10, should not have next or previous page.
    (10, 0, False, False),
])
def test_get_movie_list_pagination_next_previous_pages(
        api_client, api_request, five_test_movies,
        limit, offset, test_next_page, test_previous_page
) -> None:
    """
    Test the next and previous pages functionality of the movie list endpoint.

    This test case verifies that the movie list endpoint correctly indicates
    the availability of next and previous pages based on the provided limit
    and offset parameters.

    Raises:
        AssertionError: If the test assertions fail.

    :param api_client: (APIClient): An instance of the Django REST Framework's
    APIClient.
    :param api_request: (RequestFactory): An instance of Django's RequestFactory
    for creating test requests.
    :param five_test_movies: (pytest fixture): A fixture that creates five
    test movies in the database.
    :param limit: (int): The maximum number of movies to be returned per page.
    :param offset: (int): The starting position for fetching movies in
    the result set.
    :param test_next_page: (bool): Indicates whether the expected response
    should have a next page.
    :param test_previous_page: (bool): Indicates whether the expected response
    should have a previous page.
    :return: None
    """

    request = api_request.get(path=MOVIE_LIST_URL)
    query_params = {'limit': limit, 'offset': offset}
    response = api_client.get(
        path=MOVIE_LIST_URL, request=request, data=query_params
    )
    assert response.status_code == status.HTTP_200_OK

    # Assert the presence of next and previous keys in the response
    has_next_page = True if response.data['next'] is not None else False
    has_previous_page = True if response.data['previous'] is not None else False
    assert has_next_page is test_next_page
    assert has_previous_page is test_previous_page


@pytest.mark.parametrize('limit, offset, test_next_page, test_previous_page', [
    # First page with limit 2 and offset 0, should have next page.
    (2, 0, True, False),

    # Second page with limit 2 and offset 2, should have both next and
    # previous pages.
    (2, 2, True, True),

    # Second page with limit 3 and offset 2, should have previous page.
    (3, 2, False, True),

    # Requesting all movies with limit 10, should not have next or previous page.
    (10, 0, False, False),
])
def test_get_movie_list_pagination_next_previous_pages_request(
        api_client, api_request, five_test_movies,
        limit, offset, test_next_page, test_previous_page
) -> None:

    """
    Test the next and previous pages functionality of the movie list endpoint.

    This test case verifies that the movie list endpoint correctly indicates
    the availability of next and previous pages based on the provided limit
    and offset parameters.

    :param api_client: (APIClient): An instance of the Django REST Framework's
        APIClient.
    :param api_request: (RequestFactory): An instance of Django's RequestFactory
        for creating test requests.
    :param five_test_movies: (pytest fixture): A fixture that creates five
        test movies in the database.
    :param limit: (int): The maximum number of movies to be returned per page.
    :param offset: (int): The starting position for fetching movies in
        the result set.
    :param test_next_page: (bool): Indicates whether the expected response
        should have a next page.
    :param test_previous_page: (bool): Indicates whether the expected response
        should have a previous page.
    :return: None
    """

    # Create a request for the movie list endpoint with the given limit and offset
    request = api_request.get(path=MOVIE_LIST_URL)
    query_params = {'limit': limit, 'offset': offset}
    response = api_client.get(
        path=MOVIE_LIST_URL, request=request, data=query_params
    )

    assert response.status_code == status.HTTP_200_OK

    # Get the queryset for all movies, prefetching related genres,
    # and deferring unnecessary fields.
    # Annotate the queryset with average ratings and order it by 'id'
    test_movies_queryset = get_movie_list()

    # If there is a next page, assert the next page URL
    if test_next_page:
        next_page_url = response.data['next']
        expected_next_url = f"http://testserver{MOVIE_LIST_URL}?" \
                            f"limit={limit}&offset={offset + limit}"
        assert next_page_url == expected_next_url

        next_page_response = api_client.get(path=next_page_url, request=request)
        assert next_page_response.status_code == status.HTTP_200_OK

        # Calculate the expected offset and limit for the next page results
        next_page_offset = next_page_response.data['offset']
        next_page_limit = next_page_response.data['limit']

        test_movies_output_serializer = MovieOutPutModelSerializer(
            test_movies_queryset, many=True, context={'request': request}
        )

        # Get the expected results for the next page based on offset and limit
        next_page_results_count = len(
            test_movies_output_serializer.data[
                next_page_offset: next_page_offset + next_page_limit
            ]
        )

        assert len(
            next_page_response.data['results']
        ) == next_page_results_count

    # If there is a previous page, assert the previous page URL
    if test_previous_page:
        previous_page_url = response.data['previous']
        expected_previous_url = f"http://testserver{MOVIE_LIST_URL}?limit={limit}"

        offset_expected_previous_url = max(0, offset - limit)
        if offset_expected_previous_url > 0:
            expected_previous_url += f'&offset={offset_expected_previous_url}'

        assert previous_page_url == expected_previous_url

        previous_page_response = api_client.get(
            path=previous_page_url, request=request
        )
        assert previous_page_response.status_code == status.HTTP_200_OK

        # Calculate the expected offset and limit for the previous page results
        previous_page_offset = previous_page_response.data['offset']
        previous_page_limit = previous_page_response.data['limit']

        test_movies_output_serializer = MovieOutPutModelSerializer(
            test_movies_queryset, many=True, context={'request': request}
        )

        # Get the expected results for the previous page based on offset and limit
        previous_page_results_count = len(
            test_movies_output_serializer.data[
                previous_page_offset: previous_page_offset + previous_page_limit
            ]
        )

        assert len(
            previous_page_response.data['results']
        ) == previous_page_results_count
