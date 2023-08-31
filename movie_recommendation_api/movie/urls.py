from django.urls import path

from movie_recommendation_api.movie.apis.movie_list_apis import MovieAPIView
from movie_recommendation_api.movie.apis.movie_detail_apis import (
    MovieDetailAPIView, MovieDetailRatingAPIView
)


app_name = 'movie'


urlpatterns = [
    path(
        '',
        MovieAPIView.as_view(),
        name="list"
    ),

    path(
        '<slug:movie_slug>/',
        MovieDetailAPIView.as_view(),
        name="detail"
    ),

    path(
        'rating/<slug:movie_slug>/',
        MovieDetailRatingAPIView.as_view(),
        name="rating"
    ),
]
