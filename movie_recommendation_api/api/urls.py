from django.urls import path, include


app_name = 'api'


urlpatterns = [
    path('users/', include(('movie_recommendation_api.users.urls', 'users'))),
    path('movie/', include(('movie_recommendation_api.movie.urls', 'movie'))),
]
