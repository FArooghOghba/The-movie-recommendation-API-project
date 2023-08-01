from django.urls import reverse

from rest_framework import serializers

from movie_recommendation_api.movie.models import Movie


class MovieOutPutModelSerializer(serializers.ModelSerializer):
    """
    Serializer for representing the output of a Movie object.

    This serializer includes fields for the title, poster, genre, average rating,
    movie detail URL, and synopsis snippet of a Movie object.

    Fields:
        title (str): The title of the movie.
        poster (ImageField): The image field for the movie's poster.
        genre (ManyToManyField): The genres associated with the movie.
        rate (DecimalField): The average rating of the movie.
        movie_detail_url (str): The URL for accessing the movie's detail view.
        synopsis_snippet (str): A shortened snippet of the movie's synopsis.

    Methods:
        get_movie_detail_url(self, movie): Returns the URL of
                                           the movie's detail view.
    """

    # Use the avg_rating annotation added by the get_movie_list function as
    # the source for the rate field
    rate = serializers.DecimalField(
        max_digits=3, decimal_places=1, source='avg_rating'
    )
    synopsis_snippet = serializers.CharField(source='get_snippet')
    movie_detail_url = serializers.SerializerMethodField(
        method_name='get_movie_detail_url'
    )

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'poster', 'trailer', 'genre',
            'rate', 'movie_detail_url', 'synopsis_snippet'
        ]

    def get_movie_detail_url(self, movie: Movie) -> str:
        """
        Retrieves the URL for accessing the movie's detail view.

        :param movie: movie (Movie): The movie object.
        :return: str: The URL for accessing the movie's detail view.
        """

        request = self.context.get("request")
        path = reverse(viewname="api:movie:detail", args=(movie.slug,))
        return request.build_absolute_uri(path)


class MovieDetailInPutSerializer(serializers.Serializer):
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

    rate_choices = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

    rate = serializers.ChoiceField(choices=rate_choices)


class MovieDetailOutPutModelSerializer(MovieOutPutModelSerializer):
    """
    Serializer for the detailed representation of a movie.

    Inherits from MovieOutPutModelSerializer.

    Additional Fields:
        cast_crew (ManyToManyField): The cast and crew members
                  associated with the movie.
        synopsis (str): The synopsis of the movie.
        trailer (URLField): The URL of the movie's trailer.
        runtime (DurationField): The runtime of the movie.
        release_date (DateField): The release date of the movie.
    """
    class Meta(MovieOutPutModelSerializer.Meta):
        fields = [
            'id', 'title', 'poster', 'genre', 'rate', 'cast_crew',
            'synopsis', 'trailer', 'runtime', 'release_date'
        ]


class MovieFilterSerializer(serializers.Serializer):
    """
     Serializer for filtering movies.

    Fields:
        title (CharField): The title of the movie.
        search (CharField): The search query for filtering movies.
        genre__title (CharField): The genres of the movies.
    """

    title = serializers.CharField(required=False, max_length=100)
    search = serializers.CharField(required=False, max_length=100)
    genre__title = serializers.CharField(required=False, max_length=100)
    # created_at__range = serializers.CharField(required=False, max_length=100)
    # author__in = serializers.CharField(required=False, max_length=100)
    # slug = serializers.CharField(required=False, max_length=100)
    # content = serializers.CharField(required=False, max_length=1000)
