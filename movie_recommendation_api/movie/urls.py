from django.urls import path

from movie_recommendation_api.movie.apis.movie_list_apis import (
    MovieAPIView, MovieRecommendationAPIView
)
from movie_recommendation_api.movie.apis.movie_detail_apis import (
    MovieDetailAPIView, MovieDetailRatingAPIView,
    MovieDetailCreateReviewAPIView, MovieDetailDeleteReviewAPIView
)


app_name = 'movie'


urlpatterns = [
    path(
        '',
        MovieAPIView.as_view(),
        name="list"
    ),

    path(
        'recommendations/<int:user_id>/',
        MovieRecommendationAPIView.as_view(),
        name="recommendation"
    ),


    path(
        '<slug:movie_slug>/',
        MovieDetailAPIView.as_view(),
        name="detail"
    ),

    path(
        '<slug:movie_slug>/rating/',
        MovieDetailRatingAPIView.as_view(),
        name="rating"
    ),

    path(
        '<slug:movie_slug>/review/',
        MovieDetailCreateReviewAPIView.as_view(),
        name="create-review"
    ),
    path(
        '<slug:movie_slug>/review/<slug:review_slug>/',
        MovieDetailDeleteReviewAPIView.as_view(),
        name="delete-review"
        ),
]
