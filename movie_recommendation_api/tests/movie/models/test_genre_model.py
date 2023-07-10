import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from movie_recommendation_api.movie.models import Genre


pytestmark = pytest.mark.django_db


def test_create_genre_successful(first_test_genre, second_test_genre) -> None:
    """
    Test that a genre can be created successfully.

    This test creates two genres using the Genre model's create() method
    and verifies that they are created with the expected attributes.
    It checks the string representation of the genres and their slugs.

    :param first_test_genre: A fixture providing the first test genre object.
    :param second_test_genre: A fixture providing the second test genre object.
    :return: None
    """

    third_test_genre = Genre.objects.create(
        title='Third Test Genre Name'
    )
    assert str(third_test_genre) == 'Third Test Genre Name'
    assert third_test_genre.slug == 'third-test-genre-name'

    test_genres = Genre.objects.order_by('id')
    assert list(test_genres) == [
        first_test_genre, second_test_genre, third_test_genre
    ]


def test_create_genre_with_empty_title_return_error(first_test_genre) -> None:
    """
    Test that creating a genre with an empty title raises a validation error.

    This test sets the title of a genre object to an empty string and
    expects a ValidationError to be raised when calling the full_clean() method
    on the genre object.

    :param first_test_genre: A fixture providing the test genre object.
    :return: None
    """

    test_genre = first_test_genre
    test_genre.title = ''  # Empty title

    with pytest.raises(ValidationError):
        test_genre.full_clean()


def test_create_genre_with_exist_title_return_error() -> None:
    """
    Test that creating a genre with an existing title raises an integrity error.

    This test creates a genre with a specific title and then attempts to create
    another genre with the same title, expecting an IntegrityError to be raised.

    Note:
        This test assumes the title field in the Genre model has a unique constraint.

    :return: None
    """

    Genre.objects.create(
        title='First Test Genre Name'
    )

    with pytest.raises(IntegrityError):
        Genre.objects.create(
            title='First Test Genre Name'
        )
