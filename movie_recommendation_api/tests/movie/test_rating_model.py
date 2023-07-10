import pytest

from django.core.exceptions import ValidationError

from movie_recommendation_api.movie.models import Rating


pytestmark = pytest.mark.django_db


def test_create_rating_successful(first_test_user, first_test_movie) -> None:
    """
    Test that a rating can be created successfully.

    This test creates a rating using the Rating model's 'create()' method and
    verifies that it is created with the expected attributes.
    It checks the user, movie, and rating values of the created rating.

    :param first_test_user: A fixture providing the first test user object.
    :param first_test_movie: A fixture providing the first test movie object.
    :return: None
    """
    rating_value = 4.5

    test_rating = Rating.objects.create(
        user=first_test_user, movie=first_test_movie, rating=rating_value
    )

    assert str(test_rating) == f"Rate for {test_rating.movie.title} by " \
                               f"{test_rating.user.username} >>" \
                               f"{test_rating.rating}"

    assert test_rating.user == first_test_user
    assert test_rating.movie == first_test_movie
    assert test_rating.rating == rating_value


@pytest.mark.parametrize(
    'invalid_rating',
    ('', 'rate', -1.0, 10.5),
)
def test_create_rating_with_wrong_rating_return_error(
    first_test_rating, invalid_rating
) -> None:
    """
    Test that creating a rating with invalid rating values raises a ValidationError.

    This test sets the rating field of the existing rating object to invalid
    rating values and checks if calling the `full_clean()` method raises
    a ValidationError.

    :param first_test_rating: A fixture providing the first test rating object.
    :param invalid_rating: An invalid rating value to be assigned to
           the rating object.
    :return: None
    """

    test_rating = first_test_rating
    test_rating.rating = invalid_rating

    with pytest.raises(ValidationError):
        test_rating.full_clean()


def test_create_rating_for_movies_successful(
    first_test_movie, second_test_movie, first_test_user, second_test_user
) -> None:
    """
    Test that ratings can be created for movies successfully and the average
    rating is calculated correctly.

    This test creates multiple ratings for different movies using
    the Rating model's 'create()' method and verifies that they are
    created successfully. It checks the average rating calculation for
    a movie and also the count of ratings associated with each movie.

    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :param first_test_user: A fixture providing the first test user object.
    :param second_test_user: A fixture providing the second test user object.
    :return: None
    """

    first_rate_for_first_movie = Rating.objects.create(
        user=first_test_user,
        movie=first_test_movie,
        rating=6.0
    )

    second_rate_for_first_movie = Rating.objects.create(
        user=second_test_user,
        movie=first_test_movie,
        rating=5.0
    )

    first_rate_for_second_movie = Rating.objects.create(
        user=first_test_user,
        movie=second_test_movie,
        rating=7.0
    )

    expected_average_for_first_movie = (
       first_rate_for_first_movie.rating + second_rate_for_first_movie.rating
                       ) / 2
    assert first_test_movie.average_rating == expected_average_for_first_movie

    test_first_movie_ratings_count = first_test_movie.ratings.count()
    assert test_first_movie_ratings_count == len([first_rate_for_first_movie, second_rate_for_first_movie])

    expected_average_for_second_movie = first_rate_for_second_movie.rating
    assert second_test_movie.average_rating == expected_average_for_second_movie

    test_second_movie_ratings_count = second_test_movie.ratings.count()
    assert test_second_movie_ratings_count == len([first_rate_for_second_movie])


def test_create_rating_for_users_successful(
    first_test_movie, second_test_movie, first_test_user, second_test_user
) -> None:
    """
    Test that ratings can be created for users successfully and the average
    rating is calculated correctly.

    This test creates multiple ratings for different users and verifies
    that they are created successfully. It checks the count of ratings
    associated with each user.

    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :param first_test_user: A fixture providing the first test user object.
    :param second_test_user: A fixture providing the second test user object.
    :return: None
    """

    first_rate_for_first_user = Rating.objects.create(
        user=first_test_user,
        movie=first_test_movie,
        rating=6.0
    )

    second_rate_for_first_user = Rating.objects.create(
        user=first_test_user,
        movie=second_test_movie,
        rating=5.0
    )

    first_rate_for_second_user = Rating.objects.create(
        user=second_test_user,
        movie=first_test_movie,
        rating=7.0
    )

    first_user_ratings = Rating.objects.filter(user=first_test_user)
    assert list(first_user_ratings) == [first_rate_for_first_user, second_rate_for_first_user]

    second_user_ratings = Rating.objects.filter(user=second_test_user)
    assert list(second_user_ratings) == [first_rate_for_second_user]
