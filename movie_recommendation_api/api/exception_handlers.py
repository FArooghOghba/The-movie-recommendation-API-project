from typing import Any, Dict, Optional

from django.core.exceptions import (
    ObjectDoesNotExist, ValidationError as DjangoValidationError, PermissionDenied
)
from django.http import Http404

from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import exceptions
from rest_framework.serializers import as_serializer_error

from movie_recommendation_api.core.exceptions import LimitExceededException


def handle_exceptions(
    exc: Exception, ctx: Dict[str, Any]
) -> Optional[Response]:

    """
    Custom exception handler function for handling exceptions in API views.

    This function takes an exception instance `exc` and a context dictionary `ctx`
    as arguments and returns an appropriate response based on the type of exception
    that was raised.

    The function checks the type of the exception using `isinstance` and creates an
    appropriate DRF exception instance with a custom error message for each type of
    exception. These DRF exception instances are then passed to the default DRF
    exception handler function `exception_handler`, which generates a response object
    with the appropriate status code and error message.

    :param exc: The exception instance to handle.
    :param ctx: A dictionary containing context information
    about the current request and view.
    :return: A response object containing an appropriate error
    message and status code.
    """

    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, ObjectDoesNotExist):
        exc = exceptions.NotFound("Movie not found.")

    if isinstance(exc, NotAuthenticated):
        exc = exceptions.NotAuthenticated("You are not authenticated.")

    if isinstance(exc, LimitExceededException):
        exc = exceptions.ValidationError(f"Filter Error - {exc}")

    if isinstance(exc, ValueError):
        exc = exceptions.ValidationError(f"Validation Error - {exc}")

    response = exception_handler(exc, ctx)

    if isinstance(exc.detail, (list, dict)):
        response.data = {
            "detail": response.data
        }

    return response


def drf_default_with_modifications_exception_handler(
    exc: Exception, ctx: Dict[str, Any]
) -> Optional[Response]:

    """
    Custom DRF exception handler function with additional modifications.

    This function extends the default DRF exception handler function by adding
    additional checks for Django-specific exceptions such as `DjangoValidationError`,
    `Http404`, and `PermissionDenied`. When one of these exceptions is raised,
    the function creates an appropriate DRF exception instance with a custom error
    message and passes it to the default DRF exception handler.

    :param exc: The exception instance to handle.
    :param ctx: A dictionary containing context information about
    the current request and view.
    :return: A response object containing an appropriate error message
    and status code.
    """

    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, ctx)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        return response

    if isinstance(exc.detail, (list, dict)):
        response.data = {
            "detail": response.data
        }

    return response


# def hacksoft_proposed_exception_handler(exc, ctx):
#     """
#     {
#         "message": "Error message",
#         "extra": {}
#     }
#     """
#     if isinstance(exc, DjangoValidationError):
#         exc = exceptions.ValidationError(as_serializer_error(exc))
#
#     if isinstance(exc, Http404):
#         exc = exceptions.NotFound()
#
#     if isinstance(exc, PermissionDenied):
#         exc = exceptions.PermissionDenied()
#
#     response = exception_handler(exc, ctx)
#
#     # If unexpected error occurs (server error, etc.)
#     if response is None:
#         if isinstance(exc, ApplicationError):
#             data = {
#                 "message": exc.message,
#                 "extra": exc.extra
#             }
#             return Response(data, status=400)
#
#         return response
#
#     if isinstance(exc.detail, (list, dict)):
#         response.data = {
#             "detail": response.data
#         }
#
#     if isinstance(exc, exceptions.ValidationError):
#         response.data["message"] = "Validation error"
#         response.data["extra"] = {
#             "fields": response.data["detail"]
#         }
#     else:
#         response.data["message"] = response.data["detail"]
#         response.data["extra"] = {}
#
#     del response.data["detail"]
#
#     return response
