from django.urls import path
from .apis import RegisterAPIView, ProfileAPIView


app_name = 'users'


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name="register"),
    path('profile/<str:username>/', ProfileAPIView.as_view(), name="profile"),
]
