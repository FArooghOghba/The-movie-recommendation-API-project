import numpy as np

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from movie_recommendation_api.movie.models import Movie, MovieRecommendationModel
from movie_recommendation_api.movie.selectors.movie_dependencies import (
    calculate_and_annotate_movie_queryset_rates
)
from movie_recommendation_api.users.models import Profile


def get_movie_recommendation_list(*, user_id: int) -> QuerySet[Movie]:

    """
    Get a list of recommended movies for a user.

    Args:
        user_id (int): The user's ID.

    Returns:
        QuerySet[Movie]: A queryset of recommended movies.
    """

    # Assuming you have a UserProfile model (replace with your actual model)
    user_profile = Profile.objects.get(user=user_id)

    # Get user interactions (ratings, watchlist, etc.)
    user_ratings = user_profile.ratings.all()

    # Convert Rating objects to tuples
    user_ratings = [
        (rates.user_id, rates.movie_id, rates.rating) for rates in user_ratings
    ]

    # Fetch all movies (you may filter this query based on your requirements)
    get_movies = Movie.objects.all()
    movie_ids = [movie.id for movie in get_movies]

    get_users = get_user_model().objects.all()
    user_ids = [user.id for user in get_users]

    # Create and configure the recommendation model
    recommendation_model = MovieRecommendationModel(loss='warp', epochs=10)

    # Prepare the data
    interactions = recommendation_model.prepare_data(
        all_movies=movie_ids, all_users=user_ids, user_ratings=user_ratings
    )

    # Train the model
    recommendation_model.train_model(interactions)

    # Generate recommendations
    movie_ids_length = len(movie_ids)
    recommended_movie_ids = recommendation_model.recommend(
        user_ids=[user_id] * movie_ids_length, item_ids=np.arange(movie_ids_length)
    )

    recommended_movies = (
        Movie.objects
        .prefetch_related('genre', 'cast_crew')
        .defer('runtime', 'created_at', 'updated_at')
        .filter(id__in=recommended_movie_ids)
    )

    # recommended_movies = (
    #     recommended_movies
    #     .annotate(avg_rating=Avg('movie_ratings__rating'))
    # )

    recommended_movies = calculate_and_annotate_movie_queryset_rates(
        movies_queryset=recommended_movies
    )

    return recommended_movies
