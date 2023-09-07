"""User Model"""
import os
import uuid

from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator

from django.utils.translation import gettext_lazy as _

from movie_recommendation_api.common.models import BaseModel


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(
            self, email: str, username: str, password: str = None, **extra_fields
    ):
        """
        Create & save a User with the given email, username, and password.
        """

        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError('The username must be set.')

        user = self.model(
            email=self.normalize_email(email.lower()),
            username=username,
            **extra_fields
        )

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(
            self, email: str, username: str, password: str = None, **extra_fields
    ):
        """
        Create & save SuperUser with given email and password.
        """

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields
        )

        user.save(using=self._db)

        return user


class BaseUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model Based on AbstractBaseUser & PermissionMixin for
    creating custom user model and adding email as USERNAME FIELD.
    """

    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(_("email address"), max_length=150, unique=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        }
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    is_verified = models.BooleanField(
        _("verified"),
        default=False,
        help_text=_(
            "Designates whether this user verified his account. "
        ),
    )

    is_superuser = models.BooleanField(
        _('superuser'),
        default=False,
        help_text=_(
            "Designates whether this user is super user."
        ),
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ('username',)

    def __str__(self):
        return self.email


def user_profile_image_file_path(instance, filename):
    """Generate a file path for new user image."""

    extension = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{extension}'

    return os.path.join('uploads', 'user_profile_image', filename)


class Profile(BaseModel):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256, null=True, blank=True)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    picture = models.ImageField(
        upload_to=user_profile_image_file_path,
        default='user_profile_image/blank-profile-image.png'
    )
    bio = models.CharField(max_length=512, null=True, blank=True)
    favorite_genres = models.ManyToManyField(to='movie.Genre', blank=True)
    watchlist = models.ManyToManyField(to='movie.Movie', blank=True)
    ratings = models.ManyToManyField(to='movie.Rating', blank=True)
    reviews = models.ManyToManyField(to='movie.Review', blank=True)
    # activity = models.ManyToManyField(to='Activity', blank=True)

    def __str__(self):
        return f"{self.user} >> {self.first_name} {self.last_name}"
