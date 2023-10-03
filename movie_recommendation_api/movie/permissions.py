from datetime import date

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.request import Request

from movie_recommendation_api.movie.models import Movie
from movie_recommendation_api.users.models import BaseUser


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

    def has_object_permission(
            self, request: Request, view: APIView, movie: Movie
    ) -> bool:

        """
        Checks if the user has permission to rate the movie.

        This method retrieves the movie object and checks if the current date is
        greater than or equal to the release date of the movie.
        If it is, it returns `True` to indicate that the user has permission
        to rate the movie. Otherwise, it returns `False` to indicate that
        the user does not have permission to rate the movie.

        :param request: The request object.
        :param view: The view object.
        :param movie: The movie being accessed.

        :return: `True` if the user has permission to rate the movie,
        `False` otherwise.
        """

        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        release_date = movie.release_date
        current_date = date.today()

        return current_date >= release_date


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
            self, request: Request, view: APIView, user: BaseUser
    ) -> bool:

        """
        Check if the user has permission to access the user profile.

        Users are granted read-only access (GET, HEAD, OPTIONS) to all profiles.
        However, updates are only allowed if the requesting user is the owner
        of the profile.

        :param request: The incoming HTTP request.
        :param view: The view requesting access to the profile.
        :param user: The user being accessed.

        :return: True if the user has permission, False otherwise.
        """

        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow updates only if the requesting user is the owner of the profile.
        return user == request.user
