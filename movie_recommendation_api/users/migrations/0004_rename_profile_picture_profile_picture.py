# Generated by Django 4.2.2 on 2023-09-05 17:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_profile_created_at_profile_updated_at"),
    ]

    operations = [
        migrations.RenameField(
            model_name="profile",
            old_name="profile_picture",
            new_name="picture",
        ),
    ]