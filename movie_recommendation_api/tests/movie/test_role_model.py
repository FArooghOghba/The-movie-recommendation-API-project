import pytest

from django.core.exceptions import ValidationError

from movie_recommendation_api.movie.models import Role


pytestmark = pytest.mark.django_db


def test_create_role_successful(first_test_movie, first_test_cast) -> None:
    """
    Test that a role can be created successfully with a name,
    cast/crew member, and movie.

    This test creates a role object by calling the Role.objects.create()
    method with a name, cast/crew member, and movie. It then calls the full_clean()
    method to ensure the object passes validation. Finally, it asserts that
    the string representation of the role matches the provided name and that
    the cast/crew member and movie fields are set correctly.

    :param first_test_movie: A fixture providing the test movie object.
    :param first_test_cast: A fixture providing the test cast/crew member object.
    :return: None
    """

    test_role = Role.objects.create(
        name='First Role Name',
        cast_crew=first_test_cast,
        movie=first_test_movie
    )
    test_role.full_clean()

    assert str(test_role) == 'First Role Name'
    assert test_role.cast_crew == first_test_cast
    assert test_role.movie == first_test_movie


def test_create_role_without_name_returns_error(first_test_movie) -> None:
    """
    Test that creating a role without a name raises a validation error.

    This test attempts to create a role object by calling
    the Role.objects.create() method without providing a name.
    It uses the first cast/crew member from the movie fixture and
    the test movie object. The test expects a ValidationError to be raised.

    :param first_test_movie: A fixture providing the test movie object.
    :return: None
    """

    test_cast_crew = first_test_movie.cast_crew.first()

    with pytest.raises(ValidationError):
        test_role = Role.objects.create(
            cast_crew=test_cast_crew,
            movie=first_test_movie
        )
        test_role.full_clean()
