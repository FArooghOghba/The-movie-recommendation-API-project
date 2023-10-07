import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from movie_recommendation_api.movie.models import Review


pytestmark = pytest.mark.django_db


def test_create_review_success(first_test_user, first_test_movie) -> None:
    """
    Test creating a review for a movie.

    This test creates a review using the `Review` model's `create()` method
    and verifies that it is created with the expected attributes.
    It checks the string representation of the review, the associated user
    and movie, and the review content.

    :param first_test_user: A fixture providing the first test user object.
    :param first_test_movie: A fixture providing the first test movie object.
    :return: None
    """

    review_title = 'first test review title'
    review_content = 'This is a valid review content within the allowed length.'

    test_review = Review.objects.create(
        title=review_title,
        spoilers=True,
        user=first_test_user,
        movie=first_test_movie,
        content=review_content
    )

    assert str(test_review) == f"Review for {test_review.movie.title} by" \
                               f"{test_review.user.username} >>" \
                               f"{test_review.title}"

    assert test_review.title == review_title
    assert test_review.spoilers is True
    assert test_review.user == first_test_user
    assert test_review.movie == first_test_movie
    assert test_review.content == review_content


def test_create_reviews_for_movies_success(
    first_test_user, second_test_user, first_test_movie, second_test_movie
) -> None:
    """
    Test creating reviews for multiple movies.

    This test creates reviews for multiple movies using the`Review`model's `create()`
    method and verifies that they are created with the expected attributes.
    It checks the correctness of the associated user, movie, and review content.
    It also checks the correctness of the reviews filtered by movie and the count
    of reviews for each movie.

    :param first_test_user: A fixture providing the first test user object.
    :param second_test_user: A fixture providing the second test user object.
    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :return: None
    """

    first_test_review_for_first_test_movie = Review.objects.create(
        title='first test review title',
        spoilers=True,
        user=first_test_user,
        movie=first_test_movie,
        content="first test review."
    )

    second_test_review_for_first_test_movie = Review.objects.create(
        title='second test review title',
        spoilers=False,
        user=second_test_user,
        movie=first_test_movie,
        content="second test review."
    )

    first_test_review_for_second_movie = Review.objects.create(
        title='third test review title',
        spoilers=False,
        user=first_test_user,
        movie=second_test_movie,
        content="first test review."
    )

    first_test_movie_reviews = Review.objects.filter(movie=first_test_movie)
    assert list(first_test_movie_reviews) == [
        first_test_review_for_first_test_movie,
        second_test_review_for_first_test_movie
    ]

    first_test_movie_reviews_count = first_test_movie.reviews.count()
    assert first_test_movie_reviews_count == len(first_test_movie_reviews)

    second_test_movie_reviews = Review.objects.filter(movie=second_test_movie)
    assert list(second_test_movie_reviews) == [first_test_review_for_second_movie]

    second_test_movie_reviews_count = second_test_movie.reviews.count()
    assert second_test_movie_reviews_count == len(second_test_movie_reviews)


def test_create_reviews_for_users_success(
    first_test_user, second_test_user, first_test_movie, second_test_movie
) -> None:
    """
    Test creating reviews by multiple users for a movie.

    This test creates reviews by multiple users for a movie using
    the `Review` model's `create()` method and verifies that they are
    created with the expected attributes. It checks the correctness of the associated
    user, movie, and review content. It also checks the correctness of the reviews
    filtered by user and the count of reviews for each user.

    :param first_test_user: A fixture providing the first test user object.
    :param second_test_user: A fixture providing the second test user object.
    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :return: None
    """

    first_user_review_for_first_movie = Review.objects.create(
        title='first test review title',
        spoilers=True,
        user=first_test_user,
        movie=first_test_movie,
        content="first test review."
    )

    second_user_review_for_first_movie = Review.objects.create(
        title='second test review title',
        spoilers=False,
        user=second_test_user,
        movie=first_test_movie,
        content="second test review."
    )

    first_user_review_for_second_movie = Review.objects.create(
        title='third test review title',
        spoilers=False,
        user=first_test_user,
        movie=second_test_movie,
        content="first test review."
    )

    # Assertions for first test movie reviews

    first_test_user_reviews = Review.objects.filter(user=first_test_user)
    assert list(first_test_user_reviews) == [
        first_user_review_for_first_movie, first_user_review_for_second_movie
    ]

    first_test_user_reviews_count = first_test_user.reviews.count()
    assert first_test_user_reviews_count == len(first_test_user_reviews)

    # Assertions for second test movie reviews

    second_test_user_reviews = Review.objects.filter(user=second_test_user)
    assert list(second_test_user_reviews) == [second_user_review_for_first_movie]

    second_test_user_reviews_count = second_test_user.reviews.count()
    assert second_test_user_reviews_count == len(second_test_user_reviews)


def test_create_review_with_max_length_content(
    first_test_user, first_test_movie
) -> None:

    """
    Test creating a review with content at the maximum allowed length.

    This test case creates a review with content that is exactly the maximum allowed
    length for the content field. It ensures that the review is created successfully
    without raising any validation errors.

    :param first_test_user: A fixture providing the first test user object.
    :param first_test_movie: A fixture providing the first test movie object.
    :return: None
    """

    content = 'A' * Review._meta.get_field('content').max_length

    test_review = Review.objects.create(
        user=first_test_user,
        movie=first_test_movie,
        content=content
    )

    assert test_review.content == content


@pytest.mark.parametrize(
    'title',
    (None, '', '   ')
)
def test_create_review_with_wrong_title_return_error(
    first_test_user, first_test_movie, title
) -> None:

    """
    Test creating a review with missing title.

    This test verifies that creating a review without providing the title
    raises a ValidationError or IntegrityError.

    :param first_test_user: A fixture providing the first test user object.
    :param first_test_movie: A fixture providing the first test movie object.
    :param title: The title of the review, which is set to a value
           that is None, an empty string, or a string containing only
           whitespace characters.
    :return: None
    """

    with pytest.raises((ValidationError, IntegrityError)):
        test_review = Review.objects.create(
            title=title,
            spoilers=True,
            user=first_test_user,
            movie=first_test_movie,
            content='first test review content.'
        )
        test_review.full_clean()


@pytest.mark.parametrize(
    'content',
    (None, '', '   ')
)
def test_create_review_with_missing_content_raises_error(
    first_test_user, first_test_movie, content
) -> None:

    """
    Test creating a review with missing content.

    This test verifies that creating a review without providing the content
    raises a ValidationError or IntegrityError.

    :param first_test_user: A fixture providing the first test user object.
    :param first_test_movie: A fixture providing the first test movie object.
    :param content: The content of the review, which is set to a value
           that is None, an empty string, or a string containing only
           whitespace characters.
    :return: None
    """

    with pytest.raises((ValidationError, IntegrityError)):
        test_review = Review.objects.create(
            user=first_test_user,
            movie=first_test_movie,
            content=content
        )
        test_review.full_clean()


@pytest.mark.parametrize(
    'content',
    [
        # Exceeds max_length by 1
        'A' * (Review._meta.get_field('content').max_length + 1),

        # Arbitrarily long content
        'A' * 1000,
    ]
)
def test_create_review_with_exceeded_max_length_content_raises_error(
    first_test_user, first_test_movie, content
) -> None:
    """
    Test creating a review with content that exceeds the allowed max_length.

    This parametrized test case tests creating a review with content that exceeds the
    allowed max_length for the content field. It verifies that a ValidationError is
    raised as expected, indicating that the content is too long.

    :param first_test_user: A fixture providing the first test user object.
    :param first_test_movie: A fixture providing the first test movie object.
    :param content: The content for the review, which exceeds the max_length.
    :return: None
    """

    with pytest.raises(ValidationError):
        test_review = Review.objects.create(
            user=first_test_user,
            movie=first_test_movie,
            content=content
        )
        test_review.full_clean()
        test_review.save()


def test_delete_review_for_user_success(first_test_review) -> None:
    """
    Test deleting a review.

    This test deletes a review and verifies that it is successfully deleted
    from the database.

    :param first_test_review: A fixture providing the first test review object.
    :return: None
    """
    test_review = first_test_review
    test_review_id = first_test_review.id

    test_review.delete()

    with pytest.raises(Review.DoesNotExist):
        Review.objects.get(id=test_review_id)
