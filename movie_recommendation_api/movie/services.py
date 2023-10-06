from django.contrib.auth import get_user_model
from django.db import transaction

from movie_recommendation_api.movie.models import Movie, Rating, Review
from movie_recommendation_api.movie.selectors import get_movie_detail
from movie_recommendation_api.users.models import Profile


def get_movie(movie_slug: str) -> Movie:

    """
    Retrieve a movie by its unique slug.

    :param movie_slug: The unique slug of the movie.
    :return: The retrieved Movie object.
    """

    movie = Movie.objects.get(slug=movie_slug)
    return movie


@transaction.atomic
def rate_movie(*, user: get_user_model(), movie_slug: str, rate: int) -> Movie:
    """
    This function creates a rating record for the given user and movie with
    the provided rating value. It first fetches the movie object based on
    the provided movie_slug and then creates a new Rating object with the user,
    movie, and rating data.

    The function is wrapped in a "transaction.atomic" block, ensuring that
    the database operations are executed within a single transaction.
    This ensures data integrity and consistency.

    :raises:
        Movie.DoesNotExist: If the movie with the provided movie_slug
        does not exist in the database.

    :param user: (User): The user who is rating the movie.
    :param movie_slug: (str): The unique slug representing the movie being rated.
    :param rate: (int): The rating value given by the user. It Should be an integer
                between 1 and 10.
    :return: Movie object that has been rated.
    """

    movie = get_movie(movie_slug=movie_slug)

    rating = Rating.objects.create(
        user=user, movie=movie, rating=rate
    )

    user_profile = Profile.objects.get(user=user)
    user_profile.ratings.add(rating)

    # cache_profile(user=user)

    rated_movie = get_movie_detail(movie_slug=movie_slug, user=user)
    return rated_movie


@transaction.atomic
def update_movie_rating(
    *, user: get_user_model(), movie_slug: str, updated_rate: int
) -> Movie:

    """
    This function updates a rating record for the given user and movie with
    the provided rating value. It first fetches the movie object based on
    the provided movie_slug and then updates a new Rating object with the user,
    movie, and rating data.

    The function is wrapped in a "transaction.atomic" block, ensuring that
    the database operations are executed within a single transaction.
    This ensures data integrity and consistency.

    :raises:
        Movie.DoesNotExist: If the movie with the provided movie_slug
        does not exist in the database.

    :param user: (User): The user who is rating the movie.
    :param movie_slug: (str): The unique slug representing the movie being rated.
    :param updated_rate: (int): The new rating value given by the user.
    It Should be an integer between 1 and 10.
    :return: Movie object that has been rated.
    """

    movie = get_movie(movie_slug=movie_slug)

    (
        Rating.objects
        .filter(user=user, movie=movie)
        .update(rating=updated_rate)
    )

    updated_movie_rating = get_movie_detail(movie_slug=movie_slug, user=user)
    return updated_movie_rating


def delete_movie_rating(
    *, user: get_user_model(), movie_slug: str
) -> Movie:

    """
    This function deletes a rating record for the given user and movie with
    the provided movie slug. It first fetches the movie object based on
    the provided movie_slug and then deletes the Rating object for the given user
    and movie.

    :raises:
        Movie.DoesNotExist: If the movie with the provided movie_slug
        does not exist in the database.

    :param user: (User): The user who is rating the movie.
    :param movie_slug: (str): The unique slug representing the movie being rated.

    :return: Movie object that has been rated.
    """

    movie = get_movie(movie_slug=movie_slug)

    rating_obj = Rating.objects.get(user=user, movie=movie)
    rating_obj.delete()

    deleted_movie_rating = get_movie_detail(movie_slug=movie_slug, user=user)
    return deleted_movie_rating


@transaction.atomic
def review_movie(*, user: get_user_model(), movie_slug: str, review: str) -> Movie:
    """
    Create a movie review for a specific movie.

    This function creates a movie review for the given user and movie with
    the provided review content. It first fetches the movie object based on
    the provided movie_slug and then creates a new Review object with the user,
    movie, and review data.

    The function is wrapped in a "transaction.atomic" block, ensuring that
    the database operations are executed within a single transaction.
    This ensures data integrity and consistency.

    :param user: The user who is writing the review (User model instance).
    :param movie_slug: The slug of the movie for which the review is being written.
    :param review: The content of the review.
    :return: The Movie object associated with the review.
    """

    movie = get_movie(movie_slug=movie_slug)

    review = Review.objects.create(
        user=user, movie=movie, content=review
    )

    user_profile = Profile.objects.get(user=user)
    user_profile.reviews.add(review)

    # cache_profile(user=user)

    return movie
