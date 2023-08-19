from datetime import timedelta

import pytest

from django.urls import reverse
from django.utils import timezone

from rest_framework import status

from movie_recommendation_api.movie.selectors import get_movie_detail
from movie_recommendation_api.movie.serializers import (
    MovieDetailOutPutModelSerializer
)


pytestmark = pytest.mark.django_db


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


def test_get_movie_detail_should_success(
    test_movie_with_cast_crew_role_and_two_user_ratings, api_client, first_test_user,
    test_movie_without_cast_crew, first_test_rating, second_test_rating
) -> None:
    """
    Test that retrieving movie details for an authenticated user should succeed.

    This test ensures that an authenticated user can retrieve the details of a movie
    through the API. The user's authentication is forced using the
    'api_client.force_authenticate()' method, and the 'api_client.get()'
    method is used to perform the GET request for movie details.

    :param test_movie_with_cast_crew_role_and_two_user_ratings: A fixture providing
    a test movie object with cast, crew, role, and two user ratings.
    :param api_client: An instance of the Django REST Framework's APIClient.
    :param test_movie_without_cast_crew: A fixture providing a test
    movie object without cast and crew.
    :param first_test_user: A fixture providing the first test user object.
    :param first_test_rating: A fixture providing the first test rating object.
    :param second_test_rating: A fixture providing the second test rating object.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    url = movie_detail_url(movie_slug=test_movie_without_cast_crew.slug)

    response = api_client.get(path=url)
    assert response.status_code == status.HTTP_200_OK

    # Assertion: Check that the average rating is calculated correctly for the movie
    test_movie = get_movie_detail(movie_slug=test_movie_without_cast_crew.slug)
    expected_rating = test_movie.avg_rating
    assert response.data['rate'] == expected_rating

    # Assertion: Check that the number of ratings is calculated correctly
    # for the movie
    expected_rating_count = len([first_test_rating, second_test_rating])
    assert response.data['ratings_count'] == expected_rating_count

    # Assertion: Check that the logged-in user's rating is returned correctly
    expected_logged_in_user_rating = first_test_rating.rating
    assert response.data['user_rating'] == expected_logged_in_user_rating


def test_get_movie_detail_with_cast_crew_role_should_return_success(
        api_client, test_movie_with_cast_crew_role_and_two_user_ratings,
        test_movie_without_cast_crew
) -> None:

    """
    Test the detailed movie retrieval API endpoint with cast and crew roles.

    This test verifies that the detailed movie retrieval API endpoint returns
    accurate and consistent information about the movie's cast and crew roles.

    :param api_client: A DRF API client instance.
    :param test_movie_with_cast_crew_role_and_two_user_ratings: A fixture providing
    a test movie object with cast, crew, role, and two user ratings.
    :param test_movie_without_cast_crew: A fixture providing a test movie object
    without cast and crew roles.
    :return: None
    """

    url = movie_detail_url(movie_slug=test_movie_without_cast_crew.slug)

    response = api_client.get(path=url)
    assert response.status_code == status.HTTP_200_OK

    # Assertion: Check that the cast and crew information is returned correctly
    test_movie = get_movie_detail(movie_slug=test_movie_without_cast_crew.slug)
    test_movie_output_serializer = MovieDetailOutPutModelSerializer(
        instance=test_movie,
        context={'user_rating': getattr(test_movie, 'user_rating', None)}
    )

    response_cast_crews = response.data['cast_crews']
    test_movie_cast_crews = test_movie_output_serializer.data['cast_crews']
    assert response_cast_crews == test_movie_cast_crews

    # Assertion: Check that the cast information is returned correctly
    response_cast_len = len(response_cast_crews['casts'])
    assert response_cast_len == 1

    response_cast_name = response_cast_crews['casts'][0]['name']
    test_movie_cast_name = test_movie_cast_crews['casts'][0]['name']
    assert response_cast_name == test_movie_cast_name

    response_cast_role = response_cast_crews['casts'][0]['role']
    test_movie_cast_role = test_movie_cast_crews['casts'][0]['role']
    assert response_cast_role == test_movie_cast_role

    # Assertion: Check that the crew information is returned correctly
    response_crew_len = len(response_cast_crews['crews'])
    assert response_crew_len == 1

    response_crew_name = response_cast_crews['crews'][0]['name']
    test_movie_crew_name = test_movie_cast_crews['crews'][0]['name']
    assert response_crew_name == test_movie_crew_name

    response_crew_role = response_cast_crews['crews'][0]['role']
    test_movie_crew_role = test_movie_cast_crews['crews'][0]['role']
    assert response_crew_role == test_movie_crew_role


def test_get_movie_detail_that_user_not_rated_should_success(
    test_movie_with_cast_crew_role, api_client, test_movie_without_cast_crew,
    first_test_user
) -> None:
    """
    Test that a user can see the movie detail when they have not rated the movie yet.

    This test ensures that an authorized user can successfully retrieve
    the movie detail and if the user has not rated the movie,
    the 'user_rating' field in the response will show the message:
    'You have not rated this movie yet.'

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param test_movie_with_cast_crew_role: A fixture providing a test movie
    object with cast, crew, and role.
    :param test_movie_without_cast_crew: A fixture providing a test movie
    object without cast and crew roles.
    :param first_test_user: A fixture providing the first test user object.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    url = movie_detail_url(movie_slug=test_movie_without_cast_crew.slug)
    response = api_client.get(path=url)

    # Assertion: Check that the response is successful and
    # contains the expected message
    assert response.status_code == status.HTTP_200_OK
    assert response.data['user_rating'] == 'You have not rated this movie yet.'


def test_get_movie_detail_with_unauthenticated_user_should_success(
    test_movie_with_cast_crew_role, api_client, test_movie_without_cast_crew,
) -> None:
    """
    Test that retrieving movie details for an anonymous user should succeed.

    This test ensures that an anonymous user (unauthenticated user) can retrieve the
    details of a movie through the API. The user is not authenticated, and the
    'api_client.get()' method is used to perform the GET request for movie details.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param test_movie_with_cast_crew_role: A fixture providing a test movie object
    with cast, crew, and role.
    :param test_movie_without_cast_crew: A fixture providing a test movie object
    without cast and crew roles.
    :return: None
    """

    url = movie_detail_url(movie_slug=test_movie_without_cast_crew.slug)
    response = api_client.get(path=url)

    # Assertion: Check that the response is successful and contains the expected data
    test_movie = get_movie_detail(movie_slug=test_movie_without_cast_crew.slug)
    test_movie_output_serializer = MovieDetailOutPutModelSerializer(
            instance=test_movie,
            context={'user_rating': getattr(test_movie, 'user_rating', None)}
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == test_movie_output_serializer.data
    assert response.data['ratings_count'] == 0
    assert response.data['user_rating'] == 'Please login to rate this movie.'


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


def test_get_movie_detail_that_not_released_yet(
    test_movie_with_cast_crew_role, api_client, test_movie_without_cast_crew,
    first_test_user,
) -> None:
    """
    Tests that getting a movie that has not been released yet return
    the expected response.

    This test function creates a test movie with a release date in the future,
    authenticates a test user, and sends a GET request to the movie detail
    endpoint to retrieve the movie detail. It then asserts that the response
    status code is 200 OK, and that the `user_rating` field in the response data
    is set to "Movie has not been released yet."

    :param api_client: The API client used to send requests to the API.
    :param test_movie_with_cast_crew_role: A fixture providing a test
    movie object with cast, crew, and role.
    :param test_movie_without_cast_crew: A fixture providing a test movie
    object without cast and crew roles.
    :param first_test_user: The test user object.
    :return: None
    """

    # Set the release date of the test movie to a future date
    test_movie_release_date = timezone.now().date() + timedelta(days=1)

    test_movie_without_cast_crew.release_date = test_movie_release_date
    test_movie_without_cast_crew.save()

    api_client.force_authenticate(user=first_test_user)

    url = movie_detail_url(movie_slug=test_movie_without_cast_crew.slug)
    response = api_client.get(path=url)

    # Assertion: Check that the response is successful and
    # contains the expected message
    assert response.status_code == status.HTTP_200_OK
    assert response.data['user_rating'] == 'Movie has not been released yet.'
