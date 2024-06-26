# Generated by Django 4.2.2 on 2023-10-07 08:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movie", "0004_role_careers"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="slug",
            field=models.SlugField(default="", unique=True),
        ),
        migrations.AddField(
            model_name="review",
            name="spoilers",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="review",
            name="title",
            field=models.CharField(default="", max_length=128, unique=True),
        ),
    ]
