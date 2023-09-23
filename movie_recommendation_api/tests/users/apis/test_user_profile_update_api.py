import pytest

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.users.models import Profile

pytestmark = pytest.mark.django_db


def user_profile_url(username: str) -> str:

    """
    Generate the URL for a user's profile.

    :param username: (str) The username of the user.

    :returns str: The URL for the user's profile.
    """

    return reverse(viewname='api:users:profile', args=[username])


@pytest.mark.parametrize(
    'field, edited_value', (
        ['username', 'edited_username'],
        ['first_name', 'edited_first_name'],
        ['last_name', 'edited_last_name'],
        ['bio', 'edited bio.'],
    )
)
def test_patch_update_user_profile_for_user_info_return_successful(
    api_client, first_test_user, field, edited_value
) -> None:

    """
    Test updating the user profile's field for the authenticated user.

    This test case verifies that an authenticated user can successfully
    update their own user profile's field
    (e.g., username, first name, last name, bio) using the PATCH request.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param field: The name of the field to update.
    :param edited_value: The new value for the field.

    :return: None
    """

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    payload = {field: edited_value}

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data[field] == payload[field]


def test_patch_update_user_profile_picture_return_successful(
    api_client, first_test_user, first_test_picture_payload
) -> None:

    """
    Test updating the user profile's picture for the authenticated user.

    This test case verifies that an authenticated user can successfully
    update their own user profile's picture using the PATCH request.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param first_test_picture_payload (dict): A dictionary containing
    the picture data.

    :return: None
    """

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    response = api_client.patch(
        path=test_user_profile_url,
        data=first_test_picture_payload
    )

    assert response.status_code == status.HTTP_202_ACCEPTED

    test_user_profile = Profile.objects.get(user=first_test_user)
    test_user_profile_picture = f'http://testserver{test_user_profile.picture.url}'
    assert response.data['picture'] == test_user_profile_picture


def test_patch_update_user_profile_for_multiple_user_info_fields_return_successful(
    api_client, first_test_user
) -> None:

    """
    Test updating multiple user profile fields for the authenticated user.

    This test case verifies that an authenticated user can successfully
    update multiple fields of their own user profile
    (e.g., first name, last name, bio) using the PATCH request.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.

    :return: None
    """

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    payload = {
        'first_name': 'edited_first_name',
        'last_name': 'edited_last_name',
        'bio': 'new edited bio.',
    }

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )

    assert response.status_code == status.HTTP_202_ACCEPTED

    for field, value in payload.items():
        assert response.data[field] == value


# def test_patch_update_user_profile_for_watchlist_return_successful(
#     api_client, first_test_user, first_test_movie, second_test_movie,
#     third_test_movie
# ) -> None:
#
#     """
#
#     """
#
#     # Add data to the user's profile
#     test_user_profile = first_test_user.profile
#     test_user_profile.watchlist.add(first_test_movie, second_test_movie)
#
#     # Authenticate the first test user for the API call
#     api_client.force_authenticate(user=first_test_user)
#
#     test_user_profile_url = user_profile_url(
#         username=first_test_user.username
#     )
#
#     payload = {'watchlist': third_test_movie.slug}
#
#     response = api_client.patch(
#         path=test_user_profile_url,
#         data=payload
#     )
#     assert response.status_code == status.HTTP_202_ACCEPTED
#
#     user_profile_watchlist = response.data['watchlist']
#     assert len(user_profile_watchlist) == 3
#
#     movie_added_by_user = user_profile_watchlist[0]['slug']
#     assert movie_added_by_user == payload['watchlist']


def test_patch_update_user_profile_for_unauthenticated_user_return_error(
    api_client, first_test_user
) -> None:

    """
    Test updating the user profile's username by an unauthenticated user.

    This test case verifies that an unauthenticated user attempting to update
    their user profile's username will result in an unauthorized error.

    :param api_client: The Django test client.
    :param first_test_user: The first test user.

    :return: None
    """

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    payload = {'username': 'edited_username'}

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_patch_update_user_profile_for_username_with_different_user_return_error(
    api_client, first_test_user, second_test_user
) -> None:

    """
    Test updating another user's profile's username.

    This test case verifies that an authenticated user cannot update the
    username of another user's profile and will result in a forbidden error.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param second_test_user: The second test user whose profile is being updated.

    :return: None
    """

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=second_test_user.username
    )

    payload = {'username': 'edited_username'}

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
