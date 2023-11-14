from django.conf.global_settings import AUTH_USER_MODEL

from movie_recommendation_api.movie.selectors.movie_dependencies import (
    check_movie_release_for_user_rating, get_movie, calculate_and_aggregate_movie_rate, aggregate_movie_reviews_count,
)
from movie_recommendation_api.movie.models import Movie


def get_movie_detail(*, movie_slug: str, user: AUTH_USER_MODEL = None) -> Movie:

    """
    Retrieve detailed information about a specific movie by its slug.

    This function retrieves the detailed representation of a movie based on its slug.
    It includes information such as the movie's genres, cast and crew members,
    reviews, average rating, total number of ratings, total number of reviews and
    the user's rating if authenticated.

    :param movie_slug: (str): The slug of the movie to retrieve.
    :param user: (Optional) The authenticated user (if available).
    :return: Movie: The detailed representation of the movie.
    """

    get_movie_obj = get_movie(movie_slug=movie_slug)
    aggregate_reviews_count_to_movie = aggregate_movie_reviews_count(movie=get_movie_obj)
    aggregate_movie_rate = calculate_and_aggregate_movie_rate(movie=aggregate_reviews_count_to_movie)
    checking_movie_user_rating = check_movie_release_for_user_rating(movie=aggregate_movie_rate, user=user)

    return checking_movie_user_rating
