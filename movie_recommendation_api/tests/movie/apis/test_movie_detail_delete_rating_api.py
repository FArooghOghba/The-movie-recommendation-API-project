import pytest

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.users.models import Profile


pytestmark = pytest.mark.django_db


def movie_detail_url(movie_slug: str) -> str:
    """
    Generate the URL for the movie detail API endpoint based on the movie slug.

    This function takes a movie slug as input and generates the URL for the
    movie detail API endpoint by using the `reverse` function provided by Django's
    URL resolver. The movie slug is included as a parameter in the URL.

    :param movie_slug: The slug of the movie.
    :return: The URL for the movie 'detail API' endpoint.
    """
    return reverse(viewname='api:movie:detail', args=[movie_slug])


def movie_rating_url(movie_slug: str) -> str:
    """
    Generate the URL for the movie rating API endpoint based on the movie slug.

    This function takes a movie slug as input and generates the URL for the
    movie rating API endpoint by using the `reverse` function provided by Django's
    URL resolver. The movie slug is included as a parameter in the URL.

    :param movie_slug: The slug of the movie.
    :return: The URL for the movie 'rating API' endpoint.
    """
    return reverse(viewname='api:movie:rating', args=[movie_slug])


def test_delete_rate_from_movie_should_success(
    api_client, first_test_user, second_test_user, third_test_user,
    first_test_movie, first_test_rating, second_test_rating, third_test_rating
) -> None:

    """
    Test that a user can successfully delete rating for a movie through the API.

    This test ensures that an authorized user can delete a rating for a movie.
    The user's authentication is forced using the 'api_client.force_authenticate()'
    method, and the 'api_client.delete()' method is used to delete the rating.
    And that the average rating is calculated correctly for the movie.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing a test movie object.
    :param first_test_user: A fixture providing the first test user object.
    :param second_test_user: A fixture providing the second test user object.
    :param first_test_rating: A fixture providing the first test rating object.
    :param second_test_rating: A fixture providing the second test rating object.
    :return: None
    """

    # Set up initial ratings for the movie by different users.
    first_test_rating.user = first_test_user
    first_test_rating.movie = first_test_movie
    first_test_rating.save()

    second_test_rating.user = second_test_user
    second_test_rating.movie = first_test_movie
    second_test_rating.save()

    third_test_rating.user = third_test_user
    third_test_rating.movie = first_test_movie
    third_test_rating.save()

    # Fetch the movie's details to get its rate before the deleting.
    get_movie_detail_url = movie_detail_url(movie_slug=first_test_movie.slug)
    get_movie_detail_response = api_client.get(path=get_movie_detail_url)
    assert get_movie_detail_response.status_code == status.HTTP_200_OK

    first_test_movie_rate_before_delete = get_movie_detail_response.data['rate']

    # Authenticate the second test user for the API call.
    api_client.force_authenticate(user=first_test_user)

    # Delete the movie rating with movie slug.
    delete_movie_rating_url = movie_rating_url(movie_slug=first_test_movie.slug)
    delete_rating_movie_response = api_client.delete(
        path=delete_movie_rating_url
    )
    assert delete_rating_movie_response.status_code == status.HTTP_204_NO_CONTENT

    first_test_movie_rate_after_delete = delete_rating_movie_response.data['rate']

    # Assertion: Check that the new rating is successfully deleted from the movie.
    first_test_movie_ratings_count = len(
        first_test_movie.movie_ratings.all()
    )
    assert first_test_movie_ratings_count == 2

    # Assertion: Check that the average rating is calculated correctly for the movie.
    first_test_movie_ratings = list(first_test_movie.movie_ratings.all())

    first_test_movie_expected_rate = (
             first_test_movie_ratings[0].rating +
             first_test_movie_ratings[1].rating
                                     ) / 2

    assert first_test_movie_rate_after_delete == round(
        first_test_movie_expected_rate, 1
    )

    assert first_test_movie_rate_after_delete != first_test_movie_rate_before_delete


def test_delete_rate_from_movie_and_user_profile_should_success(
        api_client, first_test_user, second_test_user,
        first_test_movie, first_test_rating, second_test_rating
) -> None:

    """
    Test that a user can successfully delete their movie rating
    and that their profile gets updated accordingly.

    This test covers the scenario where a user has already rated
    a movie and then deletes their rating, and also checks that
    their profile is updated with no rating.

    :param api_client: Django test client.
    :param first_test_user: First test user object.
    :param second_test_user: Second test user object.
    :param first_test_movie: First test movie object.
    :param first_test_rating: First test rating object.
    :param second_test_rating: Second test rating object.
    :return: None
    """

    # Set up initial ratings for the movie by different users.
    first_test_rating.user = first_test_user
    first_test_rating.movie = first_test_movie
    first_test_rating.save()

    first_test_user_profile = first_test_user.profile
    first_test_user_profile.ratings.add(first_test_rating)

    second_test_rating.user = second_test_user
    second_test_rating.movie = first_test_movie
    second_test_rating.save()

    # Fetch the movie's details to get its rate before the deleting.
    get_movie_detail_url = movie_detail_url(movie_slug=first_test_movie.slug)
    get_movie_detail_response = api_client.get(path=get_movie_detail_url)
    assert get_movie_detail_response.status_code == status.HTTP_200_OK

    # Authenticate the second test user for the API call.
    api_client.force_authenticate(user=first_test_user)

    # Delete the movie rating with the movie slug.
    delete_movie_rating_url = movie_rating_url(movie_slug=first_test_movie.slug)
    delete_rating_movie_response = api_client.delete(
        path=delete_movie_rating_url
    )
    assert delete_rating_movie_response.status_code == status.HTTP_204_NO_CONTENT

    # Get the user's profile after the update.
    first_test_user_profile_after_delete = (
        Profile.objects.get(user=first_test_user)

    )

    first_test_user_ratings_after_delete = list(
        first_test_user_profile_after_delete.ratings.all()
    )

    # Assertion: Check that the user's profile rating gets deleted correctly.
    assert first_test_user_ratings_after_delete == []


def test_delete_rate_from_movie_does_not_exists_should_error(
    api_client, first_test_user
) -> None:

    """
    Test delete rating for a movie that does not exist.

    This test verifies that when the client attempts to delete rating
    for a movie using a not existed movie slug, the API responds with
    an 'HTTP 404 Not Found' error.

    The test constructs a URL for the movie rating endpoint using a not existed movie
    slug and sends a DELETE request to this URL. The test expects the API to respond
    with an HTTP 404 status code indicating that the movie with the specified
    slug was not found.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_user: A fixture that creates the first test user
    in the database.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    not_exists_movie_slug = 'not-exists-movie-slug'

    url = movie_rating_url(movie_slug=not_exists_movie_slug)

    response = api_client.delete(path=url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_rate_from_movie_with_unauthorized_user_should_error(
    api_client, first_test_movie
) -> None:

    """
    Test that an unauthorized user cannot delete a rating from a movie
    and receives an error.

    This test verifies that an unauthenticated user receives
    a 401 Unauthorized status when trying to delete a rating from a movie.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :return: None
    """

    url = movie_rating_url(movie_slug=first_test_movie.slug)

    response = api_client.delete(path=url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
