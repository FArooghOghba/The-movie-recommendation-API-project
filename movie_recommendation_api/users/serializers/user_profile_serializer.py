from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from movie_recommendation_api.users.models import Profile


class InPutProfileSerializer(serializers.Serializer):

    """
    Serializer for updating user profile information.

    This serializer is used for updating user profile information
    using the PATCH request. It includes fields such as username,
    first name, last name, bio, watchlist, and favorite_genres.
    Each field is optional.

    Attributes:
        username (serializers.CharField): The username field for the user.
            It is optional and validated for uniqueness.
        first_name (serializers.CharField): The first name field for the user.
            It is optional.
        last_name (serializers.CharField): The last name field for the user.
            It is optional.
        picture (serializers.ImageField): The picture field for the user.
            It is optional.
        bio (serializers.CharField): The biography field for the user.
            It is optional.
        watchlist (serializers.CharField): The watchlist field for the user.
            It is optional.
        favorite genres (serializers.CharField): The favorite genres field
            for the user. It is optional.

    Methods:
        validate_username(username): Validate the uniqueness of the username.
    """

    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator(), MinLengthValidator(5)],
        required=False,
    )
    first_name = serializers.CharField(
        max_length=256, allow_blank=True, required=False
    )
    last_name = serializers.CharField(
        max_length=256, allow_blank=True, required=False
    )
    picture = serializers.ImageField(allow_null=True, required=False)
    bio = serializers.CharField(max_length=512, allow_blank=True, required=False)
    watchlist = serializers.CharField(max_length=256, required=False)
    favorite_genres = serializers.CharField(max_length=256, required=False)

    def validate_username(self, username: str) -> str | ValueError:
        """
        Validate the uniqueness of the username.

        This method is called during the validation
        phase to check if the provided username is
        unique in the database. If an existing user
        with the same username is found, a validation
        error is raised.

        :param username: (str): The username to validate.
        :return: str: The validated username.
        :Raises: serializers.ValidationError: If the username is already taken.
        """

        if get_user_model().objects.filter(username=username).exists():
            raise serializers.ValidationError(_("username Already Taken"))
        return username


class OutPutProfileModelSerializer(serializers.ModelSerializer):
    """
    Serializer for the user's profile data.

    This serializer is used to transform a user's profile data into a format suitable
    for API responses. It includes information such as favorite genres, watchlist,
    ratings, and reviews.

    Attributes:
        favorite_genres (serializers.SerializerMethodField): A method field
            to retrieve and format the user's favorite genres.
        watchlist (serializers.SerializerMethodField): A method field to retrieve and
            format the user's watchlist of movies.
        ratings (serializers.SerializerMethodField): A method field to retrieve and
            format the user's movie ratings.
        reviews (serializers.SerializerMethodField): A method field to retrieve and
            format the user's movie reviews.

    Meta:
        model (Profile): The model that this serializer is based on.
        fields (tuple): The fields to be included in the serialized representation.

    Methods:
        get_favorite_genres(obj): Retrieve and format the user's favorite genres.
        get_watchlist(obj): Retrieve and format the user's watchlist.
        get_ratings(obj): Retrieve and format the user's movie ratings.
        get_reviews(obj): Retrieve and format the user's movie reviews.
    """

    username = serializers.ReadOnlyField(source='user.username')
    favorite_genres = serializers.SerializerMethodField()
    watchlist = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "username", "first_name", "last_name",
            "picture", "bio", "created_at",
            "favorite_genres", "watchlist",
            "ratings", "reviews"
        )

    def get_favorite_genres(self, obj) -> dict[str, list[str]]:

        """
        Retrieve and format the user's favorite genres their count.

        :param: obj (Profile): The user's profile object.

        :return: list[str]: A list of favorite genres' titles.
        """

        favorite_genres = {
            'genres_count': obj.favorite_genres_count,
            'genres': [genre.title for genre in obj.favorite_genres.all()]
        }

        return favorite_genres

    def get_watchlist(self, obj) -> dict[str, list[dict[str, Any]]]:

        """
        Retrieve and format the user's watchlist and movies count.

        :param: obj (Profile): The user's profile object.

        :return: list[dict]: A list of movie details in the user's watchlist.
        """

        watchlist_queryset = obj.watchlist.order_by('-created_at')

        watchlist = {}
        movies = []

        for movie_obj in watchlist_queryset:
            movie_detail = {
                'movie_title': movie_obj.title,
                'movie_poster': movie_obj.poster.url,
                'movie_release_date': movie_obj.release_date,
                'movie_runtime': movie_obj.runtime,
                # 'movie_genres': movie_obj.genres,
                # 'movie_rate': movie_obj.rate,
                # 'movie_cast_crew': movie_obj.cast_crew,
                'movie_synopsis': movie_obj.synopsis,
            }
            movies.append(movie_detail)

        watchlist['movies'] = movies
        watchlist['watchlist_count'] = obj.watchlist_count

        return watchlist

    def get_ratings(self, obj) -> dict[str, list[dict[str, Any]]]:
        """
        Retrieve and format the user's movie ratings and ratings count.

        :param: obj (Profile): The user's profile object.

        :return: list[dict]: A list of movie ratings and details.
        """

        rating_queryset = obj.ratings.order_by('-created_at')

        ratings = {}
        ratings_detail = []

        for rating_obj in rating_queryset:
            rating_detail = {
                'movie_title': rating_obj.movie.title,
                'movie_poster': rating_obj.movie.poster.url,
                'movie_release_date': rating_obj.movie.release_date,
                'movie_runtime': rating_obj.movie.runtime,
                'rating_created_at': rating_obj.created_at,
                # 'movie_rate': rating_obj.movie.rate,
                'user_rating': rating_obj.rating,
                'movie_synopsis': rating_obj.movie.synopsis,
                # 'movie_cast_crew': movie_obj.cast_crew,
                # 'ratings_count': rating_obj.movie.ratings_count,
            }
            ratings_detail.append(rating_detail)

        ratings['ratings_detail'] = ratings_detail
        ratings['ratings_count'] = obj.ratings_count

        return ratings

    def get_reviews(self, obj) -> dict[str, list[dict[str, Any]]]:

        """
        Retrieve and format the user's movie reviews and reviews count.

        :param: obj (Profile): The user's profile object.

        :return: list[dict]: A list of movie reviews and details.
        """

        review_queryset = obj.reviews.order_by('-created_at')

        reviews = {}
        reviews_detail = []

        for review_obj in review_queryset:
            review_detail = {
                'movie_title': review_obj.movie.title,
                'movie_poster': review_obj.movie.poster.url,
                'movie_release_date': review_obj.movie.release_date,
                'title': review_obj.title,
                'content': review_obj.content,
                'datetime': review_obj.created_at
            }
            reviews_detail.append(review_detail)

        reviews['reviews_detail'] = reviews_detail
        reviews['reviews_count'] = obj.reviews_count

        return reviews
