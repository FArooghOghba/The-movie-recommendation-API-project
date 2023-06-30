import os
import uuid

from django.db import models
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
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    poster = models.ImageField(upload_to=movie_poster_file_path)
    trailer = models.URLField()
    runtime = models.DurationField()
    release_date = models.DateField()

    class Meta:
        ordering = ['-release_date']

    def get_absolute_url(self):
        return reverse('movie:single', kwargs={'movie_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Role(BaseModel):
    """
    Represents the role of a cast/crew member in a movie.
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
