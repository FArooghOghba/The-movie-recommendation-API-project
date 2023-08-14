from typing import Any, Sequence

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from movie_recommendation_api.api.exception_handlers import handle_exceptions
from movie_recommendation_api.api.mixins import ApiAuthMixin
from movie_recommendation_api.movie.models import Movie
from movie_recommendation_api.movie.permissions import CanRateAfterReleaseDate
from movie_recommendation_api.movie.serializers import (
    MovieFilterSerializer, MovieOutPutModelSerializer,
    MovieDetailOutPutModelSerializer, MovieDetailInPutSerializer
)
from movie_recommendation_api.movie.selectors import (
    get_movie_obj, get_movie_detail, get_movie_list
)
from movie_recommendation_api.movie.services import rate_movie
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


class MovieDetailAPIView(ApiAuthMixin, APIView):
    """
    API view for retrieving a movie detail.

    This view allows clients to retrieve the detailed representation of a movie
    and rate a movie by sending GET and POST requests to the movie detail endpoint.
    The view uses the `MovieDetailOutPutModelSerializer` to serialize the output
    representation of the movie and the `MovieDetailInPutSerializer` to validate
    the input data for rating a movie.

    Output Serializer:
        MovieDetailOutPutModelSerializer: Serializer for the detailed
        representation of a movie.

    Input Serializer:
        MovieDetailInPutSerializer: Serializer for validating the input
        data for rating a movie.

    Methods:
        get(self, request, movie_slug): Retrieves the detail of a movie
        based on the provided movie slug.
        post(self, request, movie_slug): POST method for creating a movie rating.
    """

    movie_input_serializer = MovieDetailInPutSerializer
    movie_output_serializer = MovieDetailOutPutModelSerializer

    def get_object(self) -> Movie:
        """
        Retrieves the movie object based on the provided movie slug.

        :return: The retrieved movie object.
        """

        movie_slug = self.kwargs.get('movie_slug')
        movie = get_movie_obj(movie_slug=movie_slug)
        return movie

    def get_permissions(self) -> Sequence[Any] | Any:
        """
        Retrieves the permission classes for the current request.

        This method overrides the default `get_permissions` method to add
        custom permissions for the `post` method. If the current request method
        is `POST`, it adds an instance of the `CanRateAfterReleaseDate` permission
        class to the list of permission classes.

        :return: A list of permission classes to be used for the current request.
        """

        permissions = super().get_permissions()

        if self.request.method == 'POST':
            return permissions + [CanRateAfterReleaseDate()]

        return permissions

    @extend_schema(
        responses=MovieDetailOutPutModelSerializer,
    )
    def get(self, request, movie_slug):
        """
        Retrieves the detail of a movie based on the provided movie slug.

        This method allows clients to retrieve the detailed representation of a movie
        by sending a GET request to the movie detail endpoint with the `movie_slug`
        parameter. The method calls the `get_movie_detail` function with the provided
        `movie_slug` and current user to retrieve the detailed representation of the
        movie. The result is then serialized using
        the `MovieDetailOutPutModelSerializer` and returned in the response.

        :param request: The request object.
        :param movie_slug: (str): The slug of the movie.
        :return: Response containing the detailed representation of the movie.

        :raises DoesNotExist: If the movie does not exist.
        """

        try:
            user = request.user
            movie_query = get_movie_detail(movie_slug=movie_slug, user=user)
        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )

        # pass 'user_rating' to the serializer through
        # the context parameter when instantiating output_serializer.
        output_serializer = self.movie_output_serializer(
            instance=movie_query,
            context={'user_rating': getattr(movie_query, 'user_rating', None)}
        )

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
        from 1 to 10.The input data is validated using
        the `MovieDetailInPutSerializer` and passed to the `rate_movie` function
        to create a new rating for the specified movie. The method then calls
        the `get_movie_detail` function to retrieve the updated detailed
        representation of the rated movie, which is serialized using
        the `MovieDetailOutPutModelSerializer` and returned in the response.


        :param request: (HttpRequest): The request object containing the rating data.
        :param movie_slug: (str): The slug of the movie for which the rating
                is being added.
        :return: Response: A response containing the detailed representation
                of the rated movie, including the newly added rating.

        :raises ValidationError: If the input data is not valid.
        :raises Authorization: If the user does not authorize.
        :raises DoesNotExist: If the movie does not exist.
        """

        input_serializer = self.movie_input_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            user = request.user
            rate = input_serializer.validated_data.get('rate')
            rate_movie(
                user=user, movie_slug=movie_slug, rate=rate
            )

            rated_movie = get_movie_detail(movie_slug=movie_slug, user=user)
        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )

        output_serializer = self.movie_output_serializer(
            rated_movie, context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
