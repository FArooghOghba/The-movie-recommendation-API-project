from typing import Optional

from django.db.models import QuerySet
from django.db.models.aggregates import Avg

from movie_recommendation_api.movie.models import Movie
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
        .prefetch_related('genre')\
        .defer('cast_crew', 'runtime', 'release_date', 'created_at', 'updated_at')

    movies_queryset = movies_queryset\
        .annotate(avg_rating=Avg('movie_ratings__rating'))

    if filters:
        movies_queryset = MovieFilterSet(filters, movies_queryset).qs

    return movies_queryset


def get_movie_detail(*, slug: str) -> Movie:
    """
    Get a specific movie by its slug.

    :param slug: (str): The slug of the movie.
    :return: Movie: The movie with the specified slug.
    """
    movie = Movie.objects.get(slug=slug)
    movie.avg_rating = movie.movie_ratings.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating']

    return movie
