import os

import pytest

from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from movie_recommendation_api.movie.models import CastCrew, cast_crew_image_file_path


pytestmark = pytest.mark.django_db


def test_create_cast_successful(
    first_test_cast, second_test_cast,
    first_test_career_for_cast, second_test_career_for_cast
) -> None:
    """
    Test that a cast member can be created successfully.

    This test creates two cast members using the CastCrew model's create() method
    and verifies that they are created with the expected attributes.
    It checks the string representation of the cast members and their careers.

    :param first_test_cast: A fixture providing the first test cast member object.
    :param second_test_cast: A fixture providing the second test cast member object.
    :param first_test_career_for_cast: A fixture providing a test career object for
    the first cast member.
    :param second_test_career_for_cast: A fixture providing a test career object for
    the second cast member.
    :return: None
    """

    third_test_cast = CastCrew.objects.create(
        name='Third Test Name',
        cast=True
    )
    third_test_cast.careers.add(
        first_test_career_for_cast, second_test_career_for_cast
    )

    assert str(third_test_cast) == 'Third Test Name'
    assert third_test_cast.crew is False

    third_test_cast_careers = third_test_cast.careers.order_by('id')
    assert list(third_test_cast_careers) == [
        first_test_career_for_cast, second_test_career_for_cast
    ]

    test_casts = CastCrew.objects.filter(cast=True).order_by('id')
    assert list(test_casts) == [first_test_cast, second_test_cast, third_test_cast]


def test_create_cast_with_empty_name_return_error(first_test_cast) -> None:
    """
    Test that creating a cast member with an empty name raises a validation error.

    This test sets the name field of a cast member object to an empty string and
    attempts to call the full_clean() method, expecting a ValidationError
    to be raised.

    :param first_test_cast: A fixture providing the test cast member object.
    :return: None
    """

    test_cast = first_test_cast
    test_cast.name = ''  # Empty title

    with pytest.raises(ValidationError):
        test_cast.full_clean()


def test_create_crew_successful(
    first_test_crew, second_test_crew,
    first_test_career_for_crew, second_test_career_for_crew
) -> None:
    """
     Test that a crew member can be created successfully.

    This test creates two crew members using the CastCrew model's create() method
    and verifies that they are created with the expected attributes.
    It checks the string representation of the crew members, their careers, and their
    cast/crew flags.

    :param first_test_crew: A fixture providing the first test crew member object.
    :param second_test_crew: A fixture providing the second test crew member object.
    :param first_test_career_for_crew: A fixture providing a test career object for
    the first crew member.
    :param second_test_career_for_crew: A fixture providing a test career object for
    the second crew member.

    :return: None
    """

    third_test_crew = CastCrew.objects.create(
        name='Third Test Name',
        crew=True
    )
    third_test_crew.careers.add(
        first_test_career_for_crew, second_test_career_for_crew
    )

    assert str(third_test_crew) == 'Third Test Name'
    assert third_test_crew.crew is True
    assert third_test_crew.cast is False

    third_test_crew_careers = third_test_crew.careers.order_by('id')
    assert list(third_test_crew_careers) == [
        first_test_career_for_crew, second_test_career_for_crew
    ]

    test_crews = CastCrew.objects.filter(crew=True).order_by('id')
    assert list(test_crews) == [first_test_crew, second_test_crew, third_test_crew]


def test_create_cast_crew_with_exist_name_return_error(
        first_test_career_for_cast, second_test_career_for_cast
) -> None:
    """
    Test that creating a cast/crew member with an existing name raises
    an integrity error.

    This test creates a cast/crew member with a specific name and cast/crew flag
    and then attempts to create another cast/crew member with the same name and
    a different career, expecting an IntegrityError to be raised.

    Note:
        This test assumes the name field in the CastCrew model has
        a unique constraint.

    :param first_test_career_for_cast: A fixture providing a test career object for
    the first cast member.
    :param second_test_career_for_cast: A fixture providing a test career object for
    the second cast member.

    :return: None
    """

    first_test_cast_crew = CastCrew.objects.create(
        name='First Test Name',
        cast=True,
    )
    first_test_cast_crew.careers.add(first_test_career_for_cast)

    with pytest.raises(IntegrityError):
        second_test_cast_crew = CastCrew.objects.create(
            name='First Test Name',
            crew=True
        )
        second_test_cast_crew.careers.add(second_test_career_for_cast)


@patch(target='movie_recommendation_api.movie.models.uuid.uuid4')
def test_cast_crew_create_file_name_uuid_for_image_path(mock_uuid):
    """
    Test generating the image path for cast and crew images.

    This test mocks the UUID generation using the patch decorator
    to ensure a consistent UUID value. It calls the cast_crew_image_file_path()
    function with a dummy file name. The expected file path is constructed
    based on UUID values. The test asserts that the generated file path matches
    the expected value.

    :param mock_uuid: A mock object for generating UUID values.
    :return: None
    """

    uuid = 'test_uuid'
    mock_uuid.return_value = uuid
    file_path = cast_crew_image_file_path(None, 'test-image.jpg')

    expected_file_path = os.path.normpath(f'uploads/cast_crew_image/{uuid}.jpg')

    assert file_path == expected_file_path
