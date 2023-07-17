from collections import OrderedDict

from typing import Type

from django.db.models import QuerySet

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView


def get_paginated_response(
    *, pagination_class: Type[LimitOffsetPagination], serializer_class,
        queryset: QuerySet, request, view: APIView
) -> Response:

    """
    Return a paginated response for a queryset using the specified
    pagination and serializer classes.

    :param pagination_class: (type): The pagination class to use.
    :param serializer_class: (type): The serializer class to use.
    :param queryset: (QuerySet): The queryset to paginate.
    :param request: The request object.
    :param view: (APIView): The API view.
    :return: Response: The paginated response.
    """

    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return Response(data=serializer.data)


def get_paginated_response_context(
    *, pagination_class: Type[LimitOffsetPagination], serializer_class,
    queryset: QuerySet, request, view: APIView
):

    """
    Return a paginated response with request context for a queryset using
    the specified pagination and serializer classes.

    :param pagination_class: (type): The pagination class to use.
    :param serializer_class: (type): The serializer class to use.
    :param queryset: (QuerySet): The queryset to paginate.
    :param request: The request object.
    :param view: (APIView): The API view.
    :return: Response: The paginated response.
    """

    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True, context={'request': request})

    return Response(data=serializer.data)


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Custom pagination class for limit-offset pagination.

    Attributes:
        default_limit (int): The default number of items to include in a page.
        max_limit (int): The maximum number of items to include in a page.

    Methods:
        get_paginated_data(self, data): Get the paginated data with
                                        additional metadata.
        get_paginated_response(self, data): Get the paginated response with
                                            additional metadata.
    """

    default_limit = 10
    max_limit = 50

    def get_paginated_data(self, data):
        """
        Get the paginated data with additional metadata.

        :param data: The serialized paginated data.
        :return: OrderedDict: The paginated data with metadata.
        """

        return OrderedDict([
            ('limit', self.limit),
            ('offset', self.offset),
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])

    def get_paginated_response(self, data):
        """
        Get the paginated response with additional metadata.

        We redefine this method in order to return `limit` and `offset`.
        This is used by the frontend to construct the pagination itself.

        :param data: The serialized paginated data.
        :return: Response: The paginated response with metadata.
        """
        return Response(OrderedDict([
            ('limit', self.limit),
            ('offset', self.offset),
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
