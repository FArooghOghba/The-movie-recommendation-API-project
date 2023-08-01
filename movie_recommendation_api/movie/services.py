from django.contrib.auth import get_user_model
from django.db import transaction

from movie_recommendation_api.movie.models import Movie, Rating


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

    movie = Movie.objects.get(slug=movie_slug)

    Rating.objects.create(
        user=user, movie=movie, rating=rate
    )
    # cache_profile(user=user)

    return movie
