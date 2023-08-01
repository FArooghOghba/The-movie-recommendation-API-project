from django.urls import path, include


app_name = 'api'


urlpatterns = [
    path(
        route='users/',
        view=include(('movie_recommendation_api.users.urls', 'users'))
    ),
    path(
        route='movie/',
        view=include(('movie_recommendation_api.movie.urls', 'movie'))
    ),
    path(
        route='auth/',
        view=include(('movie_recommendation_api.authentication.urls', 'auth'))
    ),
]
