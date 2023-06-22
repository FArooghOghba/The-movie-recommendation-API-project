from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import RefreshToken

from .validators import number_validator, special_char_validator, letter_validator


class InputRegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration input.

    This serializer handles the validation and
    serialization of user registration data,
    including email, bio, password, and confirm_password fields.
    """

    email = serializers.EmailField(max_length=150)
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator(), MinLengthValidator(5)]
    )
    bio = serializers.CharField(max_length=1000, required=False)
    password = serializers.CharField(
        max_length=255,
        write_only=True,
        style={"input_type": "password"},
        validators=[
            number_validator,
            letter_validator,
            special_char_validator,
            MinLengthValidator(limit_value=10)
        ]
    )
    confirm_password = serializers.CharField(
        max_length=255,
        write_only=True,
        style={"input_type": "password"}
    )

    def validate_email(self, email: str) -> str | ValueError:
        """
        Validate the uniqueness of the email.

        This method is called during the validation
        phase to check if the provided email is unique
        in the database. If an existing user with the same
        email is found, a validation error is raised.

        :param email: (str): The email to validate.
        :return: str: The validated email.
        :Raises: serializers.ValidationError: If the email is already taken.
        """
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError(_("email Already Taken"))
        return email

    def validate_username(self, username: str) -> str | ValueError:
        """
        Validate the uniqueness of the username.

        This method is called during the validation
        phase to check if the provided username is
        unique in the database. If an existing user
        with the same username is found, a validation
        error is raised.

        :param username: (str): The username to validate.
        :return: str: The validated username.
        :Raises: serializers.ValidationError: If the username is already taken.
        """

        if get_user_model().objects.filter(username=username).exists():
            raise serializers.ValidationError(_("username Already Taken"))
        return username

    def validate(self, data: dict) -> dict | ValueError:
        """
        Validate the password and confirm_password fields.

        This method is called during the validation phase
        to perform additional validation on the password
        and confirm_password fields. It checks if both fields
        are filled, and if they match each other. If any
        validation error occurs, an exception is raised.

        :param data: (dict): The input data to validate.
        :return: dict: The validated data.
        :Raises: serializers.ValidationError: If password and confirm_password
         validations fail.
        """

        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not username:
            raise serializers.ValidationError(
                _("Please provide a username.")
            )

        if not password or not confirm_password:
            raise serializers.ValidationError(
                _("Please fill password and confirm password.")
            )

        if not password == confirm_password:
            raise serializers.ValidationError(
                _("confirm password is not equal to password.")
            )

        return data


class OutPutRegisterModelSerializer(serializers.ModelSerializer):

    token = serializers.SerializerMethodField("get_token")

    class Meta:
        model = get_user_model()
        fields = (
            "email", "username", "token", "created_at", "updated_at"
        )

    def get_token(self, user):
        data = dict()
        token_class = RefreshToken

        refresh_token = token_class.for_user(user)

        data["refresh_token"] = str(refresh_token)
        data["access_token"] = str(refresh_token.access_token)

        return data
