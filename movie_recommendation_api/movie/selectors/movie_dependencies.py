from datetime import date

from django.conf.global_settings import AUTH_USER_MODEL
from django.db.models import Count, Prefetch, QuerySet
from django.db.models.aggregates import Avg

from movie_recommendation_api.movie.models import (
    Genre, Movie, Rating, Review, Role
)


def get_movie_obj(*, movie_slug: str) -> Movie:
    """
    Retrieves a movie object based on the provided movie slug.

    This function takes a movie slug as an input parameter and retrieves the
    corresponding movie object from the database using the Django ORM.

    :param movie_slug: The slug of the movie to retrieve.
    :return: The retrieved movie object.
    """

    movie_obj = Movie.objects.get(slug=movie_slug)
    return movie_obj


def get_movie(*, movie_slug: str) -> Movie:

    """
    Retrieves detailed information about a specific movie by its slug.

    This function fetches a movie along with associated genres, cast, crew,
    and reviews based on its slug.

    :param movie_slug: (str): The slug of the movie to retrieve.
    :return: Movie: The detailed representation of the movie.
    """

    # Create a Prefetch object that fetches roles for a specific movie
    cast_crew = Prefetch(
        lookup='cast_crew',
        queryset=Role.objects
        .filter(movie__slug=movie_slug)
        .select_related('cast_crew')
        .prefetch_related('careers'),
        to_attr='cast_crew_roles'
    )

    # Create a Prefetch object that fetches reviews along with their related user
    reviews = Prefetch(
        lookup='reviews',
        queryset=Review.objects.select_related('user'),
        to_attr='movie_reviews'
    )

    # Fetch the movie with the associated genres, cast_crews, and their roles
    movie = (
        Movie.objects
        .prefetch_related('genre', reviews, cast_crew)
        .get(slug=movie_slug)
    )

    return movie


def aggregate_movie_reviews_count(*, movie: Movie) -> Movie:

    """
    Aggregates the count of reviews for a movie.

    This function annotates the count of reviews for the provided movie object.

    :param movie: (Movie): The movie object.
    :return: Movie: The movie object with annotated review count.
    """

    # Annotates the count of reviews for the movie
    reviews_data = movie.reviews.aggregate(
        reviews_count=Count('id')
    )

    movie.reviews_count = reviews_data['reviews_count']

    return movie


def calculate_and_aggregate_movie_rate(*, movie: Movie) -> Movie:

    """
    Calculates and annotates the average rating and ratings count for a movie.

    This function calculates the average rating and annotates the count of ratings
    for the provided movie object.

    :param movie: (Movie): The movie object.
    :return: Movie: The movie object with calculated ratings.
    """

    # Calculate the average rating for the movie
    # Annotates the count of ratings for the movie
    ratings_data = movie.movie_ratings.aggregate(
        avg_rating=Avg('rating'),
        ratings_count=Count('id')
    )

    movie.avg_rating = ratings_data['avg_rating']
    movie.ratings_count = ratings_data['ratings_count']

    return movie


def calculate_and_annotate_movie_queryset_rates(
    *, movies_queryset: QuerySet[Movie]
) -> QuerySet[Movie]:

    """
    Annotates the average rating for a queryset of movies.

    This function annotates the average rating for the provided queryset of movies.

    :param movies_queryset: (QuerySet[Movie]): Queryset of movies.
    :return: QuerySet[Movie]: Queryset of movies with annotated ratings.
    """

    movies_queryset = movies_queryset \
        .annotate(avg_rating=Avg('movie_ratings__rating'))

    return movies_queryset


def rating_obj_existence(*, movie_slug: str, user: AUTH_USER_MODEL) -> bool:

    """
    Check the existence of a rating object for a user and a movie.

    This function checks whether a rating object exists in the database
    based on the provided movie slug and user. It uses the Django ORM to query
    the database for the existence of a rating object.

    :param movie_slug: (str) The slug of the movie to check.
    :param user: (User) The authenticated user.
    :return: (bool) True if a rating object exists, False otherwise.
    """

    rating_obj = Rating.objects.filter(
        user=user,
        movie__slug=movie_slug
    )

    return rating_obj.exists()


def get_movie_release_date(*, movie_slug: str) -> Movie:

    """
    Retrieves the release date of a movie based on the provided movie slug.

    This function takes a movie slug as an input parameter and retrieves the
    corresponding movie object from the database using the Django ORM. It then
    extracts and returns the release date of the movie.

    :param movie_slug: The slug of the movie for which to retrieve the release date.
    :return: The release date of the movie as a 'date' object.
    """

    movie = Movie.objects.only('release_date').get(slug=movie_slug)
    release_date = movie.release_date
    return release_date


def check_movie_release_for_user_rating(
    *, movie: Movie, user: AUTH_USER_MODEL
) -> Movie:

    """
    Checks movie release status and retrieves the user's rating if authenticated.

    This function checks if the movie is released and gets the authenticated
    user's rating for the movie if available.

    :param movie: (Movie): The movie object.
    :param user: (User): The authenticated user.
    :return: Movie: The movie object with updated user rating status.
    """

    # Check if the movie is released
    release_date = movie.release_date
    current_date = date.today()

    if movie.release_date and current_date < release_date:
        movie.user_rating = "Movie has not been released yet."

    # If a user is authenticated, get their rating for the movie
    elif user and user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=user, movie=movie)
            movie.user_rating = user_rating.rating
        except Rating.DoesNotExist:
            # If the user has not rated the movie yet, display a message
            movie.user_rating = "You have not rated this movie yet."

    else:
        # If the user is not authenticated, display a message
        movie.user_rating = "Please login to rate this movie."

    return movie


def get_genre_obj(*, genre_slug: str) -> Genre:
    """
    Retrieves a genre object based on the provided genre slug.

    This function takes a genre slug as an input parameter and retrieves the
    corresponding genre object from the database using the Django ORM.

    :param genre_slug: The slug of the genre to retrieve.
    :return: The retrieved genre object.
    """

    genre_obj = Genre.objects.get(slug=genre_slug)
    return genre_obj


def get_rating_obj(*, user: AUTH_USER_MODEL, movie: Movie) -> Rating:

    rating_obj = Rating.objects.get(
        user=user, movie=movie
    )
    return rating_obj
