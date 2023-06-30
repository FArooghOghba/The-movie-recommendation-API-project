import factory

from movie_recommendation_api.movie.models import (
    CastCrew, Genre, Movie, Role,
    cast_crew_image_file_path, movie_poster_file_path
)
from movie_recommendation_api.utils.tests import fake


class GenreFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Genre model.
    """
    class Meta:
        model = Genre

    title = factory.LazyAttribute(lambda _: fake.word())


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
    career = factory.LazyAttribute(
        lambda _: fake.random_element(
            elements=('Actor', 'Actress', 'Director', 'Writer', 'Producer', 'Music')
        )
    )
    cast = factory.Faker('boolean')
    crew = factory.Faker('boolean')


class MovieFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Movie model.
    """
    class Meta:
        model = Movie

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    slug = factory.LazyAttribute(lambda _: fake.slug())
    synopsis = factory.LazyAttribute(lambda _: fake.paragraph())
    rating = factory.Faker(
        'pydecimal',
        left_digits=1, right_digits=1, positive=True, min_value=1, max_value=10
    )
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


class RoleFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating instances of the Role model.
    """
    class Meta:
        model = Role

    name = fake.job()
    cast_crew = factory.SubFactory(CastCrewFactory)
    movie = factory.SubFactory(MovieFactory)
