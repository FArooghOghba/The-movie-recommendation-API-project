from rest_framework import serializers

from movie_recommendation_api.movie.models import Movie
from movie_recommendation_api.movie.serializers.movie_list_serializers import (
    MovieOutPutModelSerializer
)


class MovieDetailRatingInPutSerializer(serializers.Serializer):

    """
    Serializer for validating and deserializing the input data for rating a movie.

    This serializer defines the input fields required for rating a movie, including
    the 'rate' field. The 'rate' field should be a valid integer from 1 to 10,
    representing the user's rating for the movie.

    Fields:
        rate (serializers.ChoiceField): The field for the user's rating of the movie.

    Attributes:
        rate_choices (set): A set of valid choices for the 'rate' field.
                            Users can choose a rating value from 1 to 10.
    """

    rate_choices = [(i, i) for i in range(1, 11)]

    rate = serializers.ChoiceField(
        choices=rate_choices,
        help_text="The user's rating for the movie (1 to 10)."
    )


class MovieDetailReviewInPutSerializer(serializers.Serializer):

    """
    Serializer for validating the input data when creating a movie review.

    Attributes:
        review (str): The user's review for the movie (max length: 512 characters).
    """

    review = serializers.CharField(
        max_length=512,
        help_text="The user's review for the movie."
    )


class MovieDetailOutPutModelSerializer(MovieOutPutModelSerializer):
    """
    Serializer for the detailed representation of a movie.

    Inherits from MovieOutPutModelSerializer.

    Additional Fields:
        ratings_count (int): The total number of ratings for the movie.
                        This field represents the count of ratings given by users.
                        It is a non-negative integer value.
        user_rating (int): The rating given by the authenticated user (if any).
                        This field represents the rating given by the user who
                        is currently authenticated and making the request. If the
                        user has not rated the movie, it will be set to 0.
                        It is an integer value between 0 and 10 (inclusive).

    Fields:
        id (int): The unique identifier for the movie.
        title (str): The title of the movie.
        poster (ImageField): The image field for the movie's poster.
        genres (list): The list of genre titles associated with the movie.
        rate (DecimalField): The average rating of the movie.
        cast_crew (ManyToManyField): The cast and crew members associated
        with the movie.
        synopsis (str): The synopsis of the movie.
        trailer (URLField): The URL of the movie's trailer.
        runtime (DurationField): The runtime of the movie.
        release_date (DateField): The release date of the movie.
    """

    ratings_count = serializers.IntegerField(min_value=0)
    user_rating = serializers.SerializerMethodField()
    cast_crews = serializers.SerializerMethodField()

    class Meta(MovieOutPutModelSerializer.Meta):
        fields = [
            'id', 'title', 'poster', 'genres', 'rate', 'ratings_count',
            'user_rating', 'cast_crews', 'synopsis', 'trailer', 'runtime',
            'release_date'
        ]

    def get_user_rating(self, obj: Movie) -> int:
        """
        Retrieve the user's rating for the movie.

        :param obj: obj (Movie): The movie object.
        :return: int: The user's rating for the movie.
        """

        return self.context.get('user_rating')

    def get_cast_crews(self, obj: Movie) -> dict:
        """
        Retrieve the cast and crew members associated with the movie.

        :param obj: (Movie): The movie object.
        :return: dict: A dictionary containing 'casts' and 'crews' lists,
        each containing person's information.
        """

        casts = []
        crews = []

        movie_roles = obj.cast_crew_roles

        for role in movie_roles:

            career_name = (
                role.careers.all()[0].name) if role.careers.exists() else None

            person_info = {
                'name': role.cast_crew.name,
                'image': role.cast_crew.image.url,
                'career': career_name,
                'role': role.name
            }

            if role.cast_crew.cast and person_info['career'] in ('Actor', 'Actress'):
                casts.append(person_info)
            elif role.cast_crew.crew:
                crews.append(person_info)

        casts_crews = {'casts': casts, 'crews': crews}
        return casts_crews
