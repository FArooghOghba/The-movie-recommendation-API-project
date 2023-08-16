import pytest

from movie_recommendation_api.tests.factories.movie_factories import CareerFactory


@pytest.fixture
def first_test_career() -> CareerFactory:
    """
    Fixture for creating and returning a test career.

    This fixture creates a test career using the `CareerFactory()` method
    from the movie factories. The created career is returned for use in tests.

    :return: Career: A test career object.
    """
    return CareerFactory()


@pytest.fixture
def second_test_career() -> CareerFactory:
    """
    Fixture for creating and returning a test career.

    This fixture creates a test career using the `CareerFactory()` method
    from the movie factories. The created career is returned for use in tests.

    :return: Career: A test career object.
    """
    return CareerFactory()


@pytest.fixture
def third_test_career() -> CareerFactory:
    """
    Fixture for creating and returning a test career.

    This fixture creates a test career using the `CareerFactory()` method
    from the movie factories. The created career is returned for use in tests.

    :return: Career: A test career object.
    """
    return CareerFactory()


@pytest.fixture
def forth_test_career() -> CareerFactory:
    """
    Fixture for creating and returning a test career.

    This fixture creates a test career using the `CareerFactory()` method
    from the movie factories. The created career is returned for use in tests.

    :return: Career: A test career object.
    """
    return CareerFactory()


@pytest.fixture
def fifth_test_career() -> CareerFactory:
    """
    Fixture for creating and returning a test career.

    This fixture creates a test career using the `CareerFactory()` method
    from the movie factories. The created career is returned for use in tests.

    :return: Career: A test career object.
    """
    return CareerFactory()
