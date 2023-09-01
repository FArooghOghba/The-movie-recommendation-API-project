from django.contrib.auth import get_user_model
from django.db import transaction

from movie_recommendation_api.movie.models import Movie, Rating, Review


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

    Raises:
        Movie.DoesNotExist: If the movie with the provided movie_slug
        does not exist in the database.

    :param user: (User): The user who is rating the movie.
    :param movie_slug: (str): The unique slug representing the movie being rated.
    :param rate: (int): The rating value given by the user. Should be an integer
                between 1 and 10.
    :return: Movie object that has been rated.
    """

    movie = get_movie(movie_slug=movie_slug)

    Rating.objects.create(
        user=user, movie=movie, rating=rate
    )
    # cache_profile(user=user)

    return movie


@transaction.atomic
def review_movie(*, user: get_user_model(), movie_slug: str, review: str) -> Movie:
    """
    Create a movie review for a specific movie.

    :param user: The user who is writing the review (User model instance).
    :param movie_slug: The slug of the movie for which the review is being written.
    :param review: The content of the review.
    :return: The Movie object associated with the review.
    """

    movie = get_movie(movie_slug=movie_slug)

    Review.objects.create(
        user=user, movie=movie, content=review
    )
    # cache_profile(user=user)

    return movie
