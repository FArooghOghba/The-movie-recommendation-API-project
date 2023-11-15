import pytest

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.users.selectors import get_profile_detail
from movie_recommendation_api.users.serializers.user_profile_serializer import (
    OutPutProfileModelSerializer
)


pytestmark = pytest.mark.django_db


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


def movie_create_review_url(movie_slug: str) -> str:

    """
    Generate the URL for the movie create review API endpoint based
    on the movie slug.

    This function takes a movie slug as input and generates the URL for the
    movie create review API endpoint by using the `reverse` function provided
    by Django's URL resolver. The movie slug is included as a parameter in the URL.

    :param movie_slug: The slug of the movie.
    :return: The URL for the movie creates 'review API' endpoint.
    """

    return reverse(viewname='api:movie:create-review', args=[movie_slug])


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
    test_user_profile = get_profile_detail(username=first_test_user.username)
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


def test_get_user_profile_updated_when_user_rating_to_movies_return_successful(
    api_client, first_test_user, first_test_movie,
    first_test_rating, second_test_rating
) -> None:

    """
    Test that adding a movie rating updates the user's profile ratings.

    This test verifies that when a user rates a movie, the user's profile
    reflects the newly added rating. It adds test ratings to the user's
    profile, authenticates the user, and then adds a new rating via the API.
    Finally, it checks that the user's profile correctly reflects the added rating.

    :param api_client: The Django test API client.
    :param first_test_user: The first test user.
    :param first_test_movie: The first test movie.
    :param first_test_rating: The first test rating.
    :param second_test_rating: The second test rating.

    :return: None
    """

    test_user_profile = first_test_user.profile
    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    # Add data to the user's profile
    test_user_profile.ratings.add(first_test_rating, second_test_rating)

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    # Add a new rating via the API
    url = movie_rating_url(movie_slug=first_test_movie.slug)
    payload = {'rate': 7}

    rating_response = api_client.post(path=url, data=payload)
    assert rating_response.status_code == status.HTTP_201_CREATED

    # Check that the user's profile correctly reflects the added rating
    profile_response = api_client.get(
        path=test_user_profile_url,
    )
    assert profile_response.status_code == status.HTTP_200_OK

    # Check rating count and rating details
    user_profile_ratings = profile_response.data['ratings']
    user_profile_ratings_detail = user_profile_ratings['ratings_detail']
    user_profile_ratings_count = user_profile_ratings['ratings_count']
    assert user_profile_ratings_count == 3
    assert len(user_profile_ratings_detail) == user_profile_ratings_count

    rating_added_by_user = user_profile_ratings_detail[0]['user_rating']
    assert rating_added_by_user == payload['rate']


def test_get_user_profile_updated_when_user_review_to_movies_return_successful(
    api_client, first_test_user, first_test_movie,
    first_test_review, second_test_review
) -> None:

    """
    Test that adding a movie review updates the user's profile reviews.

    This test verifies that when a user writes a movie review, the user's profile
    reflects the newly added review. It adds test reviews to the user's
    profile, authenticates the user, and then adds a new review via the API.
    Finally, it checks that the user's profile correctly reflects the added review.

    :param api_client: The Django test API client.
    :param first_test_user: The first test user.
    :param first_test_movie: The first test movie.
    :param first_test_review: The first test review.
    :param second_test_review: The second test review.

    :return: None
    """

    test_user_profile = first_test_user.profile
    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    # Add data to the user's profile
    test_user_profile.reviews.add(first_test_review, second_test_review)

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    # Add a new review via the API
    url = movie_create_review_url(movie_slug=first_test_movie.slug)
    payload = {
        'title': 'first test review title',
        'spoilers': True,
        'review': 'This is Test user review.'
    }

    review_response = api_client.post(path=url, data=payload)
    assert review_response.status_code == status.HTTP_201_CREATED

    # Check that the user's profile correctly reflects the added review
    profile_response = api_client.get(
        path=test_user_profile_url,
    )
    assert profile_response.status_code == status.HTTP_200_OK

    # Check reviews count and review details
    user_profile_reviews = profile_response.data['reviews']
    user_profile_reviews_detail = user_profile_reviews['reviews_detail']
    user_profile_reviews_count = user_profile_reviews['reviews_count']
    assert user_profile_reviews_count == 3
    assert len(user_profile_reviews_detail) == user_profile_reviews_count

    review_added_by_user = user_profile_reviews_detail[0]['content']
    review_title_added_by_user = user_profile_reviews_detail[0]['title']
    assert review_added_by_user == payload['review']
    assert review_title_added_by_user == payload['title']


def test_get_profile_counts_for_watchlist_favorite_genres_return_successful(
    api_client, first_test_movie, second_test_movie, third_test_movie,
    first_test_genre, second_test_genre, third_test_genre, forth_test_genre,
    first_test_user,
) -> None:

    """
    Test to ensure that the user's profile correctly reflects watchlist
    and favorite genres counts.

    This test verifies that the user's profile, when accessed through
    the API, correctly displays the counts for watchlist movies and
    favorite genres.


    :param api_client (APIClient): The Django REST framework API client.
    :param first_test_movie (Movie): An instance of the first test movie.
    :param second_test_movie (Movie): An instance of the second test movie.
    :param third_test_movie (Movie): An instance of the third test movie.
    :param first_test_genre (Genre): An instance of the first test genre.
    :param second_test_genre (Genre): An instance of the second test genre.
    :param third_test_genre (Genre): An instance of the third test genre.
    :param forth_test_genre (Genre): An instance of the fourth test genre.
    :param first_test_user (User): An instance of the first test user.

    :return: None
    """

    test_user_profile = first_test_user.profile
    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    # Add data to the user's profile
    test_user_profile.watchlist.add(
        first_test_movie, second_test_movie, third_test_movie
    )

    test_user_profile.favorite_genres.add(
        first_test_genre, second_test_genre, third_test_genre, forth_test_genre
    )

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    # Check that the user's profile correctly reflects the added review
    profile_response = api_client.get(
        path=test_user_profile_url,
    )
    assert profile_response.status_code == status.HTTP_200_OK

    # Check favorite genres count and details
    user_profile_favorite_genres = profile_response.data['favorite_genres']
    user_profile_genres_detail = user_profile_favorite_genres['genres']
    user_profile_favorite_genres_count = user_profile_favorite_genres['genres_count']
    assert user_profile_favorite_genres_count == 4
    assert len(user_profile_genres_detail) == user_profile_favorite_genres_count

    # Check watchlist count and movie details
    user_profile_watchlist = profile_response.data['watchlist']
    user_profile_watchlist_movies = user_profile_watchlist['movies']
    user_profile_watchlist_count = user_profile_watchlist['watchlist_count']
    assert user_profile_watchlist_count == 3
    assert len(user_profile_watchlist_movies) == user_profile_watchlist_count
