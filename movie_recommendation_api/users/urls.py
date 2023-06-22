from django.urls import path
from .apis import RegisterAPIView


app_name = 'users'


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name="register"),
    # path('profile/', ProfileApi.as_view(),name="profile"),
]
