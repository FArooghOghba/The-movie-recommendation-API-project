"""
Factories for the user tests.
"""

import factory

from movie_recommendation_api.users.models import BaseUser, Profile


class BaseUserFactory(factory.django.DjangoModelFactory):
    """
    Factory class for creating instances of the BaseUser model.

    This factory provides a convenient way to generate
    test data for the BaseUser model in Django.
    It automatically generates unique email addresses,
    usernames, and sets a default password for each
    created instance.
    """
    class Meta:
        model = BaseUser

    email = factory.Sequence(
        lambda instance_num: f'test_user_{instance_num}@example.com'
    )

    username = factory.Sequence(
        lambda instance_num: f'test_user_{instance_num}'
    )

    password = factory.PostGenerationMethodCall('set_password', 'test_pass0')

    @classmethod
    def create_payload(cls) -> dict:
        """
        A class method that generates a payload dictionary for creating
        a user via the API.
        :return: generate a payload dictionary with consistent values
        for creating users via the API.
        """

        test_user = cls.build()
        return {
            'email': test_user.email,
            'username': test_user.username,
            'password': 'test_pass0',
            'confirm_password': 'test_pass0',
        }

    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A profile was passed in, use it
            self.profile = extracted
        else:
            # No profile was passed in, create one
            ProfileFactory(user=self)


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(BaseUserFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    bio = factory.Faker('text')

    @classmethod
    def create_profile(cls, user=None):
        return cls.create(user=user)
