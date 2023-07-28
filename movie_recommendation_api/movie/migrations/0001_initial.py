# Generated by Django 4.2.2 on 2023-07-25 15:28

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import movie_recommendation_api.movie.models
import movie_recommendation_api.movie.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CastCrew",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "image",
                    models.ImageField(
                        default="cast_crew_image/blank-profile-picture.png",
                        upload_to=movie_recommendation_api.movie.models.cast_crew_image_file_path,
                    ),
                ),
                (
                    "career",
                    models.CharField(
                        choices=[
                            ("Actor", "Actor"),
                            ("Actress", "Actress"),
                            ("Director", "Director"),
                            ("Writer", "Writer"),
                            ("Producer", "Producer"),
                            ("Music", "Music"),
                        ],
                        default="Actor",
                        max_length=10,
                    ),
                ),
                ("cast", models.BooleanField(default=False)),
                ("crew", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255, unique=True)),
                ("slug", models.SlugField(unique=True)),
            ],
            options={
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="Movie",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255, unique=True)),
                ("slug", models.SlugField(unique=True)),
                ("synopsis", models.TextField()),
                (
                    "poster",
                    models.ImageField(
                        upload_to=movie_recommendation_api.movie.models.movie_poster_file_path
                    ),
                ),
                ("trailer", models.URLField()),
                ("runtime", models.DurationField()),
                ("release_date", models.DateField()),
            ],
            options={
                "ordering": ["-release_date"],
            },
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=64)),
                (
                    "cast_crew",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="movie.castcrew"
                    ),
                ),
                (
                    "movie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="movie.movie"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "content",
                    models.TextField(
                        max_length=512,
                        validators=[
                            movie_recommendation_api.movie.validators.validate_review_content,
                            django.core.validators.MaxLengthValidator(
                                512, "Content exceeds the maximum allowed length."
                            ),
                        ],
                    ),
                ),
                (
                    "movie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="movie.movie",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Rating",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "rating",
                    models.DecimalField(
                        decimal_places=1,
                        max_digits=3,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(10.0),
                        ],
                    ),
                ),
                (
                    "movie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="movie_ratings",
                        to="movie.movie",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="movie",
            name="cast_crew",
            field=models.ManyToManyField(
                related_name="casts_crews", through="movie.Role", to="movie.castcrew"
            ),
        ),
        migrations.AddField(
            model_name="movie",
            name="genre",
            field=models.ManyToManyField(related_name="movies", to="movie.genre"),
        ),
        migrations.AddField(
            model_name="movie",
            name="ratings",
            field=models.ManyToManyField(
                related_name="rated_movies", to="movie.rating"
            ),
        ),
    ]
