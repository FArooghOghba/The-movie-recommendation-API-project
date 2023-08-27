from typing import Optional

from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, QuerySet
from django.db.models.aggregates import Avg

from movie_recommendation_api.movie.models import Movie, Rating, Role
from movie_recommendation_api.movie.filters import MovieFilterSet


def get_movie_list(*, filters: Optional[dict] = None) -> QuerySet[Movie]:
    """
    Get a list of movies based on filters.
    This function retrieves a queryset of Movie objects and applies
    the provided filters. It also annotates the queryset with
    the average rating for each movie using the 'movie_ratings' related name.

    :param filters:  (dict, optional): Optional filters to apply when
           retrieving movies. Defaults to None.
    :return: QuerySet[Movie]: A queryset of movies matching the provided filters.
    """

    filters = filters or {}

    movies_queryset = Movie.objects \
        .prefetch_related('genre', 'cast_crew')\
        .defer('runtime', 'created_at', 'updated_at')

    movies_queryset = movies_queryset\
        .annotate(avg_rating=Avg('movie_ratings__rating'))

    if filters:
        movies_queryset = MovieFilterSet(filters, movies_queryset).qs

    return movies_queryset.order_by('-release_date')


def get_movie_detail(*, movie_slug: str, user: get_user_model() = None) -> Movie:
    """
    Retrieve detailed information about a specific movie by its slug.

    This function retrieves the detailed representation of a movie based on its slug.
    It includes information such as the movie's genres, cast and crew members,
    average rating, total number of ratings, and the user's rating if authenticated.

    :param movie_slug: (str): The slug of the movie to retrieve.
    :param user: (Optional) The authenticated user (if available).
    :return: Movie: The detailed representation of the movie.
    """

    # Create a Prefetch object that fetches roles for a specific movie
    cast_crew = Prefetch(
        lookup='cast_crew',
        queryset=Role.objects
        .filter(movie__slug=movie_slug)
        .select_related('cast_crew')
        .prefetch_related('careers'),
        to_attr='cast_crew_roles'
    )

    # Fetch the movie with the associated genres, cast_crews, and their roles
    movie = (
        Movie.objects
        .prefetch_related('genre', cast_crew)
        .get(slug=movie_slug)
    )

    # Calculate the average rating for the movie
    # Annotates the count of ratings for the movie
    ratings_data = movie.movie_ratings.aggregate(
        avg_rating=Avg('rating'),
        ratings_count=Count('id')
    )

    movie.avg_rating = ratings_data['avg_rating']
    movie.ratings_count = ratings_data['ratings_count']

    # Check if the movie is released
    release_date = movie.release_date
    current_date = date.today()

    if movie.release_date and current_date < release_date:
        movie.user_rating = "Movie has not been released yet."

    # If a user is authenticated, get their rating for the movie
    elif user and user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=user, movie=movie)
            movie.user_rating = user_rating.rating
        except Rating.DoesNotExist:
            # If the user has not rated the movie yet, display a message
            movie.user_rating = "You have not rated this movie yet."
    else:
        # If the user is not authenticated, display a message
        movie.user_rating = "Please login to rate this movie."

    return movie


def get_movie_obj(*, movie_slug: str) -> Movie:
    """
    Retrieves a movie object based on the provided movie slug.

    This function takes a movie slug as an input parameter and retrieves the
    corresponding movie object from the database using the Django ORM.

    :param movie_slug: The slug of the movie to retrieve.
    :return: The retrieved movie object.
    """

    movie_obj = Movie.objects.get(slug=movie_slug)
    return movie_obj
