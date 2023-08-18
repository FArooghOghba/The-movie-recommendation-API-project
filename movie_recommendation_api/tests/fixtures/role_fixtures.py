import pytest

from movie_recommendation_api.tests.factories.movie_factories import RoleFactory


@pytest.fixture
def first_test_role(first_test_career_for_cast):
    """
    Fixture for creating and returning a test role.

    This fixture creates a test role using the `RoleFactory.create()` method
    from the movie factories. The created role is returned for use in tests.

    :return: Role: A test role object.
    """
    test_role = RoleFactory.create(
        careers=[first_test_career_for_cast],
    )
    return test_role


@pytest.fixture
def second_test_role(second_test_career_for_crew):
    """
    Fixture for creating and returning a test role.

    This fixture creates a test role using the `RoleFactory.create()` method
    from the movie factories. The created role is returned for use in tests.

    :return: Role: A test role object.
    """
    test_role = RoleFactory.create(
        careers=[second_test_career_for_crew],
    )
    return test_role
