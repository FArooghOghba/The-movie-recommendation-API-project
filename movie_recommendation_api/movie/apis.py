from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from movie_recommendation_api.movie.serializers import (
    MovieDetailOutPutModelSerializer, MovieOutPutModelSerializer,
    MovieFilterSerializer,
)
from movie_recommendation_api.movie.selectors import get_movie_detail, get_movie_list
from movie_recommendation_api.api.pagination import (
    CustomLimitOffsetPagination, get_paginated_response_context
)


class MovieAPIView(APIView):
    """
    API view for retrieving a list of movies.

    Output Serializer:
        MovieOutPutModelSerializer: Serializer for the output
                                    representation of movies.

    Pagination:
        CustomLimitOffsetPagination: Custom pagination class for movie list.

    Methods:
        get(self, request): Retrieves a paginated list of movies based on
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

        Query Parameters:
            title (str): Filter movies by title.
            search (str): Search query to filter movies.

        Raises:
            ValidationError: If the filter parameters are invalid.
        :param request: The request object.
        :return: Paginated response containing the list of movies.
        """

        filters_serializer = MovieFilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        try:
            movie_list_queryset = get_movie_list(
                filters=filters_serializer.validated_data
            )
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=self.output_serializer,
            queryset=movie_list_queryset,
            request=request,
            view=self,
        )


class MovieDetailAPIView(APIView):
    """
    API view for retrieving a movie detail.

    Output Serializer:
        MovieDetailOutPutModelSerializer: Serializer for the detailed
                                          representation of a movie.

    Pagination:
        CustomLimitOffsetPagination: Custom pagination class for movie detail.

    Methods:
        get(self, request, movie_slug): Retrieves the detail of a movie
                                        based on the provided movie slug.

    """
    output_serializer = MovieDetailOutPutModelSerializer

    class Pagination(CustomLimitOffsetPagination):
        default_limit = 10

    @extend_schema(
        responses=MovieDetailOutPutModelSerializer,
    )
    def get(self, request, movie_slug):
        """
        Retrieves the detail of a movie based on the provided movie slug.

        Raises:
            DoesNotExist: If the movie does not exist.
        :param request: The request object.
        :param movie_slug: (str): The slug of the movie.
        :return: Response containing the detailed representation of the movie.
        """

        try:
            movie_query = get_movie_detail(slug=movie_slug)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.output_serializer(movie_query)

        return Response(serializer.data)
