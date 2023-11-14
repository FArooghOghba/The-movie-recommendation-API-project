from typing import Optional

from django.db.models import QuerySet

from movie_recommendation_api.movie.filters import MovieFilterSet
from movie_recommendation_api.movie.models import Movie
from movie_recommendation_api.movie.selectors.movie_dependencies import (
    calculate_and_annotate_movie_queryset_rates
)


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

    movies_queryset = calculate_and_annotate_movie_queryset_rates(
        movies_queryset=movies_queryset
    )

    if filters:
        movies_queryset = MovieFilterSet(filters, movies_queryset).qs

    return movies_queryset.order_by('-release_date')
