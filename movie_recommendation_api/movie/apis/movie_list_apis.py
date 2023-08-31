from rest_framework.views import APIView
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from movie_recommendation_api.api.exception_handlers import handle_exceptions
from movie_recommendation_api.movie.serializers.movie_list_serializers import (
    MovieOutPutModelSerializer,
)
from movie_recommendation_api.movie.serializers.movie_filter_serializers import (
    MovieFilterSerializer,
)

from movie_recommendation_api.movie.selectors import get_movie_list
from movie_recommendation_api.api.pagination import (
    CustomLimitOffsetPagination, get_paginated_response_context
)


class MovieAPIView(APIView):
    """
    API view for retrieving a list of movies.

    This view allows clients to retrieve a paginated
    list of movies based on the provided filters.
    The view uses the `MovieOutPutModelSerializer` to serialize
    the output representation of movies and
    the `CustomLimitOffsetPagination` class to paginate the results.

    Output Serializer:
        MovieOutPutModelSerializer: Serializer for the output
        representation of movies.

    Pagination:
        CustomLimitOffsetPagination: Custom pagination class for a movie list.

    Methods:
        get(self, request): Retrieve a paginated list of movies based on
        the provided filters.

    """

    output_serializer = MovieOutPutModelSerializer
    # filter_serializer = MovieFilterSerializer

    class Pagination(CustomLimitOffsetPagination):
        default_limit = 10

    @extend_schema(
        parameters=[MovieFilterSerializer],
        responses=MovieOutPutModelSerializer,
    )
    def get(self, request):
        """
        Retrieves a paginated list of movies based on the provided filters.

        This method allows clients to retrieve a paginated list of movies
        by sending a GET request to the movie list endpoint with optional
        filter parameters. The filter parameters are validated using
        the `MovieFilterSerializer` and passed to the `get_movie_list`
        function to retrieve a queryset of movies matching the provided
        filters. The results are then paginated using
        the `CustomLimitOffsetPagination` class and serialized using
        the `MovieOutPutModelSerializer`.

        Query Parameters:
            title (str): Filter movies by title.
            search (str): Search query to filter movies.


        :param request: The request object.
        :return: Paginated response containing the list of movies.

        :raises ValidationError: If the filter parameters are invalid.
        :raises LimitExceededException: If a filter parameter exceeds
        its allowed limit.
        """

        filters_serializer = MovieFilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        try:
            movie_list_queryset = get_movie_list(
                filters=filters_serializer.validated_data
            )
        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )

        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=self.output_serializer,
            queryset=movie_list_queryset,
            request=request,
            view=self,
        )
