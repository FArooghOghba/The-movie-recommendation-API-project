from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from movie_recommendation_api.api.mixins import ApiAuthMixin
from movie_recommendation_api.movie.serializers import (
    MovieFilterSerializer, MovieOutPutModelSerializer,
    MovieDetailOutPutModelSerializer, MovieDetailInPutSerializer
)
from movie_recommendation_api.movie.selectors import get_movie_detail, get_movie_list
from movie_recommendation_api.movie.services import rate_movie
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


class MovieDetailAPIView(ApiAuthMixin, APIView):
    """
    API view for retrieving a movie detail.

    Output Serializer:
        MovieDetailOutPutModelSerializer: Serializer for the detailed
                                          representation of a movie.
    Methods:
        get(self, request, movie_slug): Retrieves the detail of a movie
                                        based on the provided movie slug.
        post(self, request, movie_slug): POST method for creating a movie rating.
    """

    movie_input_serializer = MovieDetailInPutSerializer
    movie_output_serializer = MovieDetailOutPutModelSerializer

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
            movie_query = get_movie_detail(movie_slug=movie_slug)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )

        output_serializer = self.movie_output_serializer(movie_query)

        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MovieDetailInPutSerializer,
        responses=MovieOutPutModelSerializer
    )
    def post(self, request, movie_slug):
        """
        POST method for creating a movie rating.

        This method allows users to rate a movie by sending a POST request with the
        'rate' field in the request body. The 'rate' field should be a valid integer
        from 1 to 10.

        Raises:
            ValidationError: If the input data is not valid.
            Authorization: If the user does not authorized.

        :param request: (HttpRequest): The request object containing the rating data.
        :param movie_slug: (str): The slug of the movie for which the rating
                is being added.
        :return: Response: A response containing the detailed representation
                of the rated movie, including the newly added rating.
        """

        input_serializer = self.movie_input_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            user = request.user
            rate = input_serializer.validated_data.get('rate')
            rate_movie(
                user=user, movie_slug=movie_slug, rate=rate
            )

            rated_movie = get_movie_detail(movie_slug=movie_slug)
        except Exception as ex:
            return Response(
                data=f"Authorization Error - {ex}",
                status=status.HTTP_401_UNAUTHORIZED
            )

        output_serializer = self.movie_output_serializer(
            rated_movie, context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
