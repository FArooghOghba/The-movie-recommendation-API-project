from typing import Optional

from django.db.models import QuerySet

from movie_recommendation_api.movie.models import Movie
from movie_recommendation_api.movie.filters import MovieFilterSet


def get_movie_list(*, filters: Optional[dict] = None) -> QuerySet[Movie]:
    """
    Get a list of movies based on filters.

    :param filters:  (dict, optional): Optional filters to apply when
           retrieving movies. Defaults to None.
    :return: QuerySet[Movie]: A queryset of movies matching the provided filters.
    """

    filters = filters or {}
    movies_queryset = Movie.objects.all()

    if filters:
        return MovieFilterSet(filters, movies_queryset).qs

    return movies_queryset


def get_movie_detail(*, slug: str) -> Movie:
    """
    Get a specific movie by its slug.

    :param slug: (str): The slug of the movie.
    :return: Movie: The movie with the specified slug.
    """
    return Movie.objects.get(slug=slug)
