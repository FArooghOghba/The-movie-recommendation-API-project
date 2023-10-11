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


def movie_delete_review_url(movie_slug: str, review_slug: str) -> str:

    """
    Generate the URL for the movie delete review API endpoint based on the movie slug
    and review slug.

    This function takes a movie slug and a review slug as input and generates
    the URL for the movie delete review API endpoint by using the `reverse` function
    provided by Django's URL resolver. The movie and review slugs are included
    as a parameter in the URL.

    :param movie_slug: The slug of the movie.
    :param review_slug: The slug of the review.
    :return: The URL for the movie delete 'review API' endpoint.
    """

    get_movie_delete_review_url = reverse(
        viewname='api:movie:delete-review', args=[movie_slug, review_slug]
    )

    return get_movie_delete_review_url


def test_delete_review_from_movie_should_success(
    api_client, first_test_user, second_test_user,
    first_test_movie, first_test_review, second_test_review
) -> None:

    """
    Test that a user can successfully delete review for a movie through the API.

    This test ensures that an authorized user can delete a review for a movie.
    The user's authentication is forced using the 'api_client.force_authenticate()'
    method, and the 'api_client.delete()' method is used to delete the review.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing a test movie object.
    :param first_test_user: A fixture providing the first test user object.
    :param second_test_user: A fixture providing the second test user object.
    :param first_test_review: A fixture providing the first test review object.
    :param second_test_review: A fixture providing the second test review object.
    :return: None
    """

    # Set up initial reviews for the movie by different users.
    first_test_review.user = first_test_user
    first_test_review.movie = first_test_movie
    first_test_review.save()

    second_test_review.user = second_test_user
    second_test_review.movie = first_test_movie
    second_test_review.save()

    # Fetch the movie's details to get its review before delete.
    get_movie_detail_url = movie_detail_url(movie_slug=first_test_movie.slug)
    get_movie_detail_response = api_client.get(path=get_movie_detail_url)
    assert get_movie_detail_response.status_code == status.HTTP_200_OK

    first_test_movie_reviews_before_delete = get_movie_detail_response.data[
        'reviews'
    ]

    first_test_movie_reviews_title_before_delete = [
        review['title'] for review in first_test_movie_reviews_before_delete
    ]

    # Authenticate the second test user for the API call.
    api_client.force_authenticate(user=first_test_user)

    # Delete the movie review with review slug for a specific movie.
    delete_movie_review_url = movie_delete_review_url(
        movie_slug=first_test_movie.slug,
        review_slug=first_test_review.slug
    )
    delete_movie_review_response = api_client.delete(
        path=delete_movie_review_url,
    )
    assert delete_movie_review_response.status_code == status.HTTP_204_NO_CONTENT

    # Assertion: Check that the new review is successfully deleted from the movie.
    first_test_movie_reviews_count = len(
        first_test_movie.reviews.all()
    )
    assert first_test_movie_reviews_count == 1

    first_test_movie_reviews_after_delete = delete_movie_review_response.data[
        'reviews'
    ]

    first_test_movie_reviews_title_after_delete = [
        review['title'] for review in first_test_movie_reviews_after_delete
    ]

    assert first_test_review.title in first_test_movie_reviews_title_before_delete
    assert first_test_review.title not in first_test_movie_reviews_title_after_delete


def test_delete_review_from_movie_and_user_profile_should_success(
        api_client, first_test_user, second_test_user,
        first_test_movie, first_test_review, second_test_review
) -> None:

    """
    Test that a user can successfully delete their movie review
    and that their profile gets updated accordingly.

    This test covers the scenario where a user has already reviewed
    a movie and then deletes their review, and also checks that
    their profile is updated with no review.

    :param api_client: Django test client.
    :param first_test_user: First test user object.
    :param second_test_user: Second test user object.
    :param first_test_movie: First test movie object.
    :param first_test_review: First test review object.
    :param second_test_review: Second test review object.
    :return: None
    """

    # Set up initial ratings for the movie by different users.
    first_test_review.user = first_test_user
    first_test_review.movie = first_test_movie
    first_test_review.save()

    first_test_user_profile = first_test_user.profile
    first_test_user_profile.reviews.add(first_test_review)

    second_test_review.user = second_test_user
    second_test_review.movie = first_test_movie
    second_test_review.save()

    # Fetch the movie's details to get its reviews before the deleting.
    get_movie_detail_url = movie_detail_url(movie_slug=first_test_movie.slug)
    get_movie_detail_response = api_client.get(path=get_movie_detail_url)
    assert get_movie_detail_response.status_code == status.HTTP_200_OK

    # Authenticate the second test user for the API call.
    api_client.force_authenticate(user=first_test_user)

    # Delete the movie review with the movie slug.
    delete_movie_review_url = movie_delete_review_url(
        movie_slug=first_test_movie.slug,
        review_slug=first_test_review.slug
    )
    delete_review_movie_response = api_client.delete(
        path=delete_movie_review_url
    )
    assert delete_review_movie_response.status_code == status.HTTP_204_NO_CONTENT

    # Get the user's profile after the update.
    first_test_user_profile_after_delete = (
        Profile.objects.get(user=first_test_user)

    )

    first_test_user_ratings_after_delete = list(
        first_test_user_profile_after_delete.ratings.all()
    )

    # Assertion: Check that the user's profile rating gets deleted correctly.
    assert first_test_user_ratings_after_delete == []


def test_delete_review_from_movie_does_not_exists_should_error(
    api_client, first_test_user, first_test_review
) -> None:

    """
    Test delete review for a movie that does not exist.

    This test verifies that when the client attempts to delete review
    for a movie using a not existed movie slug, the API responds with
    an 'HTTP 404 Not Found' error.

    The test constructs a URL for the movie review endpoint using a not existed movie
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

    url = movie_delete_review_url(
        movie_slug=not_exists_movie_slug,
        review_slug=first_test_review.slug
    )

    response = api_client.delete(path=url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_review_does_not_exists_from_movie_should_error(
    api_client, first_test_user, first_test_movie
) -> None:

    """
    Test delete review that does not exist from a movie.

    This test verifies that when the client attempts to delete
    a review using a not existed review slug for a movie,
    the API responds with an 'HTTP 404 Not Found' error.

    The test constructs a URL for the movie review endpoint using
    a not existed review slug and sends a DELETE request to this URL.
    The test expects the API to respond with an HTTP 404 status code
    indicating that the review with the specified slug was not found.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_user: A fixture that creates the first test user
    in the database.
    :param first_test_movie: First test movie object.
    :return: None
    """

    api_client.force_authenticate(user=first_test_user)

    not_exists_review_slug = 'not-exists-review-slug'

    url = movie_delete_review_url(
        movie_slug=first_test_movie.slug,
        review_slug=not_exists_review_slug
    )

    response = api_client.delete(path=url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_review_from_movie_with_unauthorized_user_should_error(
    api_client, first_test_movie, first_test_review
) -> None:

    """
    Test that an unauthorized user cannot delete a review from a movie
    and receives an error.

    This test verifies that an unauthenticated user receives
    a 401 Unauthorized status when trying to delete a review from a movie.

    :param api_client: An instance of the Django REST Framework's APIClient.
    :param first_test_movie: A fixture providing the first test movie object.
    :return: None
    """

    url = movie_delete_review_url(
        movie_slug=first_test_movie.slug,
        review_slug=first_test_review.slug
    )

    response = api_client.delete(path=url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
