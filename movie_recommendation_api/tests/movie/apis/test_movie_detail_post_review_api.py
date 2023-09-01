import pytest

from django.urls import reverse

from rest_framework import status


pytestmark = pytest.mark.django_db


def movie_review_url(movie_slug: str) -> str:

    """
    Generate the URL for the movie review API endpoint based on the movie slug.

    This function takes a movie slug as input and generates the URL for the
    movie review API endpoint by using the `reverse` function provided by Django's
    URL resolver. The movie slug is included as a parameter in the URL.

    :param movie_slug: The slug of the movie.
    :return: The URL for the movie 'review API' endpoint.
    """

    return reverse(viewname='api:movie:review', args=[movie_slug])


def test_post_review_to_movie_should_success(
    test_movie_with_cast_crew_role_and_two_user_ratings_and_reviews, api_client,
    test_movie_without_cast_crew, third_test_user
) -> None:

    """
    Test that a user can successfully review a movie through the API.

    This test ensures that an authorized user can post a valid review for a movie.
    The user's authentication is forced using the 'api_client.force_authenticate()'
    method, and the 'api_client.post()' method is used to post the review.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param test_movie_with_cast_crew_role_and_two_user_ratings_and_reviews: A fixture
    providing a test movie object with cast, crew, role, and two user ratings
    and review.
    :param test_movie_without_cast_crew: A fixture providing a test movie object
    without cast and crew.
    :param third_test_user: A fixture providing the third test user object.
    :return: None
    """

    # Authenticate the second test user for the API call
    api_client.force_authenticate(user=third_test_user)

    url = movie_review_url(movie_slug=test_movie_without_cast_crew.slug)
    payload = {'review': 'This is Third Test user review.'}

    response = api_client.post(path=url, data=payload)
    assert response.status_code == status.HTTP_201_CREATED

    # Assertion: Check that the new review is successfully added to the movie
    first_test_movie_reviews_count = len(
        test_movie_without_cast_crew.reviews.all()
    )
    assert first_test_movie_reviews_count == 3


def test_post_review_to_movie_does_not_exists_should_error(
    api_client, first_test_user
) -> None:

    """
    Test review a movie that does not exist.

    This test verifies that when the client attempts to review a movie using a
    not existed movie slug, the API responds with an 'HTTP 404 Not Found' error.

    The test constructs a URL for the movie review endpoint using a not existed movie
    slug and sends a POST request to this URL with a valid payload containing
    the review data. The test expects the API to respond with an HTTP 404 status code
    indicating that the movie with the specified slug was not found.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_user: A fixture that creates the first test user
    in the database.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    not_exists_movie_slug = 'not-exists-movie-slug'

    url = movie_review_url(movie_slug=not_exists_movie_slug)
    payload = {'review': 'This is the Test user review.'}

    response = api_client.post(path=url, data=payload)
    print(response.data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_post_review_to_movie_with_unauthorized_user_should_error(
    api_client, first_test_movie
) -> None:

    """
    Test that an unauthorized user cannot review a movie and receives an error.

    This test verifies that an unauthenticated user receives
    a 401 Unauthorized status when trying to post a review for a movie.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :return: None
    """

    url = movie_review_url(movie_slug=first_test_movie.slug)
    payload = {'review': 'This is the Test user review.'}

    response = api_client.post(path=url, data=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    'wrong_review', (
        '',
        ' ',
        '    '
    )
)
def test_post_review_to_movie_with_wrong_data_should_error(
    api_client, first_test_movie, first_test_user, wrong_review
) -> None:

    """
     Test that posting a review with wrong data returns a 400 Bad Request error.

    This parameterized test checks various cases where the provided review data
    is invalid, such as wrong review format, empty string or white-space.

    The test ensures that the API returns a 400 Bad Request status for each
    invalid case.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :param first_test_user: A fixture providing the first test user object.
    :param wrong_review: A parameter representing invalid review values.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    url = movie_review_url(movie_slug=first_test_movie.slug)
    payload = {'review': wrong_review}

    response = api_client.post(path=url, data=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
