import pytest

from django.urls import reverse

from rest_framework import status


pytestmark = pytest.mark.django_db

MOVIE_LIST_URL = reverse('api:movie:list')


@pytest.mark.parametrize(
    'cast_crew_filter, expected_movie_ids', [
        ('first_test_cast', {1, 2, 4}),
        ('third_test_crew', {3, 5}),
        ('second_test_cast, third_test_crew', {1, 3, 5}),
        ('first_test_crew, second_test_cast, third_test_crew', {1, 3, 5}),
        ('', {1, 2, 3, 4, 5}),
    ]
)
def test_get_movie_by_filter_cast_crew_return_success(
    api_client, five_test_movies, first_test_cast, first_test_crew,
    second_test_cast, second_test_crew, third_test_cast, third_test_crew,
    request, cast_crew_filter, expected_movie_ids
) -> None:

    """
    Test filtering movies by specific cast and crew members.

    This test suite checks the behavior of the movie filtering endpoint when
    filtering movies based on specific cast and crew members. It verifies that
    the endpoint correctly returns the expected movies based on the provided
    cast and crew filter.

    :param api_client: Django REST framework API client.
    :param five_test_movies: Fixtures for five test movies.
    :param first_test_cast: Fixture for the first cast member.
    :param first_test_crew: Fixture for the first crew member.
    :param second_test_cast: Fixture for the second cast member.
    :param second_test_crew: Fixture for the second crew member.
    :param third_test_cast: Fixture for the third cast member.
    :param third_test_crew: Fixture for the third crew member.
    :param request: Pytest request object for dynamic fixture retrieval.
    :param cast_crew_filter: Filter string for cast and crew members.
    :param expected_movie_ids: Set of expected movie IDs in the response.
    :return: None
    """

    test_cast_crew_filters = cast_crew_filter

    # If cast_crew_filter is provided, convert fixture names to cast_crew names
    if cast_crew_filter:
        filters = []
        split_test_cast_crew_names = cast_crew_filter.split(',')
        for cast_crew in split_test_cast_crew_names:
            # Get the cast_crew object from the fixture name and add its name
            # to the filter list
            get_test_cast_crew_fixture = request.getfixturevalue(cast_crew.strip())
            filters.append(get_test_cast_crew_fixture.name)

        # Combine the cast_crew names to form the final cast_crew filter string
        test_cast_crew_filters = ','.join(filters)

    first_test_movie, \
        second_test_movie, \
        third_test_movie, \
        forth_test_movie, \
        fifth_test_movie = five_test_movies

    first_test_movie.cast_crew.add(
        first_test_cast, second_test_cast, first_test_crew
    )

    second_test_movie.cast_crew.add(
        first_test_cast, third_test_cast, second_test_crew
    )

    third_test_movie.cast_crew.add(
        third_test_cast, third_test_crew
    )

    forth_test_movie.cast_crew.add(
        first_test_cast, second_test_crew
    )

    fifth_test_movie.cast_crew.add(
        first_test_crew, second_test_cast, third_test_crew
    )

    # Apply the partial filtering using the first three characters of the genre title
    filter_params = {'cast_crew': test_cast_crew_filters}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_200_OK

    response_movie_ids = {movie['id'] for movie in response.data['results']}
    assert response_movie_ids == expected_movie_ids


def test_get_movie_by_filter_partial_cast_crew_name_return_success(
    api_client, three_test_movies, first_test_crew, second_test_cast,
    second_test_crew, third_test_cast
) -> None:

    """
    Test filtering movies by partial cast and crew names.

    This test checks the behavior of the movie filtering endpoint when filtering
    movies based on partial cast and crew names. It verifies that the endpoint
    correctly returns the expected movies based on partial
    cast and crew name matching.

    :param api_client: Django REST framework API client.
    :param three_test_movies: Fixtures for three test movies.
    :param first_test_crew: Fixture for the first crew member.
    :param second_test_cast: Fixture for the second cast member.
    :param second_test_crew: Fixture for the second crew member.
    :param third_test_cast: Fixture for the third cast member.
    :return: None
    """

    first_test_movie, \
        second_test_movie, \
        third_test_movie = three_test_movies

    first_test_movie.cast_crew.add(first_test_crew, second_test_cast)
    second_test_movie.cast_crew.add(second_test_crew)
    third_test_movie.cast_crew.add(first_test_crew, third_test_cast)

    # Apply the partial filtering using the first
    # five characters of the cast_crew name
    partial_cast_crew_name = first_test_crew.name[:5]
    filter_params = {'cast_crew': partial_cast_crew_name}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_200_OK

    expected_movies = {first_test_movie.id, third_test_movie.id}
    response_movie_ids = {movie['id'] for movie in response.data['results']}

    assert response_movie_ids == expected_movies


def test_get_movie_by_filter_cast_crew_name_more_than_limit_should_return_error(
        api_client, first_test_movie, first_test_crew, first_test_cast,
        second_test_cast, second_test_crew, third_test_cast, third_test_crew
) -> None:

    """
    Test filtering movies by cast and crew names exceeding the maximum limit.

    This test case verifies that the movie filtering endpoint correctly handles
    filtering by cast and crew names when the number of cast and crew names
    in the filter exceeds the maximum allowed limit. It expects a 400 Bad Request
    response with an appropriate error message.

    :param api_client: Django REST framework API client.
    :param first_test_movie: Fixture for the first test movie.
    :param first_test_crew: Fixture for the first crew member.
    :param first_test_cast: Fixture for the first cast member.
    :param second_test_cast: Fixture for the second cast member.
    :param second_test_crew: Fixture for the second crew member.
    :param third_test_cast: Fixture for the third cast member.
    :param third_test_crew: Fixture for the third crew member.
    :return: None
    """

    # Apply genre title with more than the allowed limit
    more_than_limit_cast_crew_names = f'{first_test_crew.name}, ' \
                                      f'{first_test_cast.name}, ' \
                                      f'{second_test_cast.name}, ' \
                                      f'{second_test_crew.name}, ' \
                                      f'{third_test_cast.name}, ' \
                                      f'{third_test_crew.name}, '
    filter_params = {'cast_crew': more_than_limit_cast_crew_names}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check the error message in the response data
    expected_error_message = ["Filter Error - You cannot add more than 5 genres"]
    assert response.data["detail"] == expected_error_message
