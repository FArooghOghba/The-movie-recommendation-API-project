from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile
from .validators import number_validator, special_char_validator, letter_validator


class InputRegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration input.

    This serializer handles the validation and
    serialization of user registration data,
    including email, bio, password, and confirm_password fields.
    """

    email = serializers.EmailField(max_length=150)
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator(), MinLengthValidator(5)]
    )
    bio = serializers.CharField(max_length=1000, required=False)
    password = serializers.CharField(
        max_length=255,
        write_only=True,
        style={"input_type": "password"},
        validators=[
            number_validator,
            letter_validator,
            special_char_validator,
            MinLengthValidator(limit_value=10)
        ]
    )
    confirm_password = serializers.CharField(
        max_length=255,
        write_only=True,
        style={"input_type": "password"}
    )

    def validate_email(self, email: str) -> str | ValueError:
        """
        Validate the uniqueness of the email.

        This method is called during the validation
        phase to check if the provided email is unique
        in the database. If an existing user with the same
        email is found, a validation error is raised.

        :param email: (str): The email to validate.
        :return: str: The validated email.
        :Raises: serializers.ValidationError: If the email is already taken.
        """
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError(_("email Already Taken"))
        return email

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

    def validate(self, data: dict) -> dict | ValueError:
        """
        Validate the password and confirm_password fields.

        This method is called during the validation phase
        to perform additional validation on the password
        and confirm_password fields. It checks if both fields
        are filled, and if they match each other. If any
        validation error occurs, an exception is raised.

        :param data: (dict): The input data to validate.
        :return: dict: The validated data.
        :Raises: serializers.ValidationError: If password and confirm_password
         validations fail.
        """

        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not username:
            raise serializers.ValidationError(
                _("Please provide a username.")
            )

        if not password or not confirm_password:
            raise serializers.ValidationError(
                _("Please fill password and confirm password.")
            )

        if not password == confirm_password:
            raise serializers.ValidationError(
                _("confirm password is not equal to password.")
            )

        return data


class OutPutRegisterModelSerializer(serializers.ModelSerializer):

    token = serializers.SerializerMethodField("get_token")

    class Meta:
        model = get_user_model()
        fields = (
            "email", "username", "token", "created_at", "updated_at"
        )

    def get_token(self, user):
        data = dict()
        token_class = RefreshToken

        refresh_token = token_class.for_user(user)

        data["refresh_token"] = str(refresh_token)
        data["access_token"] = str(refresh_token.access_token)

        return data


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

    favorite_genres = serializers.SerializerMethodField()
    watchlist = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "user", "first_name", "last_name",
            "picture", "bio", "created_at",
            "favorite_genres", "watchlist",
            "ratings", "reviews"
        )

    def get_favorite_genres(self, obj):

        """
        Retrieve and format the user's favorite genres.

        :param: obj (Profile): The user's profile object.

        :return: list[str]: A list of favorite genres' titles.
        """

        return [genre.title for genre in obj.favorite_genres.all()]

    def get_watchlist(self, obj) -> list[dict]:

        """
        Retrieve and format the user's watchlist.

        :param: obj (Profile): The user's profile object.

        :return: list[dict]: A list of movie details in the user's watchlist.
        """

        watchlist_queryset = obj.watchlist.order_by('created_at')

        watchlist = []

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
            watchlist.append(movie_detail)

        return watchlist

    def get_ratings(self, obj) -> list[dict]:
        """
        Retrieve and format the user's movie ratings.

        :param: obj (Profile): The user's profile object.

        :return: list[dict]: A list of movie ratings and details.
        """

        rating_queryset = obj.ratings.order_by('created_at')

        ratings = []

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
            ratings.append(rating_detail)

        return ratings

    def get_reviews(self, obj) -> list[dict]:
        """
        Retrieve and format the user's movie reviews.

        :param: obj (Profile): The user's profile object.

        :return: list[dict]: A list of movie reviews and details.
        """

        review_queryset = obj.reviews.order_by('created_at')

        reviews = []

        for review_obj in review_queryset:
            review_detail = {
                'movie_title': review_obj.movie.title,
                'movie_poster': review_obj.movie.poster.url,
                'movie_release_date': review_obj.movie.release_date,
                'content': review_obj.content,
                'datetime': review_obj.created_at
            }
            reviews.append(review_detail)

        return reviews
