import factory

from movie_recommendation_api.movie.models import (
    Career, CastCrew, Genre, Movie, Rating, Review, Role,
    cast_crew_image_file_path, movie_poster_file_path
)
from movie_recommendation_api.tests.factories.user_factories import BaseUserFactory
from movie_recommendation_api.utils.tests import fake


class GenreFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Genre model.
    """
    class Meta:
        model = Genre

    title = factory.LazyAttribute(lambda _: fake.word())


class CareerFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Career model.
    """
    class Meta:
        model = Career

    name = factory.LazyAttribute(lambda _: fake.word())


class CastCrewFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the CastCrew model.
    """
    class Meta:
        model = CastCrew

    name = factory.LazyAttribute(lambda _: fake.name())
    image = factory.django.ImageField(
        upload_to=cast_crew_image_file_path,
        default='cast_crew_image/blank-profile-picture.png'
    )

    cast = factory.Faker('boolean')
    crew = factory.Faker('boolean')

    @factory.post_generation
    def careers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for career in extracted:
                self.careers.add(career)


class MovieFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Movie model.
    """
    class Meta:
        model = Movie

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    slug = factory.LazyAttribute(lambda _: fake.slug())
    synopsis = factory.LazyAttribute(lambda _: fake.paragraph())
    poster = factory.django.ImageField(
        upload_to=movie_poster_file_path
    )
    trailer = factory.LazyAttribute(lambda _: fake.url())
    runtime = factory.Faker('time_delta')
    release_date = factory.Faker('date_object')

    @factory.post_generation
    def genre(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for genre in extracted:
                self.genre.add(genre)

    @factory.post_generation
    def cast_crew(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cast_crew in extracted:
                name = fake.job()
                Role.objects.create(
                    name=name, cast_crew=cast_crew, movie=self
                )

    @factory.post_generation
    def ratings(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for rating in extracted:
                self.ratings.add(rating)


class RatingFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Rating model.
    """
    class Meta:
        model = Rating

    user = factory.SubFactory(BaseUserFactory)
    movie = factory.SubFactory(MovieFactory)
    rating = factory.LazyFunction(lambda: fake.pyint(min_value=1, max_value=10))


class ReviewFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Review model.
    """
    class Meta:
        model = Review

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    slug = factory.LazyAttribute(lambda _: fake.slug())
    spoilers = factory.Faker('boolean')
    user = factory.SubFactory(BaseUserFactory)
    movie = factory.SubFactory(MovieFactory)
    content = factory.LazyAttribute(lambda _: fake.paragraph())


class RoleFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Role model.
    """

    class Meta:
        model = Role

    name = factory.LazyAttribute(lambda _: fake.job())
    cast_crew = factory.SubFactory(CastCrewFactory)
    movie = factory.SubFactory(MovieFactory)

    @factory.post_generation
    def careers(self, create, extracted, **kwargs):
        """
        Post-generation hook for adding careers to the Role instance.

        :param create: Whether the Role instance was created or built.
        :param extracted: The value passed to the 'careers' parameter
         when calling the factory.
        :param kwargs: Additional keyword arguments.
        :return:
        """
        if not create:
            # If the Role instance was not created, do nothing

            return

        if extracted:
            # If careers were passed to the factory, add them to the Role instance

            for career in extracted:
                self.careers.add(career)
