from django.db import models

from movie_recommendation_api.common.models import BaseModel


# Create your models here.

class Genre(BaseModel):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
