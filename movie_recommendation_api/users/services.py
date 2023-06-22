from django.db import transaction 
from .models import BaseUser


# def create_profile(*, user: BaseUser, bio: str | None) -> Profile:
#     return Profile.objects.create(user=user, bio=bio)


def create_user(*, username: str, email: str, password: str) -> BaseUser:
    return BaseUser.objects.create_user(
        email=email, username=username, password=password
    )


@transaction.atomic
def register(*, username: str, email: str, bio: str | None, password: str) -> BaseUser:

    user = create_user(
        email=email, username=username, password=password
    )
    # create_profile(user=user, bio=bio)

    return user
