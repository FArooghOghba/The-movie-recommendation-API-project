from django.db import transaction

from .models import BaseUser, Profile


def create_profile(
    *, user: BaseUser, first_name: str | None, last_name: str | None, bio: str | None
) -> Profile:
    return Profile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        bio=bio
    )


def create_user(*, username: str, email: str, password: str) -> BaseUser:
    return BaseUser.objects.create_user(
        email=email, username=username, password=password
    )


@transaction.atomic
def register(
    *, username: str, email: str, password: str,
    first_name: str | None, last_name: str | None, bio: str | None
) -> BaseUser:

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
