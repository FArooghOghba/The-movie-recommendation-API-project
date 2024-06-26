from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction

from .models import BaseUser, Profile
from .selectors import get_profile_detail, get_user_obj, get_user_profile_obj
from ..movie.selectors.movie_dependencies import get_genre_obj, get_movie_obj


def create_profile(
    *, user: BaseUser, first_name: str | None = None, last_name: str | None = None,
    bio: str | None = None
) -> Profile:

    """
    Create a user profile.

    :param user: (BaseUser): The user for whom to create the profile.
    :param first_name: (str | None): The user's first name (optional).
    :param last_name: (str | None): The user's last name (optional).
    :param bio: (str | None): A short biography or description
    of the user (optional).
    :return: Profile: The created user profile.
    """

    return Profile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        bio=bio
    )


def create_user(*, username: str, email: str, password: str) -> BaseUser:

    """
    Create a user.

    :param username: (str): The user's username.
    :param email: (str): The user's email address.
    :param password: (str): The user's password.
    :return: BaseUser: The created user.
    """

    return BaseUser.objects.create_user(
        email=email, username=username, password=password
    )


@transaction.atomic
def register(
    *, username: str, email: str, password: str,
    first_name: str | None = None, last_name: str | None = None,
    bio: str | None = None
) -> BaseUser:

    """
    Register a new user along with their profile.

    :param username: (str): The user's username.
    :param email: (str): The user's email address.
    :param password: (str): The user's password.
    :param first_name: (str | None): The user's first name (optional).
    :param last_name: (str | None): The user's last name (optional).
    :param bio: (str | None): A short biography or description of
    the user (optional).
    :return: BaseUser: The created user.
    """

    user = create_user(
        email=email, username=username, password=password
    )

    create_profile(
        user=user,
        first_name=first_name,
        last_name=last_name,
        bio=bio
    )

    return user


def update_user_profile_picture() -> SimpleUploadedFile:

    """
    Generates a default user profile picture.

    This function creates a default profile picture using a pre-existing image
    and returns it as a SimpleUploadedFile object.

    :return: SimpleUploadedFile: Default user profile picture.
    """

    default_image = SimpleUploadedFile(
        name='user_profile_image/blank-profile-image.png',
        content=b"image_content",
        content_type="image/png"
    )
    return default_image


def update_user_profile_watchlist(
    *, user_profile: Profile, new_movie_slug: str
) -> Profile:

    """
    Update the user's watchlist with a new movie.

    This function manages the user's watchlist by adding or removing a movie
    based on its slug. If the movie exists in the watchlist, it removes it.
    Otherwise, it adds the movie to the watchlist.

    :param user_profile: (Profile): The user's profile.
    :param new_movie_slug: (str): The slug of the new movie.
    :return: Profile: Updated user profile.
    """

    new_movie = get_movie_obj(movie_slug=new_movie_slug)

    watchlist_movie_slugs = user_profile.watchlist.values_list('slug', flat=True)
    if new_movie_slug in watchlist_movie_slugs:
        # Remove the existed movie from the watchlist.
        user_profile.watchlist.remove(new_movie)
    else:
        # Add the new movie to the watchlist.
        user_profile.watchlist.add(new_movie)

    return user_profile


def update_user_profile_favorite_genres(
    *, user_profile: Profile, new_genre_slug: str
) -> Profile:

    """
    Update the user's favorite genres with a new genre.

    This function manages the user's favorite genres by adding or removing a genre
    based on its slug. If the genre exists in the favorites, it removes it.
    Otherwise, it adds the genre to the favorites.

    :param user_profile: (Profile): The user's profile.
    :param new_genre_slug: (str): The slug of the new genre.
    :return: Profile: Updated user profile.
    """

    new_genre = get_genre_obj(genre_slug=new_genre_slug)

    favorite_genre_slugs = (user_profile.favorite_genres
                            .values_list('slug', flat=True))
    if new_genre_slug in favorite_genre_slugs:
        # Remove the existed genre from the favorite genres.
        user_profile.favorite_genres.remove(new_genre)
    else:
        # Add the new genre to the favorite genres
        user_profile.favorite_genres.add(new_genre)

    return user_profile


@transaction.atomic
def update_profile_fields(*, username: str, updated_fields: dict) -> Profile:

    """
    Update a user's profile information, including the username if provided.

    This function retrieves the user and their associated profile based on the
    provided username. If a 'username' field is included in the 'updated_fields'
    dictionary, it updates the user's username and saves the changes. Then, it
    updates other profile fields based on the provided data and returns the
    user's updated profile.

    If 'watchlist' is included in the 'updated_fields' dictionary, it adds a new
    movie to the user's watchlist based on the provided movie slug. If the movie
    is already in the watchlist, it will be removed, and if it's not in the
    watchlist, it will be added.

    If 'favorite_genres' is included in the 'updated_fields' dictionary, it adds
    a new genre to the user's favorite_genres based on the provided genre slug.
    If the genre is already in the favorite genres, it will be removed, and if
    it's not in the favorites, it will be added.

    If 'picture' is included in the 'updated_fields' dictionary with a value of
    None, the user's profile picture is set to the default profile image.

    :param username: (str): The username of the user whose profile to update.
    :param updated_fields: (dict): A dictionary containing the fields to update
        and their new values.
    :return: Profile: The updated user profile.
    """

    user = get_user_obj(username=username)
    user_profile = get_user_profile_obj(user=user)

    if 'username' in updated_fields.keys():
        user.username = updated_fields['username']
        user.save()

    # If 'picture' is in validated_data and its value is None,
    # set it to the default picture
    if 'picture' in updated_fields and updated_fields['picture'] is None:
        updated_fields['picture'] = update_user_profile_picture()

    # Handle updating the watchlist separately
    if 'watchlist' in updated_fields:
        new_movie_slug = updated_fields['watchlist']
        user_profile = update_user_profile_watchlist(
            user_profile=user_profile, new_movie_slug=new_movie_slug
        )

    # Handle updating the favorite genres separately
    if 'favorite_genres' in updated_fields:
        new_genre_slug = updated_fields['favorite_genres']
        user_profile = update_user_profile_favorite_genres(
            user_profile=user_profile, new_genre_slug=new_genre_slug
        )

    # Update each field in the profile based on the provided data
    for field, value in updated_fields.items():
        if hasattr(user_profile, field) and \
                field not in ['watchlist', 'favorite_genres']:

            setattr(user_profile, field, value)

    user_profile.save()

    user_updated_profile = get_profile_detail(username=user.username)

    return user_updated_profile
