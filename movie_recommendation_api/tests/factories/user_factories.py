"""
Factories for the user tests.
"""

from typing import Dict, Optional

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
    def create_payload(cls) -> Dict[str, str]:
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
    def profile(self, create: bool, extracted: Optional['Profile'], **kwargs):

        """
        Post-generation hook to create a related Profile instance for the BaseUser.

        :param create: (bool): Flag indicating whether to create a related Profile.
        :param extracted: A Profile instance that can be passed in.
        :param kwargs:
        :return:
        """

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
    """
    Factory class for creating instances of the Profile model.

    This factory allows creating Profile instances with associated
    BaseUser instances.

    Attributes:
        user (BaseUser): The BaseUser instance associated with the profile.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        bio (str): A short biography or description of the user.

    Methods:
        create_profile(cls, user) -> Profile: Creates a Profile instance with
        an associated BaseUser.
    """

    class Meta:
        model = Profile

    user = factory.SubFactory(BaseUserFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    bio = factory.Faker('text')

    @classmethod
    def create_profile(cls, user: Optional[BaseUser] = None) -> Profile:

        """
        Creates a Profile instance with an associated BaseUser.

        :param user: (BaseUser, optional): The BaseUser instance to associate
        with the profile.
        :return: Profile: The created Profile instance.
        """

        return cls.create(user=user)
