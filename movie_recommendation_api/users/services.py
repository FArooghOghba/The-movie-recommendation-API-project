from django.db import transaction

from .models import BaseUser, Profile


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


@transaction.atomic
def update_profile(*, username: str, updated_fields: dict) -> Profile:

    """
    Update a user's profile information, including the username if provided.

    This function retrieves the user and their associated profile based on the
    provided username. If an 'username' field is included in the 'updated_fields'
    dictionary, it updates the user's username and saves the changes. Then, it
    updates other profile fields based on the provided data and returns the
    user's updated profile.

    :param username: (str): The username of the user whose profile to update.
    :param updated_fields: (dict): A dictionary containing the fields to update
        and their new values.
    :return: Profile: The updated user profile.
    """

    user = BaseUser.objects.get(username=username)
    user_profile = Profile.objects.get(user=user)

    if 'username' in updated_fields.keys():
        user.username = updated_fields['username']
        user.save()

    # Update each field in the profile based on the provided data
    for field, value in updated_fields.items():
        if hasattr(user_profile, field):
            setattr(user_profile, field, value)

    user_profile.save()

    return user_profile
