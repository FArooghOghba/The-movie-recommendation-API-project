from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator


def validate_review_content(value: str) -> None:
    """
    Custom validator for review content.

    Validates that the review content is not empty or contains only whitespace characters.

    :param value: The review content.
    :raises ValidationError: If the content is empty or contains only whitespace characters.
    """

    if not value or value.strip() == '':
        raise ValidationError(
            "Content cannot be empty or contain only whitespace characters."
        )


validate_content_length = MaxLengthValidator(
    512, "Content exceeds the maximum allowed length."
)
