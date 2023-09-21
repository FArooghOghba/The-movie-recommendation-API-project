from datetime import date

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response

from movie_recommendation_api.api.exception_handlers import handle_exceptions
from movie_recommendation_api.users.models import Profile


class CanRateAfterReleaseDate(permissions.BasePermission):
    """
    Permission class for checking if a movie can be rated.

    This permission class checks if the current date is greater than or equal to
    the release date of the movie being rated. If it is, the permission check passes
    and the user is allowed to rate the movie. Otherwise, the permission check fails
    and the user is not allowed to rate the movie.

    Methods:
        has_permission(self, request, view): Checks if the user has permission to
        rate the movie.
    """

    def has_permission(self, request: Request, view: APIView) -> bool | Response:
        """
        Checks if the user has permission to rate the movie.

        This method retrieves the movie object from the view using the `get_object`
        method and checks if the current date is greater than or equal to the release
        date of the movie. If it is, it returns `True` to indicate that the user has
        permission to rate the movie. Otherwise, it returns `False` to indicate that
        the user does not have permission to rate the movie.

        :param request: The request object.
        :param view: The view object.
        :return: `True` if the user has permission to rate the movie,
        `False` otherwise.
        """

        try:
            movie = view.get_object()
            release_date = movie.release_date
            current_date = date.today()

            return current_date >= release_date

        except Exception as exc:
            exception_response = handle_exceptions(
                exc=exc, ctx={"request": request, "view": self}
            )
            return Response(
                data=exception_response.data,
                status=exception_response.status_code,
            )


class IsOwnerProfilePermissionOrReadOnly(permissions.BasePermission):
    """
    Custom permission class for user profile access.

    This permission class restricts access to user profiles, allowing read-only
    access for unauthenticated users and full access (including updates) only to
    the owner of the profile.

    Methods:
        has_object_permission(request, view, profile): Determine if the user has
        permission to access the given user profile.

    """

    def has_object_permission(
            self, request: Request, view: APIView, profile: Profile
    ) -> bool:

        """
        Check if the user has permission to access the user profile.

        Users are granted read-only access (GET, HEAD, OPTIONS) to all profiles.
        However, updates are only allowed if the requesting user is the owner
        of the profile.

        :param request: The incoming HTTP request.
        :param view: The view requesting access to the profile.
        :param profile: The user profile being accessed.

        :return: True if the user has permission, False otherwise.
        """

        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow updates only if the requesting user is the owner of the profile.
        return profile.user == request.user
