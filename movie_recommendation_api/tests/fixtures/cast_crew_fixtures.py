import pytest

from movie_recommendation_api.tests.factories.movie_factories import CastCrewFactory


@pytest.fixture
def first_test_cast(first_test_career, second_test_career) -> CastCrewFactory:
    """
    Fixture for creating the first test cast.

    This fixture creates a CastCrewFactory instance with
    the specified cast role and career as an actor.
    It returns the created cast object for testing purposes.

    :return: CastCrewFactory: The created cast object.
    """

    return CastCrewFactory.create(
        cast=True,
        careers=[first_test_career, second_test_career]
    )


@pytest.fixture
def second_test_cast(second_test_career) -> CastCrewFactory:
    """
    Fixture for creating the first test cast.

    This fixture creates a CastCrewFactory instance with
    the specified cast role and career as an actor.
    It returns the created cast object for testing purposes.

    :return: CastCrewFactory: The created cast object.
    """

    return CastCrewFactory.create(
        cast=True,
        careers=[second_test_career]
    )


@pytest.fixture
def third_test_cast(third_test_career) -> CastCrewFactory:
    """
    Fixture for creating the first test cast.

    This fixture creates a CastCrewFactory instance with
    the specified cast role and career as an actor.
    It returns the created cast object for testing purposes.

    :return: CastCrewFactory: The created cast object.
    """

    return CastCrewFactory.create(
        cast=True,
        careers=[third_test_career]
    )


@pytest.fixture
def first_test_crew(first_test_career) -> CastCrewFactory:
    """
    Fixture for creating the first test crew.

    This fixture creates a CastCrewFactory instance with
    the specified crew role and career as a director.
    It returns the created crew object for testing purposes.

    :return: CastCrewFactory: The created crew object.
    """
    return CastCrewFactory.create(
        crew=True,
        careers=[first_test_career]
    )


@pytest.fixture
def second_test_crew(second_test_career) -> CastCrewFactory:
    """
    Fixture for creating the first test crew.

    This fixture creates a CastCrewFactory instance with
    the specified crew role and career as a director.
    It returns the created crew object for testing purposes.

    :return: CastCrewFactory: The created crew object.
    """

    return CastCrewFactory.create(
        crew=True,
        careers=[second_test_career]
    )


@pytest.fixture
def third_test_crew(third_test_career) -> CastCrewFactory:
    """
    Fixture for creating the first test crew.

    This fixture creates a CastCrewFactory instance with
    the specified crew role and career as a director.
    It returns the created crew object for testing purposes.

    :return: CastCrewFactory: The created crew object.
    """

    return CastCrewFactory.create(
        crew=True,
        careers=[third_test_career]
    )
