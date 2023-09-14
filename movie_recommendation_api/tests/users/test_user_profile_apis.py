import pytest

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.users.models import Profile
from movie_recommendation_api.users.serializers import OutPutProfileModelSerializer


pytestmark = pytest.mark.django_db


def user_profile_url(username: str) -> str:

    """
    Generate the URL for a user's profile.

    :param username: (str) The username of the user.

    :returns str: The URL for the user's profile.
    """

    return reverse(viewname='api:users:profile', args=[username])


def test_register_create_user_profile_return_successful(
    api_client, first_test_user, first_test_movie, second_test_movie,
    first_test_rating, second_test_rating, first_test_review, second_test_review
) -> None:

    """
    Test the user profile retrieval API.

    This test verifies that the API returns the user's profile data correctly.

    :param api_client: The Django REST framework test client.
    :param first_test_user: The first test user.
    :param first_test_movie: The first test movie.
    :param second_test_movie: The second test movie.
    :param first_test_rating: The first test rating.
    :param second_test_rating: The second test rating.
    :param first_test_review: The first test review.
    :param second_test_review: The second test review.

    :return: None
    """

    test_user_profile = first_test_user.profile
    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    # Add data to the user's profile
    test_user_profile.watchlist.add(first_test_movie, second_test_movie)
    test_user_profile.ratings.add(first_test_rating, second_test_rating)
    test_user_profile.reviews.add(first_test_review, second_test_review)

    response = api_client.get(
        path=test_user_profile_url,
    )
    assert response.status_code == status.HTTP_200_OK

    # Serialize the user's profile
    test_user_profile = Profile.objects.get(user=first_test_user)
    test_user_profile_serializer = OutPutProfileModelSerializer(
        instance=test_user_profile
    )
    test_user_profile = test_user_profile_serializer.data

    # Check if the user's profile picture matches
    response_user_profile_picture = response.data['picture']
    test_user_profile_picture = test_user_profile['picture']
    assert response_user_profile_picture.endswith(test_user_profile_picture)

    # Check if the user's watchlist matches
    response_user_profile_watchlist = response.data['watchlist']
    test_user_profile_watchlist = test_user_profile['watchlist']
    assert response_user_profile_watchlist == test_user_profile_watchlist

    # Check if the user's ratings match
    response_user_profile_ratings = response.data['ratings']
    test_user_profile_ratings = test_user_profile['ratings']
    assert response_user_profile_ratings == test_user_profile_ratings

    # Check if the user's reviews match
    response_user_profile_reviews = response.data['reviews']
    test_user_profile_reviews = test_user_profile['reviews']
    assert response_user_profile_reviews == test_user_profile_reviews
