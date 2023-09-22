from typing import Any, Sequence

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from movie_recommendation_api.api.exception_handlers import handle_exceptions
from movie_recommendation_api.api.mixins import ApiAuthMixin
from movie_recommendation_api.movie.permissions import (
    IsOwnerProfilePermissionOrReadOnly
)
from movie_recommendation_api.users.serializers.user_register_serializers import (
    InputRegisterSerializer, OutPutRegisterModelSerializer
)
from movie_recommendation_api.users.serializers.user_profile_serializer import (
    InPutProfileSerializer, OutPutProfileModelSerializer
)
from movie_recommendation_api.users.services import register, update_profile
from movie_recommendation_api.users.selectors import get_profile

from drf_spectacular.utils import extend_schema


class RegisterAPIView(APIView):

    input_serializer = InputRegisterSerializer
    output_serializer = OutPutRegisterModelSerializer

    @extend_schema(
        request=InputRegisterSerializer, responses=OutPutRegisterModelSerializer
    )
    def post(self, request):

        serializer = self.input_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = register(
                email=serializer.validated_data.get("email"),
                username=serializer.validated_data.get("username"),
                bio=serializer.validated_data.get("bio"),
                password=serializer.validated_data.get("password"),
            )
        except Exception as ex:
            return Response(
                data=f"Database Error {ex}",
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            self.output_serializer(user, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )


class ProfileAPIView(ApiAuthMixin, APIView):
    """
    API endpoint for retrieving user profiles.

    This view allows users to retrieve their own profiles or view other
    users' profiles by specifying the target user's username in the URL.
    It returns information such as the user's first name, last name
    profile picture, biography, favorite genres, watchlist, ratings,
    and reviews.

    Attributes:
        input_serializer (Serializer): The serializer class used for input data.
        output_serializer (Serializer): The serializer class used for formatting the
        output data.
    """

    input_serializer = InPutProfileSerializer
    output_serializer = OutPutProfileModelSerializer

    def get_permissions(self) -> Sequence[Any] | Any:

        """
        Retrieves the permission classes for the current request.

        This method overrides the default `get_permissions` method to add
        custom permissions for the `patch` method. If the current request method
        is `PATCH`, it adds an instance of the `IsOwnerProfilePermissionOrReadOnly`
        permission class to the list of permission classes.

        :return: A list of permission classes to be used for the current request.
        """

        permissions = super().get_permissions()

        if self.request.method == 'PATCH':
            permissions.append(IsOwnerProfilePermissionOrReadOnly())

        return permissions

    @extend_schema(responses=OutPutProfileModelSerializer)
    def get(self, request, username):

        """
        Get user profile information.

        :param: request (Request): The HTTP request object.
        :param: username (str): The username of the target user's profile
        to retrieve.

        :return:
           Response: The HTTP response containing the user profile data
           or an error message.
        """

        if not username:
            username = request.user.username

        try:

            user_profile = get_profile(username=username)

        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )

        output_serializer = self.output_serializer(
            user_profile, context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=InPutProfileSerializer, responses=OutPutProfileModelSerializer
    )
    def patch(self, request, username):

        """
        Update user profile information.

        :param: request (Request): The HTTP request object.
        :param: username (str): The username of the target user's profile to update.

        :return: Response: The HTTP response containing the updated user profile data
        or an error message.
        """

        serializer = self.input_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:

            # Extract the validated data from the serializer
            updated_fields = serializer.validated_data

            user_profile = update_profile(
                username=username,
                updated_fields=updated_fields,
            )

            # Check object-level permissions
            self.check_object_permissions(request, user_profile)

        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )

        output_serializer = self.output_serializer(
            user_profile, context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_202_ACCEPTED)
