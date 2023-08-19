import pytest

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework import status


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


def test_post_rate_to_movie_should_success(
    test_movie_with_cast_crew_role_and_two_user_ratings, api_client,
    test_movie_without_cast_crew, third_test_user
) -> None:
    """
    Test that a user can successfully rate a movie through the API.

    This test ensures that an authorized user can post a valid rating for a movie.
    The user's authentication is forced using the 'api_client.force_authenticate()'
    method, and the 'api_client.post()' method is used to post the rating.
    and that the average rating is calculated correctly for the movie.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param test_movie_with_cast_crew_role_and_two_user_ratings: A fixture providing
    a test movie object with cast, crew, role, and two user ratings.
    :param test_movie_without_cast_crew: A fixture providing a test movie object
    without cast and crew.
    :param third_test_user: A fixture providing the third test user object.
    :return: None
    """

    # Authenticate the second test user for the API call
    api_client.force_authenticate(user=third_test_user)

    url = movie_detail_url(movie_slug=test_movie_without_cast_crew.slug)
    payload = {'rate': 7}

    response = api_client.post(path=url, data=payload)
    assert response.status_code == status.HTTP_201_CREATED

    # Assertion: Check that the new rating is successfully added to the movie
    first_test_movie_ratings_count = len(
        test_movie_without_cast_crew.movie_ratings.all()
    )
    assert first_test_movie_ratings_count == 3

    # Assertion: Check that the average rating is calculated correctly for the movie
    (first_test_rating,
     second_test_rating,
     third_test_rating) = test_movie_without_cast_crew.movie_ratings.all()

    first_test_movie_expected_rate = (
             first_test_rating.rating +
             second_test_rating.rating +
             third_test_rating.rating
                                     ) / 3
    assert response.data['rate'] == round(first_test_movie_expected_rate, 1)


def test_post_rate_to_movie_does_not_exists_should_error(
    api_client, first_test_user
) -> None:

    """
    Test rating a movie that does not exist.

    This test verifies that when the client attempts to rate a movie using a
    not existed movie slug, the API responds with an 'HTTP 404 Not Found' error.

    The test constructs a URL for the movie detail endpoint using a not existed movie
    slug and sends a POST request to this URL with a valid payload containing
    the rating data. The test expects the API to respond with an HTTP 404 status code
    indicating that the movie with the specified slug was not found.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_user: A fixture that creates the first test user
    in the database.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    not_exists_movie_slug = 'not-exists-movie-slug'

    url = movie_detail_url(movie_slug=not_exists_movie_slug)
    payload = {'rate': 7}

    response = api_client.post(path=url, data=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


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
    invalid case.

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


def test_post_rate_to_movie_that_not_released_yet_should_error(
    api_client, first_test_movie, first_test_user
) -> None:

    """
    Tests that posting a rating to a movie that has not been released yet
    returns an error.

    This test function creates a test movie with a release date in the future,
    authenticates a test user, and sends a POST request to the movie detail
    endpoint to rate the movie. It then asserts that the response status code
    is 403 Forbidden, indicating that the user is not allowed to rate the movie
    because it has not been released yet.

    :param api_client: The API client used to send requests to the API.
    :param first_test_movie: The test movie object.
    :param first_test_user: The test user object.
    :return: None
    """

    test_movie_release_date = timezone.now().date() + timedelta(days=1)

    first_test_movie.release_date = test_movie_release_date
    first_test_movie.save()

    api_client.force_authenticate(user=first_test_user)

    url = movie_detail_url(movie_slug=first_test_movie.slug)
    payload = {'rate': 8}
    print(first_test_movie.release_date)

    response = api_client.post(path=url, data=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN
