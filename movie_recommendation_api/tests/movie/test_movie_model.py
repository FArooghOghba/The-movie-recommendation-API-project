"""
Tests for Movie Models.
"""

import os

import pytest

from unittest.mock import patch

from django.core.exceptions import ValidationError

from movie_recommendation_api.movie.models import (
    Movie, movie_poster_file_path
)

from datetime import date, timedelta
from decimal import Decimal


pytestmark = pytest.mark.django_db


def test_create_movie_successful(
    first_test_genre, second_test_genre, first_test_cast, first_test_crew
) -> None:
    """
    Test that a movie can be created successfully.

    This test creates a movie using the Movie model's create() method
    and verifies that it is created with the expected attributes.
    It checks the string representation of the movie,
    its slug, rating, poster, trailer, runtime, and release date.
    It also verifies the associated genres and cast/crew members.

    :param first_test_genre: A fixture providing the first test genre object.
    :param second_test_genre: A fixture providing the second test genre object.
    :param first_test_cast: A fixture providing the first test cast member object.
    :param first_test_crew: A fixture providing the first test crew member object.
    :return: None
    """

    runtime = timedelta(hours=2, minutes=10)

    test_movie = Movie.objects.create(
        title='Test Movie Name',
        synopsis='Test synopsis',
        rating=Decimal(4.5),
        poster='poster.jpg',
        trailer='https://www.example.com/trailer',
        runtime=runtime,
        release_date=date(2022, 1, 1),
    )
    test_movie.genre.add(first_test_genre, second_test_genre)
    test_movie.cast_crew.add(first_test_cast, first_test_crew)

    assert str(test_movie) == 'Test Movie Name'
    assert test_movie.slug == 'test-movie-name'
    assert test_movie.rating == 4.5
    assert test_movie.poster == 'poster.jpg'
    assert test_movie.trailer == 'https://www.example.com/trailer'
    assert test_movie.runtime == runtime
    assert test_movie.release_date == date(2022, 1, 1)

    test_movie_genres = test_movie.genre.order_by('id')
    assert list(test_movie_genres) == [first_test_genre, second_test_genre]

    test_movie_cast_crews = test_movie.cast_crew.order_by('id')
    assert list(test_movie_cast_crews) == [first_test_cast, first_test_crew]


def test_create_movie_with_invalid_rating_return_error(first_test_movie) -> None:
    """
    Test that creating a movie with an invalid rating raises a validation error.

    This test sets an invalid rating value (10.5) on the first_test_movie fixture
    object and calls the full_clean() method. It expects a ValidationError
    to be raised.

    :param first_test_movie: A fixture providing the test movie object.
    :return: None
    """

    test_movie = first_test_movie
    test_movie.rating = 10.5  # Set an invalid rating value

    with pytest.raises(ValidationError):
        test_movie.full_clean()


def test_create_movie_with_empty_title_return_error(first_test_movie) -> None:
    """
    Test that creating a movie with an empty title raises a validation error.

    This test sets an empty title on the first_test_movie fixture object and
    calls the full_clean() method. It expects a ValidationError to be raised.

    :param first_test_movie: A fixture providing the test movie object.
    :return: None
    """

    test_movie = first_test_movie
    test_movie.title = ''  # Empty title

    with pytest.raises(ValidationError):
        test_movie.full_clean()


def test_create_movie_with_exists_title_return_error(
    first_test_movie, second_test_movie
) -> None:
    """
    Test that creating a movie with an existing title raises a validation error.

    This test sets the title of the first_test_movie fixture object
    to the title of the second_test_movie fixture object, creating
    a case where the title already exists. It then calls the full_clean()
    method and expects a ValidationError to be raised.

    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :return: None
    """

    test_movie = first_test_movie
    test_movie.title = second_test_movie.title  # Exists title

    with pytest.raises(ValidationError):
        test_movie.full_clean()


@patch(target='movie_recommendation_api.movie.models.uuid.uuid4')
def test_movie_poster_create_file_name_uuid_for_image_path(
    mock_uuid, first_test_movie
) -> None:
    """
    Test generating the image path for a movie poster.

    This test mocks the UUID generation using the patch decorator
    to ensure a consistent UUID value. It calls the movie_poster_file_path() function
    with the first_test_movie fixture object and a dummy file name.
    The expected file path is constructed based on the year, month, and UUID values.
    The test asserts that the generated file path matches the expected value.

    :param mock_uuid: A mock object for generating UUID values.
    :param first_test_movie: A fixture providing the test movie object.
    :return: None
    """

    uuid = 'test_uuid'
    mock_uuid.return_value = uuid
    file_path = movie_poster_file_path(first_test_movie, 'test-poster.jpg')

    year = first_test_movie.release_date.year
    month = first_test_movie.release_date.month
    expected_file_path = os.path.normpath(
        f'uploads/movie-poster/{year}/{month}/{uuid}.jpg'
    )

    assert file_path == expected_file_path
