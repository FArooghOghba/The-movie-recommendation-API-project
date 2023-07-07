import os
import uuid

from django.db import models
from django.db.models.aggregates import Avg
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

from movie_recommendation_api.common.models import BaseModel


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
        career (str): The career of the cast or crew member.
        cast (bool): Indicates if the member is part of the cast.
        crew (bool): Indicates if the member is part of the crew.

   Methods:
        save(self, *args, **kwargs): Overrides the save method to generate
        the slug based on the title.
        __str__(self): Returns a string representation of the genre.
   """

    CAREER_CHOICES = [
        ('Actor', 'Actor'),
        ('Actress', 'Actress'),
        ('Director', 'Director'),
        ('Writer', 'Writer'),
        ('Producer', 'Producer'),
        ('Music', 'Music'),
    ]

    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(
        upload_to=cast_crew_image_file_path,
        default='cast_crew_image/blank-profile-picture.png'
    )
    career = models.CharField(max_length=10, choices=CAREER_CHOICES, default="Actor")
    cast = models.BooleanField(default=False)
    crew = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


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
        ratings (ManyToManyField): The ratings given to the movie by users.
        poster (ImageField): The image field for the movie's poster.
        trailer (URLField): The URL of the movie's trailer.
        runtime (DurationField): The runtime of the movie.
        release_date (DateField): The release date of the movie.

    Methods:
        get_absolute_url(self): Returns the absolute URL of the movie.
        save(self, *args, **kwargs): Overrides the save method to generate
        the slug based on the title.
        __str__(self): Returns a string representation of the movie.
        average_rating(self): Calculates and returns the average rating of the movie.
    """

    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(null=False, unique=True)
    genre = models.ManyToManyField(to=Genre, related_name='movies')
    cast_crew = models.ManyToManyField(
        CastCrew,
        related_name='casts_crews',
        through='role'
    )
    synopsis = models.TextField()
    ratings = models.ManyToManyField(
        get_user_model(), through='Rating', related_name='rated_movies'
    )
    poster = models.ImageField(upload_to=movie_poster_file_path)
    trailer = models.URLField()
    runtime = models.DurationField()
    release_date = models.DateField()

    class Meta:
        ordering = ['-release_date']

    @property
    def average_rating(self) -> float:
        """
        Calculates and returns the average rating of the movie.
        :return: float: The average rating of the movie.
        """
        rating_average = self.movie_ratings.aggregate(
            rating_avg=Avg('rating')
        ).get('rating_avg', 0.0)

        return rating_average

    def get_absolute_url(self) -> str:
        """
        Returns the absolute URL of the movie.
        :return: str: The absolute URL of the movie.
        """
        return reverse('movie:single', kwargs={'movie_slug': self.slug})

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


class Role(BaseModel):
    """
    Represents the role of a cast/crew member in a movie.

    Attributes:
        name (str): The name of the role.
        cast_crew (ForeignKey): The cast or crew member associated with the role.
        movie (ForeignKey): The movie associated with the role.
    """

    name = models.CharField(max_length=64)
    cast_crew = models.ForeignKey(
        to=CastCrew,
        on_delete=models.CASCADE,
    )
    movie = models.ForeignKey(
        to=Movie,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


# class Movie(models.Model):
#     # Fields of the movie model
#     title = models.CharField(max_length=255)
#     ratings = models.ManyToManyField(User, through='Rating')
#
#     @property
#     def average_rating(self):
#         return self.ratings.aggregate(Avg('rating')).get('rating__avg', 0.0)
#
#
# class Review(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
