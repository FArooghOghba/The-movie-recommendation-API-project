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
    'payload', (
        {'username': 'edited_username'},
        {'first_name': 'edited_first_name'},
        {'first_name': ''},
        {'last_name': 'edited_last_name'},
        {'last_name': ''},
        {'bio': 'edited bio.'},
        {'bio': ''},
    )
)
def test_patch_update_user_profile_for_user_info_return_successful(
    api_client, first_test_user, payload
) -> None:

    """
    Test updating the user profile's field for the authenticated user.

    This test case verifies that an authenticated user can successfully
    update their own user profile's field
    (e.g., username, first name, last name, bio) using the PATCH request.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param payload: The payload containing the fields to update.

    :return: None
    """

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )

    assert response.status_code == status.HTTP_202_ACCEPTED

    field = list(payload.keys())[0]
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

    # Get the user's updated profile and the URL of their profile picture
    test_user_profile = Profile.objects.get(user=first_test_user)
    test_user_profile_picture = f'http://testserver{test_user_profile.picture.url}'

    # Check if the response contains the correct URL for the updated profile picture
    assert response.data['picture'] == test_user_profile_picture


def test_patch_update_user_profile_for_remove_picture_return_successful(
    api_client, first_test_user
) -> None:

    """
    Test removing the user profile's picture for an authenticated user.

    This test verifies that an authenticated user can successfully remove
    their own user profile's picture using the PATCH request.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.

    :return: None
    """

    test_user_profile = first_test_user.profile
    test_user_profile_picture = f'http://testserver{test_user_profile.picture.url}'

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    payload = {'picture': ''}

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )

    assert response.status_code == status.HTTP_202_ACCEPTED

    # Get the user's updated profile and the URL of their profile picture
    # after removal
    test_user_profile = Profile.objects.get(user=first_test_user)
    test_user_updated_profile_picture = (f'http://testserver'
                                         f'{test_user_profile.picture.url}')

    # Check if the response contains the correct URL for the updated profile picture
    assert response.data['picture'] == test_user_updated_profile_picture

    # Verify that the updated profile picture URL is different from the original one
    assert response.data['picture'] != test_user_profile_picture


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


def test_patch_update_user_profile_for_add_movie_to_watchlist_return_successful(
    api_client, first_test_user, first_test_movie, second_test_movie,
    third_test_movie
) -> None:

    """
    Test updating the user's profile watchlist successfully.

    This test case verifies that an authenticated user can successfully
    update their own user profile's watchlist by adding a movie using
    the PATCH request.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param first_test_movie: The first test movie.
    :param second_test_movie: The second test movie.
    :param third_test_movie: The third test movie.

    :return: None
    """

    # Add data to the user's profile
    test_user_profile = first_test_user.profile
    test_user_profile.watchlist.add(first_test_movie, second_test_movie)

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    payload = {'watchlist': third_test_movie.slug}

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )
    assert response.status_code == status.HTTP_202_ACCEPTED

    user_profile_watchlist = response.data['watchlist']['movies']
    assert len(user_profile_watchlist) == 3

    movie_added_by_user = third_test_movie.title
    assert movie_added_by_user == user_profile_watchlist[0]['movie_title']


def test_patch_update_profile_for_add_genre_to_favorite_genres_return_successful(
    api_client, first_test_user, first_test_genre, second_test_genre,
    third_test_genre
) -> None:

    """
    Test updating the user's profile favorite_genres successfully.

    This test case verifies that an authenticated user can successfully
    update their own user profile's favorite_genres by adding a genre using
    the PATCH request.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param first_test_genre: The first test genre.
    :param second_test_genre: The second test genre.
    :param third_test_genre: The third test genre.

    :return: None
    """

    # Add data to the user's profile
    test_user_profile = first_test_user.profile
    test_user_profile.favorite_genres.add(first_test_genre, second_test_genre)

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    payload = {'favorite_genres': third_test_genre.slug}

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )
    assert response.status_code == status.HTTP_202_ACCEPTED

    user_profile_favorite_genres = response.data['favorite_genres']['genres']
    assert len(user_profile_favorite_genres) == 3

    genre_added_by_user = third_test_genre.title
    assert genre_added_by_user in user_profile_favorite_genres


def test_update_user_profile_for_remove_movie_from_watchlist_return_successful(
    api_client, first_test_user, first_test_movie, second_test_movie,
    third_test_movie
) -> None:

    """
    Test removing a movie from the user's watchlist.

    This test case verifies that an authenticated user can successfully
    remove a movie from their watchlist using the PATCH request.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param first_test_movie: The first test movie added to the watchlist.
    :param second_test_movie: Another test movie added to the watchlist.
    :param third_test_movie: The movie to be removed from the watchlist.

    :return: None
    """

    # Add data to the user's profile
    test_user_profile = first_test_user.profile
    test_user_profile.watchlist.add(
        first_test_movie, second_test_movie, third_test_movie
    )

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    payload = {'watchlist': third_test_movie.slug}

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )
    assert response.status_code == status.HTTP_202_ACCEPTED

    user_profile_response = response.data['watchlist']['movies']
    assert len(user_profile_response) == 2

    user_profile_response_watchlist = [
        movie['movie_title'] for movie in user_profile_response
    ]
    movie_removed_by_user = third_test_movie.title
    assert movie_removed_by_user not in user_profile_response_watchlist


def test_update_user_profile_for_remove_genre_from_favorite_genres_return_successful(
    api_client, first_test_user, first_test_genre, second_test_genre,
    third_test_genre
) -> None:

    """
    Test removing a genre from the user's favorite genres.

    This test case verifies that an authenticated user can successfully
    remove a genre from their favorite genres using the PATCH request.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param first_test_genre: The first test genre added to favorite genres.
    :param second_test_genre: Another test genre added to favorite genres.
    :param third_test_genre: The genre to be removed from favorite genres.

    :return: None
    """

    # Add data to the user's profile
    test_user_profile = first_test_user.profile
    test_user_profile.favorite_genres.add(
        first_test_genre, second_test_genre, third_test_genre
    )

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    payload = {'favorite_genres': third_test_genre.slug}

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )
    assert response.status_code == status.HTTP_202_ACCEPTED

    profile_favorite_genres_response = response.data['favorite_genres']['genres']
    assert len(profile_favorite_genres_response) == 2

    genre_removed_by_user = third_test_genre.title
    assert genre_removed_by_user not in profile_favorite_genres_response


@pytest.mark.parametrize(
    'payload', (
        {'username': 'edited_username'},
        {'watchlist': 'first_test_movie'},
        {'favorite_genres': 'first_test_genre'},
    )
)
def test_patch_update_user_profile_for_unauthenticated_user_return_error(
    api_client, request, first_test_user, payload
) -> None:

    """
    Test updating the user profile's username, watchlist or favorite genres
    by an unauthenticated user.

    This test case verifies that an unauthenticated user attempting to update
    their user profile's username, watchlist or favorite genre will result
    in an unauthorized error.

    :param api_client: The Django test client.
    :param first_test_user: The first test user.
    :param payload: The payload containing the fields to update.

    :return: None
    """

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    for key, value in payload.items():
        if key in ['watchlist', 'favorite_genres']:
            # Get the object from the fixture name and add its name
            get_test_fixture = request.getfixturevalue(value)
            payload[key] = get_test_fixture.slug

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    'payload', (
        {'username': 'edited_username'},
        {'watchlist': 'first_test_movie'},
        {'favorite_genres': 'first_test_genre'},
    )
)
def test_patch_update_user_profile_for_username_with_different_user_return_error(
    api_client, request, first_test_user, second_test_user, payload
) -> None:

    """
    Test updating another user's profile's username, watchlist or favorite genres.

    This test case verifies that an authenticated user cannot update the
    username, watchlist or favorite genres of another user's profile and
    will result in a forbidden error.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param second_test_user: The second test user whose profile is being updated.
    :param payload: The payload containing the fields to update.

    :return: None
    """

    test_user_profile_before_request = first_test_user.profile

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=second_test_user.username
    )

    for key, value in payload.items():
        if key in ['watchlist', 'favorite_genres']:
            # Get the object from the fixture name and add its name
            get_test_fixture = request.getfixturevalue(value)
            payload[key] = get_test_fixture.slug

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Check that user profile fields have not changed after forbidden status.
    test_user_profile_after_request = Profile.objects.get(user=first_test_user)
    payload_key = list(payload.keys())[0]

    if payload_key == 'username':
        profile_field = test_user_profile_after_request.user.username
        assert profile_field == test_user_profile_before_request.user.username
    else:
        profile_field_after_update = getattr(
            test_user_profile_after_request, payload_key
        )

        profile_field_before_update = getattr(
            test_user_profile_before_request, payload_key
        )

        assert profile_field_after_update == profile_field_before_update


@pytest.mark.parametrize(
    'payload', (
        {'favorite_genres': 'wrong genre slug'},
        {'watchlist': 'wrong movie slug'},
    )
)
def test_patch_update_user_profile_with_wrong_slug_for_genres_and_movie_return_error(
    api_client, first_test_user, first_test_genre, second_test_genre,
    first_test_movie, second_test_movie, payload
) -> None:

    """
    Test updating the user profile with incorrect genre and movie slugs.

    This test case verifies that when an authenticated user attempts to update
    their user profile with incorrect genre and movie slugs in the payload, it
    results in a 404 Not Found error.

    :param api_client: The Django test client.
    :param first_test_user: The first test user for authentication.
    :param first_test_genre: The first test genre for adding to the user's profile.
    :param second_test_genre: The second test genre for adding to the user's profile.
    :param first_test_movie: The first test movie for adding to the user's profile.
    :param second_test_movie: The second test movie for adding to the user's profile.
    :param payload: The payload with incorrect genre or movie slugs.

    :return: None
    """

    # Add data to the user's profile
    test_user_profile = first_test_user.profile
    test_user_profile.favorite_genres.add(first_test_genre, second_test_genre)
    test_user_profile.watchlist.add(first_test_movie, second_test_movie)

    # Authenticate the first test user for the API call
    api_client.force_authenticate(user=first_test_user)

    test_user_profile_url = user_profile_url(
        username=first_test_user.username
    )

    response = api_client.patch(
        path=test_user_profile_url,
        data=payload
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
