from typing import Sequence, Type, TYPE_CHECKING

from importlib import import_module # noqa

from django.conf import settings # noqa

from django.contrib import auth # noqa

from rest_framework.permissions import BasePermission, IsAuthenticatedOrReadOnly
from rest_framework.authentication import BaseAuthentication

from rest_framework_simplejwt.authentication import JWTAuthentication


def get_auth_header(headers):
    """
    Extracts the authorization header from the request headers.

    :param headers: The request headers.
    :return: Tuple: The authorization type and value, or None if not present.
    """

    value = headers.get('Authorization')

    if not value:
        return None

    auth_type, auth_value = value.split()[:2]

    return auth_type, auth_value


if TYPE_CHECKING:
    # This is going to be resolved in the stub library
    # https://github.com/typeddjango/djangorestframework-stubs/
    from rest_framework.permissions import _PermissionClass

    PermissionClassesType = Sequence[_PermissionClass]
else:
    PermissionClassesType = Sequence[Type[BasePermission]]


class ApiAuthMixin:
    """
    Mixin class for authentication and permission settings for API views.

    This mixin provides a standard set of authentication and permission classes
    that can be used in API views. It includes JWTAuthentication for authentication,
    which requires valid JWT tokens for the authenticated requests, and
    IsAuthenticatedOrReadOnly for permissions, allowing read-only access for
    unauthenticated users.

    Attributes:
        authentication_classes (Sequence[Type[BaseAuthentication]]): A list of
            authentication classes to be used for the API view. By default,
            it includes JWTAuthentication.
        permission_classes (PermissionClassesType): A list of permission classes
            to be used for the API view. By default, it includes
            IsAuthenticatedOrReadOnly, allowing read-only access for
            unauthenticated users.

    Example:
        class MyAPIView(ApiAuthMixin, APIView):
            # Your API view implementation here
    """

    authentication_classes: Sequence[Type[BaseAuthentication]] = [
            JWTAuthentication,
    ]
    permission_classes: PermissionClassesType = (IsAuthenticatedOrReadOnly, )
