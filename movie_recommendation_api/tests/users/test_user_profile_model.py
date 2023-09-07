import pytest

from django.core.exceptions import ValidationError

from movie_recommendation_api.users.services import register


pytestmark = pytest.mark.django_db


def test_create_profile_alongside_user_return_successful(
    time_tracker, first_test_user
) -> None:

    """
    Test creating a user profile alongside a user and check if it's successful.

    This test ensures that when creating a user, a user profile is also created
    and its attributes match the expected values.

    :param time_tracker: A fixture for tracking test execution time.
    :param first_test_user: A fixture for the first test user.

    :return: None
    """

    test_user_profile = first_test_user.profile
    expected_representation = (
        f"{first_test_user} >> "
        f"{test_user_profile.first_name} "
        f"{test_user_profile.last_name}"
    )

    assert str(test_user_profile) == expected_representation
    assert test_user_profile.first_name
    assert test_user_profile.last_name
    assert test_user_profile.bio


def test_create_profile_with_favorite_genres_return_successful(
    time_tracker, first_test_user, first_test_genre, second_test_genre
) -> None:

    """
    Test adding favorite genres to a user profile and check if it's successful.

    This test ensures that genres can be added to a user's profile and
    retrieved correctly.

    :param time_tracker: A fixture for tracking test execution time.
    :param first_test_user: A fixture for the first test user.
    :param first_test_genre: A fixture for the first test genre.
    :param second_test_genre: A fixture for the second test genre.

    :return: None
    """

    test_user_profile = first_test_user.profile
    test_user_profile.favorite_genres.add(first_test_genre, second_test_genre)

    test_user_favorite_genres = list(
        test_user_profile.favorite_genres.order_by('id')
    )
    assert test_user_favorite_genres == [first_test_genre, second_test_genre]


def test_create_profile_with_watchlist_return_successful(
    time_tracker, first_test_user, first_test_movie, second_test_movie
) -> None:

    """
    Test adding movies to a user profile and check if it's successful.

    This test ensures that movies can be added to a user's profile and
    retrieved correctly.

    :param time_tracker: A fixture for tracking test execution time.
    :param first_test_user: A fixture for the first test user.
    :param first_test_movie: A fixture for the first test movie.
    :param second_test_movie: A fixture for the second test movie.

    :return: None
    """

    test_user_profile = first_test_user.profile
    test_user_profile.watchlist.add(first_test_movie, second_test_movie)

    test_user_watchlist = list(test_user_profile.watchlist.order_by('id'))
    assert test_user_watchlist == [first_test_movie, second_test_movie]


def test_create_profile_with_ratings_return_successful(
    time_tracker, first_test_user, first_test_rating, second_test_rating,
    first_test_movie, second_test_movie
) -> None:

    """
    Test adding movie ratings to a user profile and check if it's successful.

    This test ensures that movie ratings can be added to a user's profile and
    retrieved correctly.

    :param time_tracker: A fixture for tracking test execution time.
    :param first_test_user: A fixture for the first test user.
    :param first_test_rating: A fixture for the first test movie rating.
    :param second_test_rating: A fixture for the second test movie rating.
    :param first_test_movie: A fixture for the first test movie.
    :param second_test_movie: A fixture for the second test movie.

    :return: None
    """

    first_test_rating.user = first_test_user
    first_test_rating.movie = first_test_movie
    first_test_rating.save()

    second_test_rating.user = first_test_user
    second_test_rating.movie = second_test_movie
    second_test_rating.save()

    test_user_profile = first_test_user.profile
    test_user_profile.ratings.add(first_test_rating, second_test_rating)

    test_user_ratings = list(test_user_profile.ratings.order_by('id'))
    assert test_user_ratings == [first_test_rating, second_test_rating]


def test_create_profile_with_reviews_return_successful(
    time_tracker, first_test_user, first_test_review, second_test_review,
    first_test_movie, second_test_movie
) -> None:

    """
    Test adding movie reviews to a user profile and check if it's successful.

    This test ensures that movie reviews can be added to a user's profile and
    retrieved correctly.

    :param time_tracker: A fixture for tracking test execution time.
    :param first_test_user: A fixture for the first test user.
    :param first_test_review: A fixture for the first test movie reviews.
    :param second_test_review: A fixture for the second test movie reviews.
    :param first_test_movie: A fixture for the first test movie.
    :param second_test_movie: A fixture for the second test movie.

    :return: None
    """

    first_test_review.user = first_test_user
    first_test_review.movie = first_test_movie
    first_test_review.save()

    second_test_review.user = first_test_user
    second_test_review.movie = second_test_movie
    second_test_review.save()

    test_user_profile = first_test_user.profile
    test_user_profile.reviews.add(first_test_review, second_test_review)

    test_user_ratings = list(test_user_profile.reviews.order_by('id'))
    assert test_user_ratings == [first_test_review, second_test_review]


def test_create_profile_without_user_return_error() -> None:
    """
    Test creating a user profile without a user reference fails.

    This test ensures that creating a user profile without associating it
    with a user instance raises the appropriate exception.

    :return: None
    """

    first_name = "John"
    last_name = "Doe"
    bio = "A test bio."

    with pytest.raises(Exception):
        register(
            username=None, email=None, password=None,
            first_name=first_name, last_name=last_name, bio=bio
        )


def test_create_profile_with_existing_username_return_error(
    first_test_user
) -> None:

    """
    Test registering a user with an existing username fails.

    This test ensures that attempting to register a user with a username
    that already exists in the database raises the appropriate exception.

    :param first_test_user: A fixture for the first test user.

    :return: None
    """

    existing_username = first_test_user.username
    email = 'test_email@example.com'
    password = "test_password"
    first_name = "John"
    last_name = "Doe"
    bio = "A test bio."

    with pytest.raises(ValidationError):
        register(
            username=existing_username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
        )
