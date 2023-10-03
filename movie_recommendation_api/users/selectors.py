from django.db.models import Count, Prefetch

from .models import BaseUser, Profile
from ..movie.models import Rating, Review


def get_user_obj(*, username: str) -> BaseUser:
    """
    Retrieves a user object based on the provided username.

    This function takes a username as an input parameter and retrieves the
    corresponding user object from the database using the Django ORM.

    :param username: The username of the user to retrieve.
    :return: The retrieved user object.
    """

    user_obj = BaseUser.objects.get(username=username)
    return user_obj


def get_profile(*, username: str) -> Profile:

    """
    Retrieve a user's profile by their username.

    This function fetches a user's profile along with related data such as favorite
    genres, watchlist, ratings, and reviews. It optimizes database queries using
    Prefetch to minimize database hits and improve performance.

    :param: username (str): The username of the user whose profile is to be
    retrieved.

    :return: Profile: The user's profile instance with related data.
    """

    # Use Prefetch to optimize the fetching of related movie data for ratings
    ratings_prefetch = Prefetch(
        lookup='ratings', queryset=Rating.objects.select_related('movie')
    )

    # Use Prefetch to optimize the fetching of related movie data for reviews
    reviews_prefetch = Prefetch(
        lookup='reviews', queryset=Review.objects.select_related('movie')
    )

    # Retrieve the user's profile along with related data
    user_profile = (
        Profile.objects
        .select_related('user')
        .prefetch_related(
            'favorite_genres',
            'watchlist',
            ratings_prefetch,
            reviews_prefetch,
        )
        .annotate(
            watchlist_count=Count('watchlist', distinct=True),
            favorite_genres_count=Count('favorite_genres', distinct=True),
            ratings_count=Count('ratings', distinct=True),
            reviews_count=Count('reviews', distinct=True)
        )
        .get(user__username=username)
    )

    return user_profile
