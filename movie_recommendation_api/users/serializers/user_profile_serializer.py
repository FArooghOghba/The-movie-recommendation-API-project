from rest_framework import serializers

from movie_recommendation_api.users.models import Profile


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

        watchlist_queryset = obj.watchlist.order_by('-created_at')

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

        rating_queryset = obj.ratings.order_by('-created_at')

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

        review_queryset = obj.reviews.order_by('-created_at')

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
