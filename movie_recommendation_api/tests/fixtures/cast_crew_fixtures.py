import pytest

from movie_recommendation_api.tests.factories.movie_factories import CastCrewFactory


@pytest.fixture
def first_test_cast() -> CastCrewFactory:
    """
    Fixture for creating the first test cast.

    This fixture creates a CastCrewFactory instance with
    the specified cast role and career as an actor.
    It returns the created cast object for testing purposes.

    :return: CastCrewFactory: The created cast object.
    """

    return CastCrewFactory.create(
        cast=True,
        career='Actor'
    )


@pytest.fixture
def second_test_cast() -> CastCrewFactory:
    """
    Fixture for creating the first test cast.

    This fixture creates a CastCrewFactory instance with
    the specified cast role and career as an actor.
    It returns the created cast object for testing purposes.

    :return: CastCrewFactory: The created cast object.
    """

    return CastCrewFactory.create(
        cast=True,
        career='Actress'
    )


@pytest.fixture
def third_test_cast() -> CastCrewFactory:
    """
    Fixture for creating the first test cast.

    This fixture creates a CastCrewFactory instance with
    the specified cast role and career as an actor.
    It returns the created cast object for testing purposes.

    :return: CastCrewFactory: The created cast object.
    """

    return CastCrewFactory.create(
        cast=True,
        career='Actor'
    )


@pytest.fixture
def first_test_crew() -> CastCrewFactory:
    """
    Fixture for creating the first test crew.

    This fixture creates a CastCrewFactory instance with
    the specified crew role and career as a director.
    It returns the created crew object for testing purposes.

    :return: CastCrewFactory: The created crew object.
    """
    return CastCrewFactory.create(
        crew=True,
        career='Director'
    )


@pytest.fixture
def second_test_crew() -> CastCrewFactory:
    """
    Fixture for creating the first test crew.

    This fixture creates a CastCrewFactory instance with
    the specified crew role and career as a director.
    It returns the created crew object for testing purposes.

    :return: CastCrewFactory: The created crew object.
    """

    return CastCrewFactory.create(
        crew=True,
        career='Writer'
    )


@pytest.fixture
def third_test_crew() -> CastCrewFactory:
    """
    Fixture for creating the first test crew.

    This fixture creates a CastCrewFactory instance with
    the specified crew role and career as a director.
    It returns the created crew object for testing purposes.

    :return: CastCrewFactory: The created crew object.
    """

    return CastCrewFactory.create(
        crew=True,
        career='Producer'
    )
