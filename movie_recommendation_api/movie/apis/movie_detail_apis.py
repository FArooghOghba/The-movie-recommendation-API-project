from typing import Any, Sequence

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from movie_recommendation_api.movie.serializers.movie_detail_serializers import (
    MovieDetailRatingInPutSerializer, MovieDetailReviewInPutSerializer,
    MovieDetailOutPutModelSerializer
)
from movie_recommendation_api.movie.services import (
    rate_movie, update_movie_rating, delete_movie_rating,
    review_movie, delete_movie_review
)
from movie_recommendation_api.movie.selectors.movie_detail import get_movie_detail
from movie_recommendation_api.movie.selectors.movie_dependencies import (
    get_movie_release_date, rating_obj_existence
)
from movie_recommendation_api.api.mixins import ApiAuthMixin
from movie_recommendation_api.api.exception_handlers import handle_exceptions
from movie_recommendation_api.movie.permissions import CanRateAfterReleaseDate


class MovieDetailAPIView(ApiAuthMixin, APIView):
    """
    API view for retrieving a movie detail.

    This view allows clients to retrieve the detailed representation of a movie.
    The view uses the `MovieDetailOutPutModelSerializer` to serialize the output
    representation of the movie.

    Output Serializer:
        MovieDetailOutPutModelSerializer: Serializer for the detailed
        representation of a movie.

    :Methods:
        get (self, request, movie_slug): Retrieve the detail of a movie
        based on the provided movie slug.
    """

    movie_output_serializer = MovieDetailOutPutModelSerializer

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


class MovieDetailRatingAPIView(ApiAuthMixin, APIView):

    """
    API view for rating a movie.

    This view allows users to rate a movie by sending a POST request.

    Input Serializer:
        MovieDetailRatingInPutSerializer: Serializer for validating the input
        data for rating a movie.

    Methods:
        post(self, request, movie_slug): POST method for creating a movie rating.
    """

    movie_input_serializer = MovieDetailRatingInPutSerializer
    movie_output_serializer = MovieDetailOutPutModelSerializer

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

        if self.request.method in ['POST', 'PATCH']:
            permissions.append(CanRateAfterReleaseDate())

        return permissions

    @extend_schema(
        request=MovieDetailRatingInPutSerializer,
        responses=MovieDetailOutPutModelSerializer
    )
    def post(self, request, movie_slug):

        """
        POST method for creating or updating a movie rating.

        This method allows users to rate a movie by sending a
        POST request with the 'rate' field in the request body.
        The 'rate' field should be a valid integer from 1 to 10.
        The input data is validated using the `MovieDetailInPutSerializer`
        and passed to the `rate_movie` function to create a new rating for
        the specified movie.
        If the user has already rated the movie, the existing rating will
        be updated. The method then calls the `get_movie_detail` function
        to retrieve the updated detailed representation of the rated movie,
        which is serialized using the `MovieDetailOutPutModelSerializer`
        and returned in the response.

        :param request: (HttpRequest): The request object containing the rating data.
        :param movie_slug: (Str): The slug of the movie for which the rating
                is being added or updated.
        :return: Response: A response containing the detailed representation
                of the rated movie, including the newly added or updated rating.

        :raises ValidationError: If the input data is not valid.
        :raises Authorization: If the user does not authorize.
        :raises DoesNotExist: If the movie does not exist.
        """

        input_serializer = self.movie_input_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            user = request.user
            existing_rating = rating_obj_existence(user=user, movie_slug=movie_slug)
            if existing_rating:
                # If the user has already rated the movie, update the existing rating
                return self.patch(request, movie_slug)

            # Check object-level permissions
            movie_release_date = get_movie_release_date(movie_slug=movie_slug)
            self.check_object_permissions(request, movie_release_date)

            rate = input_serializer.validated_data.get('rate')
            rated_movie = rate_movie(
                user=user, movie_slug=movie_slug, rate=rate
            )

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

    @extend_schema(
        request=MovieDetailRatingInPutSerializer,
        responses=MovieDetailOutPutModelSerializer
    )
    def patch(self, request, movie_slug):
        """
        PATCH method for updating a movie rating.

        This method allows users to update their rate to a movie by sending
        a PATCH request with the 'rate' field in the request body.
        The 'rate' field should be a valid integer from 1 to 10.
        The input data is validated using the `MovieDetailInPutSerializer`
        and passed to the `update_rate_movie` function to update a rating for
        the specified movie. The method then calls the `get_movie_detail`
        function to retrieve the updated detailed representation of
        the rated movie, which is serialized using
        the `MovieDetailOutPutModelSerializer` and returned in the response.


        :param request: (HttpRequest): The request object containing the rating data.
        :param movie_slug: (Str): The slug of the movie for which the rating
                is being updated.
        :return: Response: A response containing the detailed representation
                of the rated movie, including the newly updated rating.

        :raises ValidationError: If the input data is not valid.
        :raises Authorization: If the user does not authorize.
        :raises DoesNotExist: If the movie does not exist.
        """

        input_serializer = self.movie_input_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            # Check object-level permissions
            movie_release_date = get_movie_release_date(movie_slug=movie_slug)
            self.check_object_permissions(request, movie_release_date)

            user = request.user
            rate = input_serializer.validated_data.get('rate')
            movie_updated = update_movie_rating(
                user=user, movie_slug=movie_slug, updated_rate=rate
            )

        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )

        output_serializer = self.movie_output_serializer(
            movie_updated, context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        responses=MovieDetailOutPutModelSerializer
    )
    def delete(self, request, movie_slug):
        """
        DELETE method for deleting a movie rating.

        This method allows users to update their rate to a movie
        by sending a DELETE request to the movie rating endpoint with
        the `movie_slug` parameter, and passed to the `delete_rate_movie`
        function to delete a rating for the specified movie.
        It then returns a response with a 204 No Content status code,
        indicating a successful deletion.

        :param request: (HttpRequest): The request object containing the rating data.
        :param movie_slug: (Str): The slug of the movie for which the rating
                is being updated.
        :return: Response: A response with a 204 No Content status code.


        :raises Authorization: If the user does not authorize.
        :raises DoesNotExist: If the movie does not exist.
        """

        try:
            # Check object-level permissions
            movie_release_date = get_movie_release_date(movie_slug=movie_slug)
            self.check_object_permissions(request, movie_release_date)

            user = request.user
            delete_movie_rating(
                user=user, movie_slug=movie_slug
            )

        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class MovieDetailCreateReviewAPIView(ApiAuthMixin, APIView):

    """
    API view for creating a review for a movie.

    This view allows authorized users to create a review for a movie by
    sending a POST request.

    Input Serializer:
        MovieDetailReviewInputSerializer: Serializer for validating the input
        data for reviewing a movie.

    Methods:
        post (self, request, movie_slug): POST method for creating a movie review.
    """

    movie_input_serializer = MovieDetailReviewInPutSerializer
    movie_output_serializer = MovieDetailOutPutModelSerializer

    @extend_schema(
        request=MovieDetailReviewInPutSerializer,
        responses=MovieDetailOutPutModelSerializer
    )
    def post(self, request, movie_slug):

        """
        POST method for creating a movie review.

        :param request: (HttpRequest): The request object containing the review data.
        :param movie_slug: (str): The slug of the movie for which the review
                is being added.
        :return: Response: A response containing the detailed representation
                of the reviewed movie, including the newly added review.

        :raises Authorization: If the user is not authorized.
        :raises DoesNotExist: If the movie does not exist.
        """

        input_serializer = self.movie_input_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            # Extract the validated data from the serializer
            review_data = input_serializer.validated_data
            user = request.user
            reviewed_movie = review_movie(
                user=user, movie_slug=movie_slug, review_data=review_data
            )

        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )

        output_serializer = self.movie_output_serializer(
            reviewed_movie, context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class MovieDetailDeleteReviewAPIView(ApiAuthMixin, APIView):

    """
    API view for deleting a movie review.

    This view allows users to delete their review for a movie
    by sending a DELETE request.

    Methods:
        delete (self, request, movie_slug, review_slug): DELETE method for
        deleting a movie review.
    """

    movie_output_serializer = MovieDetailOutPutModelSerializer

    @extend_schema(
        responses=MovieDetailOutPutModelSerializer
    )
    def delete(self, request, movie_slug, review_slug):
        """
        DELETE method for deleting a movie review.

        This method allows users to delete their review to a movie
        by sending a DELETE request to the movie review endpoint with
        the `movie_slug` and `review_slug` parameter, and passed
        to the `delete_review_movie` function to delete a review for
        the specified movie.
        The method calls the `get_movie_detail` function with the provided
        `movie_slug` and current user to retrieve the detailed
        representation of the movie. The result is then serialized using
        the `MovieDetailOutPutModelSerializer` and returned in the response.

        :param request: (HttpRequest): The request object containing the rating data.
        :param movie_slug: (Str): The slug of the movie for which the rating
                is being updated.
        :param review_slug: (Str): The slug of the review is going to be deleted.
        :return: Response: A response containing the detailed representation
                of the rated movie, including the newly updated rating.

        :raises Authorization: If the user does not authorize.
        :raises DoesNotExist: If the movie does not exist.
        """

        try:

            user = request.user
            movie_review_deleted = delete_movie_review(
                user=user, movie_slug=movie_slug, review_slug=review_slug
            )

        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )

        output_serializer = self.movie_output_serializer(
            movie_review_deleted, context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_204_NO_CONTENT)
