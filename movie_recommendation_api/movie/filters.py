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
        min_rating (NumberFilter): Filter for searching movies by min rating value.
        max_rating (NumberFilter): Filter for searching movies by max rating value.
        release_date_before (DateField, optional): The release date before which
        to filter movies.
        release_date_after (DateField, optional): The release date after which
        to filter movies.
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
    min_rating = filters.NumberFilter(method='filter_min_rating')
    max_rating = filters.NumberFilter(method='filter_max_rating')
    release_date_before = filters.DateFilter(
        field_name='release_date', lookup_expr='lte'
    )
    release_date_after = filters.DateFilter(
        field_name='release_date', lookup_expr='gte'
    )
    cast_crew = filters.CharFilter(
        field_name='cast_crew__name',
        method='filter_cast_crew'
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

    def filter_min_rating(
            self, queryset: QuerySet[Movie], name: str, value: str
    ) -> QuerySet[Movie]:

        """
        Filter movies based on their minimum average rating.

        This custom filter method is used to filter a queryset of movies based on
        their minimum average rating. It filters movies with an average rating
        greater than or equal to the specified value.

        :param queryset: The queryset of movies to filter.
        :param name: The name of the filter field (unused in this method).
        :param value: The minimum average rating value for filtering.
        :return: The filtered queryset containing movies meeting the criteria.
        """

        queryset = queryset.filter(avg_rating__gte=value)
        return queryset

    def filter_max_rating(
            self, queryset: QuerySet[Movie], name: str, value: str
    ) -> QuerySet[Movie]:

        """
        Filter movies based on their maximum average rating.

        This custom filter method is used to filter a queryset of movies based on
        their maximum average rating. It filters movies with an average rating
        less than or equal to the specified value.

        :param queryset: The queryset of movies to filter.
        :param name: The name of the filter field (unused in this method).
        :param value: The maximum average rating value for filtering.
        :return: The filtered queryset containing movies meeting the criteria.
        """

        queryset = queryset.filter(avg_rating__lte=value)
        return queryset

    def filter_cast_crew(
            self, queryset: QuerySet[Movie], name: str, value: str
    ) -> QuerySet[Movie]:
        """
        Filter movies based on their cast and crew members.

        This custom filter method allows users to filter movies based on
        the names of cast and crew members. Users can specify multiple names
        separated by commas, and movies with any of the specified cast or crew
        members will be included in the results.

        :param queryset: The queryset of movies to filter.
        :param name: The name of the filter field (unused in this method).
        :param value: The names of cast and crew members to filter by
        (comma-separated).
        :return: The filtered queryset containing movies meeting the criteria.
        """

        limit = 5
        names = value.split(",")
        filter_condition = Q()

        print(names)
        if len(names) > limit:
            raise LimitExceededException(f"You cannot add more than {limit} genres")
        for name in names:
            # Create a Q object that checks if the name appears in
            # either the cast or crew
            filter_condition |= Q(cast_crew__name__icontains=name.strip())

        queryset = queryset.filter(filter_condition)
        return queryset

    class Meta:
        model = Movie
        fields = ('title', 'genre', 'search', 'cast_crew')
