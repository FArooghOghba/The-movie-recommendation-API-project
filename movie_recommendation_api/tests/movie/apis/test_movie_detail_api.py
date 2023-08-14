import pytest

from datetime import timedelta

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
    api_client, first_test_movie, first_test_user, second_test_user,
    first_test_rating, second_test_rating
) -> None:
    """
    Test that retrieving movie details for an authenticated user should succeed.

    This test ensures that an authenticated user can retrieve the details of a movie
    through the API. The user's authentication is forced using the
    'api_client.force_authenticate()' method, and the 'api_client.get()'
    method is used to perform the GET request for movie details.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :param first_test_user: A fixture providing the first test user object.
    :param second_test_user: A fixture providing the second test user object.
    :param first_test_rating: A fixture providing the first test rating object.
    :param second_test_rating: A fixture providing the second test rating object.
    :return: None
    """

    first_test_rating.user = first_test_user
    first_test_rating.movie = first_test_movie
    first_test_rating.save()

    second_test_rating.user = second_test_user
    second_test_rating.movie = first_test_movie
    second_test_rating.save()

    api_client.force_authenticate(user=first_test_user)

    url = movie_detail_url(movie_slug=first_test_movie.slug)

    response = api_client.get(path=url)
    assert response.status_code == status.HTTP_200_OK

    test_movie = get_movie_detail(movie_slug=first_test_movie.slug)
    expected_rating = test_movie.avg_rating
    assert response.data['rate'] == expected_rating

    expected_rating_count = len([first_test_rating, second_test_rating])
    assert response.data['ratings_count'] == expected_rating_count

    expected_logged_in_user_rating = first_test_rating.rating
    assert response.data['user_rating'] == expected_logged_in_user_rating


def test_get_movie_detail_with_cast_crew_role_should_return_success(
        api_client, second_test_movie, third_test_movie,
        test_movie_without_cast_crew, first_test_cast, first_test_crew
) -> None:

    """
    Test the detailed movie retrieval API endpoint with cast and crew roles.

    This test verifies that the detailed movie retrieval API endpoint returns
    accurate and consistent information about the movie's cast and crew roles.

    :param api_client: A DRF API client instance.
    :param test_movie_without_cast_crew (Movie): A test movie object
    without cast and crew roles.
    :param second_test_movie (Movie): Another test movie object created
    using fixtures.
    :param third_test_movie (Movie): Yet another test movie object created
    using fixtures.
    :param first_test_cast (CastCrew): A test cast member.
    :param first_test_crew (CastCrew): A test crew member.
    :return: None
    """

    a_test_movie = test_movie_without_cast_crew
    a_test_movie.cast_crew.add(first_test_cast, first_test_crew)
    a_test_movie.save()

    url = movie_detail_url(movie_slug=a_test_movie.slug)

    response = api_client.get(path=url)
    assert response.status_code == status.HTTP_200_OK

    test_movie = get_movie_detail(movie_slug=a_test_movie.slug)
    test_movie_output_serializer = MovieDetailOutPutModelSerializer(
        instance=test_movie,
        context={'user_rating': getattr(test_movie, 'user_rating', None)}
    )

    response_cast_crews = response.data['cast_crews']
    test_movie_cast_crews = test_movie_output_serializer.data['cast_crews']
    assert response_cast_crews == test_movie_cast_crews

    response_cast_len = len(response_cast_crews['casts'])
    assert response_cast_len == 1

    response_cast_name = response_cast_crews['casts'][0]['name']
    test_movie_cast_name = test_movie_cast_crews['casts'][0]['name']
    assert response_cast_name == test_movie_cast_name

    response_cast_role = response_cast_crews['casts'][0]['role']
    test_movie_cast_role = test_movie_cast_crews['casts'][0]['role']
    assert response_cast_role == test_movie_cast_role


def test_get_movie_detail_that_user_not_rated_should_success(
    api_client, first_test_movie, first_test_user
) -> None:
    """
    Test that a user can see the movie detail when they have not rated the movie yet.

    This test ensures that an authorized user can successfully retrieve
    the movie detail and if the user has not rated the movie,
    the 'user_rating' field in the response will show the message:
    'You have not rated this movie yet.'

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :param first_test_user: A fixture providing the first test user object.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    url = movie_detail_url(movie_slug=first_test_movie.slug)
    response = api_client.get(path=url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['user_rating'] == 'You have not rated this movie yet.'


def test_get_movie_detail_with_unauthenticated_user_should_success(
    api_client, first_test_movie
) -> None:
    """
    Test that retrieving movie details for an anonymous user should succeed.

    This test ensures that an anonymous user (unauthenticated user) can retrieve the
    details of a movie through the API. The user is not authenticated, and the
    'api_client.get()' method is used to perform the GET request for movie details.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :return: None
    """

    url = movie_detail_url(movie_slug=first_test_movie.slug)
    response = api_client.get(path=url)

    test_movie = get_movie_detail(movie_slug=first_test_movie.slug)
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


def test_get_movie_that_not_released_yet(
    api_client, first_test_movie, first_test_user
) -> None:
    """
    Tests that getting a movie that has not been released yet returns
    the expected response.

    This test function creates a test movie with a release date in the future,
    authenticates a test user, and sends a GET request to the movie detail
    endpoint to retrieve the movie detail. It then asserts that the response
    status code is 200 OK, and that the `user_rating` field in the response data
    is set to "Movie has not been released yet."

    :param api_client: The API client used to send requests to the API.
    :param first_test_movie: The test movie object.
    :param first_test_user: The test user object.
    """

    test_movie_release_date = timezone.now().date() + timedelta(days=1)

    first_test_movie.release_date = test_movie_release_date
    first_test_movie.save()

    api_client.force_authenticate(user=first_test_user)

    url = movie_detail_url(movie_slug=first_test_movie.slug)
    response = api_client.get(path=url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['user_rating'] == 'Movie has not been released yet.'


def test_post_rate_to_movie_should_success(
    api_client, first_test_movie, first_test_rating,
    first_test_user, second_test_user
) -> None:
    """
    Test that a user can successfully rate a movie through the API.

    This test ensures that an authorized user can post a valid rating for a movie.
    The user's authentication is forced using the 'api_client.force_authenticate()'
    method, and the 'api_client.post()' method is used to post the rating.
    and that the average rating is calculated correctly for the movie.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :param first_test_rating: A fixture providing the first test rating object.
    :param second_test_user: A fixture providing the second test user object.
    :param first_test_user: A fixture providing the first test user object.
    :return: None
    """

    # Set up: Assign the first test rating to the first test movie
    first_test_rating.user = first_test_user
    first_test_rating.movie = first_test_movie
    first_test_rating.save()

    # Authenticate the second test user for the API call
    api_client.force_authenticate(user=second_test_user)

    url = movie_detail_url(movie_slug=first_test_movie.slug)
    payload = {'rate': 7}

    response = api_client.post(path=url, data=payload)
    assert response.status_code == status.HTTP_201_CREATED

    # Assertion: Check that the new rating is successfully added to the movie
    first_test_movie_ratings_count = len(first_test_movie.movie_ratings.all())
    assert first_test_movie_ratings_count == 2

    # Assertion: Check that the average rating is calculated correctly for the movie
    first_test_rating, second_test_rating = first_test_movie.movie_ratings.all()
    first_test_movie_expected_rate = (
             first_test_rating.rating + second_test_rating.rating
                                     ) / 2
    assert response.data['rate'] == first_test_movie_expected_rate


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
