import django_filters as filters

from django.db.models import Q, QuerySet
# from django.utils import timezone

from movie_recommendation_api.core.exceptions import LimitExceededException
from movie_recommendation_api.movie.models import Movie


class MovieFilterSet(filters.FilterSet):
    """
    FilterSet class for filtering movies.

    Attributes:
        title (CharFilter): Filter for exact match of the movie title.
        search (CharFilter): Filter for searching movies by title
                             using full-text search.
        genre__title (CharFilter): Filter for searching movies by genre titles.

    Methods:
        filter_search(self, queryset, name, value): Custom filter method
                        for performing full-text search on movie titles.

    Meta:
        model (Movie): The model to be filtered.
        fields (tuple): The fields to be used for filtering.

    Raises:
        APIException: If there is an error in the filter.
    """

    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    search = filters.CharFilter(method="filter_search")
    genre__title = filters.CharFilter(
        field_name='genre', method='filter_genre__title'
    )

    def filter_search(
            self, queryset: QuerySet[Movie], name: str, value: str
    ) -> QuerySet[Movie]:

        """
        Custom filter method for performing full-text search on
        movie titles and synopsis.

        :param queryset: The movie queryset to be filtered.
        :param name: The name of the field to be filtered.
        :param value: The search value.
        :return: queryset: The filtered movie queryset.
        """
        return queryset.filter(
            Q(title__icontains=value) | Q(synopsis__icontains=value)
        )

    def filter_genre__title(
            self, queryset: QuerySet[Movie], name: str, value: str
    ) -> QuerySet[Movie]:

        """
        Custom filter method for filtering movies by genre titles.

        The genre__title filter allows filtering movies based on
        comma-separated genre titles. It accepts a list of genre
        titles and returns movies that have any of the specified genres.
        If the limit is exceeded, the method raises a `LimitExceededException`
        with an appropriate error message. Otherwise, it filters the `queryset`
        by checking if each movie has any of the specified genres and returns the
        filtered queryset.

        :param queryset: The movie queryset to be filtered.
        :param name: The name of the field to be filtered.
        :param value: The genre titles to filter movies by (comma-separated).
        :return: queryset: The filtered movie queryset.

        :raises LimitExceededException: If the number of genres provided exceeds
        the maximum allowed limit.
        """

        limit = 4
        genres = value.split(",")

        if len(genres) > limit:
            raise LimitExceededException(f"You cannot add more than {limit} genres")
        for genre in genres:
            queryset = queryset.filter(genre__title__icontains=genre.strip())

        return queryset

    # cast_crew__in = filters.CharFilter(
    #   field_name='cast_crew', method="filter_cast_crew__in"
    # )
    # release_date__range = filters.CharFilter(
    #   field_name='release_date', method="filter_release_date__range"
    # )
    # rating__range = filters.

    # def filter_cast_crew__in(self, queryset, name, value):
    #     limit = 10
    #     cast_crew_names = value.split(",")
    #     if len(cast_crew_names) > limit:
    #         raise APIException(f"You cannot add more than {limit} cast/crew names")
    #     return queryset.filter(cast_crew__name__in=cast_crew_names)

    # def filter_release_date__range(self, queryset, name, value):
    #     limit = 2
    #     release_date__in = value.split(",")
    #     if len(release_date__in) > limit:
    #         raise APIException("Please just add two date with ',' in the middle")
    #
    #     first_date, second_date = release_date__in
    #
    #     if not second_date:
    #         second_date = timezone.now()
    #
    #     if not first_date:
    #         return queryset.filter(release_date__date__lt=second_date)
    #
    #     return queryset.filter(release_date__date__range=(first_date, second_date))

    class Meta:
        model = Movie
        fields = ('title', 'genre', 'search')
