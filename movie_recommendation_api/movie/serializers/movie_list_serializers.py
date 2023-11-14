from typing import List

from django.urls import reverse

from rest_framework import serializers

from movie_recommendation_api.movie.models import Movie


class MovieOutPutModelSerializer(serializers.ModelSerializer):
    """
    Serializer for representing the output of a Movie object.

    This serializer includes fields for the title, poster, genres, average rating,
    movie detail URL, and synopsis snippet of a Movie object.

    Fields:
        id (int): The ID of the movie.
        title (str): The title of the movie.
        poster (ImageField): The image field for the movie's poster.
        genres (list): The list of genre titles associated with the movie.
        rate (DecimalField): The average rating of the movie.
        movie_detail_url (str): The URL for accessing the movie's detail view.
        synopsis_snippet (str): A shortened snippet of the movie's synopsis.

    Methods:
        get_genres(self, obj): Returns a list of genre titles for the movie.
        get_movie_detail_url(self, movie): Returns the URL of
        the movie's detail view.
    """

    # Use the avg_rating annotation added by the get_movie_list function as
    # the source for the rate field
    rate = serializers.DecimalField(
        max_digits=3, decimal_places=1, source='avg_rating'
    )
    genres = serializers.SerializerMethodField()
    synopsis_snippet = serializers.CharField(source='get_snippet')
    movie_detail_url = serializers.SerializerMethodField(
        method_name='get_movie_detail_url'
    )

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'poster', 'trailer', 'genres',
            'rate', 'movie_detail_url', 'synopsis_snippet',
            'release_date'
        ]

    def get_genres(self, obj) -> List[str]:
        """
         Returns a list of genre titles associated with the movie.

        :param obj: The movie object.
        :return: list: List of genre titles.
        """
        return [genre.title for genre in obj.genre.all()]

    def get_movie_detail_url(self, movie: Movie) -> str:
        """
        Retrieves the URL for accessing the movie's detail view.

        :param movie: movie (Movie): The movie object.
        :return: str: The URL for accessing the movie's detail view.
        """

        request = self.context.get("request")
        path = reverse(viewname="api:movie:detail", args=(movie.slug,))
        return request.build_absolute_uri(path)
