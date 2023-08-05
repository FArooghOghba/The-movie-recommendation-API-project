from rest_framework.exceptions import APIException
from rest_framework import status


class ApplicationError(Exception):
    """
    Custom exception class for representing application-level errors.

    This class extends the built-in `Exception` class and adds
    'extra' attribute for storing additional information about the error.

    :param message: The error message.
    :param extra: An optional dictionary containing additional information
    about the error.
    """

    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}


class LimitExceededException(APIException):
    """
    Custom exception class for representing errors when a limit is exceeded.

    This class extends the DRF `APIException` class and sets the default status code
    and error message for the exception.

    :ivar status_code: The HTTP status code to return when this exception is raised.
    :ivar default_detail: The default error message to return when this
    exception is raised.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'You cannot add more than limit.'
