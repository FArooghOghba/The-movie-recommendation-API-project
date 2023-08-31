from rest_framework import serializers


class MovieFilterSerializer(serializers.Serializer):
    """
     Serializer for filtering movies.

    Fields:
        title (CharField, optional): The title of the movie.
        search (CharField, optional): The search query for filtering movies.
        genre__title (CharField, optional): The genres of the movies.
        min_rating (DecimalField, optional): The min average rating for filtering.
        max_rating (DecimalField, optional): The max average rating for filtering.
        release_date_before (DateField, optional): The release date before which
        to filter movies.
        release_date_after (DateField, optional): The release date after which
        to filter movies.
    """

    title = serializers.CharField(required=False, max_length=100)
    search = serializers.CharField(required=False, max_length=100)
    genre__title = serializers.CharField(required=False, max_length=100)
    min_rating = serializers.DecimalField(
        required=False, max_digits=2, decimal_places=1
    )
    max_rating = serializers.DecimalField(
        required=False, max_digits=2, decimal_places=1
    )
    release_date_before = serializers.DateField(required=False)
    release_date_after = serializers.DateField(required=False)
    cast_crew = serializers.CharField(
        required=False, max_length=255
    )
