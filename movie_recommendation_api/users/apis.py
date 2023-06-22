from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from movie_recommendation_api.api.mixins import ApiAuthMixin
from movie_recommendation_api.users.serializers import (
    InputRegisterSerializer, OutPutRegisterModelSerializer
)
from movie_recommendation_api.users.services import register
# from movie_recommendation_api.users.selectors import get_profile

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
                f"Database Error {ex}",
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            self.output_serializer(user, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )


# class ProfileApi(ApiAuthMixin, APIView):
#
#     class OutPutSerializer(serializers.ModelSerializer):
#         class Meta:
#             model = Profile
#             fields = (
#               "bio", "posts_count", "subscriber_count", "subscription_count"
#             )
#
#     @extend_schema(responses=OutPutSerializer)
#     def get(self, request):
#         query = get_profile(user=request.user)
#         return Response(self.OutPutSerializer(
#           query, context={"request": request}).data
#         )
