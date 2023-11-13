import os
import uuid

from lightfm import LightFM
from lightfm.data import Dataset

import numpy as np

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

from movie_recommendation_api.common.models import BaseModel
from movie_recommendation_api.movie.validators import (
    validate_content_length, validate_review_content
)


def movie_poster_file_path(instance, filename):
    """Generate file path for new movie poster."""
    extension = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{extension}'

    year = str(instance.release_date.year)
    month = str(instance.release_date.month)

    return os.path.join(
        'uploads', 'movie-poster', year, month, filename
    )


def cast_crew_image_file_path(instance, filename):
    """Generate file path for new cast/crew image."""
    extension = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{extension}'

    return os.path.join('uploads', 'cast_crew_image', filename)


class Genre(BaseModel):
    """
    Represents a movie genre.

    Attributes:
        title (str): The title of the genre.
        slug (str): The slug field for the genre's URL representation.

    Methods:
        save(self, *args, **kwargs): Overrides the save method to generate
        the slug based on the title.
        __str__(self): Returns a string representation of the genre.
    """

    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CastCrew(BaseModel):
    """
   Represents a cast or crew member of a movie.

   Attributes:
        name (str): The name of the cast or crew member.
        image (ImageField): The image field for the cast or crew member's image.
        careers (ManyToManyField): The list of careers associated with
        the cast or crew member.
        cast (bool): Indicates if the member is part of the cast.
        crew (bool): Indicates if the member is part of the crew.

   Methods:
        save(self, *args, **kwargs): Overrides the save method to generate
        the slug based on the title.
        __str__(self): Returns a string representation of the genre.
   """

    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(
        upload_to=cast_crew_image_file_path,
        default='cast_crew_image/blank-profile-picture.png'
    )
    careers = models.ManyToManyField(
        to='Career',
        related_name='cast_crew_members',
    )
    cast = models.BooleanField(default=False)
    crew = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Career(models.Model):
    """
    Represents a career (role) of a cast/crew member.

    Attributes:
        name (str): The name of the career.

    Methods:
        __str__(self): Returns a string representation of the career.
    """

    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Movie(BaseModel):
    """
    Represents a movie.

    Attributes:
        title (str): The title of the movie.
        slug (str): The slug field for the movie's URL representation.
        genre (ManyToManyField): The genres associated with the movie.
        cast_crew (ManyToManyField): The cast and crew members associated
        with the movie.
        synopsis (str): The synopsis of the movie.
        poster (ImageField): The image field for the movie's poster.
        trailer (URLField): The URL of the movie's trailer.
        runtime (DurationField): The runtime of the movie.
         release_date (DateField): The release date of the movie.

    Methods:
        get_absolute_url(self): Returns the absolute URL of the movie.
        save(self, *args, **kwargs): Overrides the save method to generate
        the slug based on the title.
        get_snippet(self): Returns a shortened snippet of the movie's synopsis.
        __str__(self): Returns a string representation of the movie.
    """

    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(null=False, unique=True)
    genre = models.ManyToManyField(to=Genre, related_name='movies')
    cast_crew = models.ManyToManyField(
        CastCrew,
        through='role'
    )
    synopsis = models.TextField()
    poster = models.ImageField(upload_to=movie_poster_file_path)
    trailer = models.URLField()
    runtime = models.DurationField()
    release_date = models.DateField()

    class Meta:
        ordering = ['-release_date']

    def get_snippet(self) -> str:
        """
        Returns a shortened snippet of the movie's synopsis.
        :return: str: The snippet of the movie's synopsis.
        """
        return f'{self.synopsis[:15]}...'

    def save(self, *args, **kwargs):
        """
        Overrides the save method to generate the slug based on the title.
        :param args: Variable length argument list.
        :param kwargs: Arbitrary keyword arguments.
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Rating(BaseModel):
    """
    Represents a rating given by a user to a movie.

    Attributes:
        user (ForeignKey): The user who gave the rating.
        movie (ForeignKey): The movie that was rated.
        rating (DecimalField): The rating value given by the user.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='movie_ratings'
    )
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )

    def __str__(self):
        return f"Rate for {self.movie.title} by " \
               f"{self.user.username} >>" \
               f"{self.rating}"


class Review(BaseModel):
    """
    Represents a review for a movie.

    A review is a user-generated content that provides insights and opinions
    about a movie.

    Attributes:
        title (CharField, max_length=128): The title of the review.
        slug (SlugField, unique=True): A unique slug used for identifying the review.
        spoilers (BooleanField, default=False): Indicates if the review
        contains spoilers.
        user (ForeignKey): The user who wrote the review.
        movie (ForeignKey): The movie for which the review is written.
        content (TextField, max_length=512): The content of the review.

    Methods:
        save(self, *args, **kwargs): Overrides the save method to auto-generate
        the slug if not provided.
        __str__(self): Returns a string representation of the review, including
        movie title, user, and title.
    """

    title = models.CharField(max_length=128, unique=True, default='')
    slug = models.SlugField(unique=True, default='')
    spoilers = models.BooleanField(default=False)
    user = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name='reviews'
    )
    movie = models.ForeignKey(
        to=Movie, on_delete=models.CASCADE, related_name='reviews'
    )
    content = models.TextField(
        max_length=512, validators=[validate_review_content, validate_content_length]
    )

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to auto-generate the slug if not provided.
        """

        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review for {self.movie.title} by" \
               f"{self.user.username} >>" \
               f"{self.title}"


class Role(BaseModel):
    """
    Represents the role of a cast/crew member in a movie.

    Attributes:
        name (str): The name of the role.
        cast_crew (ForeignKey): The cast or crew member associated with the role.
        careers (ManyToManyField): The list of careers associated with the role.
        movie (ForeignKey): The movie associated with the role.
    """

    name = models.CharField(max_length=64)
    cast_crew = models.ForeignKey(
        to=CastCrew,
        on_delete=models.CASCADE,
    )
    careers = models.ManyToManyField(
        to='Career',
        related_name='roles',
    )
    movie = models.ForeignKey(
        to=Movie,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class MovieRecommendationModel:

    """
    A movie recommendation model that uses LightFM.

    This model provides movie recommendations based on user
    interactions such as ratings and watchlist.

    Attributes:
        loss (str): The loss function to use ('warp' or 'bpr').
        epochs (int): The number of training epochs.
        model (LightFM): The LightFM model for recommendations.
        dataset (Dataset): The dataset for users and movies.

    Methods:
        prepare_data(all_movies, all_users, user_ratings): Prepare data for
        training the recommendation model.
        train_model(interactions): Train the recommendation model.
        recommend(user_ids, item_ids, num_recs=10): Get movie recommendations
        for users.
    """

    def __init__(self, loss='warp', epochs=10):

        """
        Initialize a movie recommendation model.

        Args:
            loss (str): The loss function to use ('warp' or 'bpr').
            epochs (int): The number of training epochs.
        """

        self.loss = loss
        self.epochs = epochs
        self.model = None
        self.dataset = Dataset()

    def prepare_data(self, all_movies, all_users, user_ratings):

        """
        Prepare data for training the recommendation model.

        Args:
            all_movies (list): List of movie IDs.
            all_users (list): List of user IDs.
            user_ratings (list): List of rating data.

        Returns:
            interactions: Interaction matrix for training.
        """

        # Fit users and movies to the dataset
        self.dataset.fit(all_users, items=all_movies)

        # Build the interaction matrix using rating data
        interactions, _ = self.dataset.build_interactions(user_ratings)

        return interactions

    def train_model(self, interactions):
        """
        Train the recommendation model.

        Args:
            interactions: Interaction matrix for training.
        """

        self.model = LightFM(loss=self.loss)
        self.model.fit(interactions, epochs=self.epochs)

    def recommend(self, user_ids, item_ids, num_recs=10):

        """
        Get movie recommendations for users.

        Args:
            user_ids: User IDs.
            item_ids: Movie IDs.
            num_recs (int): Number of recommendations to return.

        Returns:
            top_items: Top recommended movie IDs.
        """

        scores = self.model.predict(user_ids, item_ids)
        top_items = np.argsort(-scores)[:num_recs]

        return top_items
