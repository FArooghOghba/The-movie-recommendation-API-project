import pytest

from movie_recommendation_api.tests.factories.movie_factories import RoleFactory


@pytest.fixture
def first_test_role():
    """
    Fixture for creating and returning a test role.

    This fixture creates a test role using the `RoleFactory.create()` method
    from the movie factories. The created role is returned for use in tests.

    :return: Role: A test role object.
    """
    test_role = RoleFactory.create()
    return test_role
