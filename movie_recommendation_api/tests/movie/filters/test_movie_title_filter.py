import pytest

from django.urls import reverse

from rest_framework import status

from movie_recommendation_api.movie.selectors import get_movie_list
from movie_recommendation_api.movie.serializers import MovieOutPutModelSerializer

pytestmark = pytest.mark.django_db

MOVIE_LIST_URL = reverse('api:movie:list')


# @pytest.mark.xfail
@pytest.mark.parametrize(
    'filtering_field',
    ('title', 'search'),
)
def test_get_movie_by_filter_exact_title(
    api_client, first_test_movie, second_test_movie, third_test_movie,
    filtering_field
) -> None:

    """
    Test the API endpoint for filtering movies by an exact title match.

    Verifies that the API correctly filters movies based on an exact title match.
    The test creates two movie objects and filters them by a specific title.
    It asserts that the API response contains only one movie with the matching title.

    Test variations:
    - The test is executed twice, once for the 'title' field and once
      for the 'search' field.

    :param api_client: A fixture providing the Django test client for API requests.
    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :param third_test_movie: A fixture providing the third test movie object.
    :param filtering_field: The filtering field for the title,
           first one is 'title' field and the second one 'search' field

    :return: None
    """

    test_movie_filter_title = first_test_movie.title
    filter_params = {filtering_field: test_movie_filter_title}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == test_movie_filter_title


# @pytest.mark.xfail
@pytest.mark.parametrize(
    'filtering_field',
    ('title', 'search'),
)
def test_get_movie_by_filter_partial_title_field(
    api_client, first_test_movie, second_test_movie, third_test_movie,
    filtering_field, django_db_reset_sequences
) -> None:

    """
    Test the API endpoint for filtering movies by a partial title match.

    Verifies that the API correctly filters movies based on a partial title match.
    The test creates two movie objects with titles containing the keyword 'star'.
    It filters the movies by the keyword and asserts that the API response contains
    both movies in the result set.

    :param api_client: A fixture providing the Django test client for API requests.
    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :param third_test_movie: A fixture providing the third test movie object.
    :param filtering_field: The filtering field for the title,
           first one is 'title' field and the second one 'search' field
    :param django_db_reset_sequences: A fixture that resets database sequences
           to prevent primary key conflicts.

    :return: None
    """

    first_test_movie.title = "Star Trek"
    first_test_movie.save()

    second_test_movie.title = "Stardust"
    second_test_movie.save()

    filter_params = {filtering_field: 'star'}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    print(response.content)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2
    assert {result['title'] for result in response.data['results']} == {
        'Star Trek', 'Stardust'
    }


# @pytest.mark.xfail
@pytest.mark.parametrize(
    'filtering_field',
    ('title', 'search'),
)
def test_get_movie_by_filter_case_insensitive_title(
    api_client, api_request, first_test_movie, second_test_movie, filtering_field,
    django_db_reset_sequences
) -> None:

    """
    Test the API endpoint for case-insensitive filtering of movies by title.

    Verifies that the API correctly performs case-insensitive filtering
    of movies by title. The test creates two movie objects with different
    case variations of the same title. It filters the movies by the uppercase
    version of the title and compares the API response with the expected
    filtered movies.

    Test variations:
    - The test is executed twice, once for the 'title' field and once
    for the 'search' field.

    :param api_client: A fixture providing the Django test client for API requests.
    :param api_request: A fixture providing the Django REST framework API request
           factory.
    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :param filtering_field: The filtering field for the title,
           first one is 'title' field and the second one 'search' field.
    :param django_db_reset_sequences: A fixture that resets database sequences
           to prevent primary key conflicts.

    :return: None
    """

    first_test_movie_title = first_test_movie.title

    # Use the uppercase version of the title
    test_title = first_test_movie_title.upper()
    request = api_request.get(path=MOVIE_LIST_URL)
    response = api_client.get(
        path=MOVIE_LIST_URL, request=request, data={filtering_field: test_title}
    )
    assert response.status_code == status.HTTP_200_OK

    # Get the queryset for all movies, prefetching related genres,
    # and deferring unnecessary fields, and adding filters.
    # Annotate the queryset with average ratings and order it by 'id'
    filter_params = {'title': first_test_movie_title}
    filtered_movies = get_movie_list(filters=filter_params)

    filtered_movies_output_serializer = MovieOutPutModelSerializer(
        filtered_movies, many=True, context={'request': request}
    )
    assert response.data['results'] == filtered_movies_output_serializer.data


# @pytest.mark.xfail
@pytest.mark.parametrize(
    'filtering_field',
    ('title', 'search'),
)
def test_get_movies_by_filter_nonexistent_title_should_return_none(
    api_client, first_test_movie, filtering_field
) -> None:

    """
    Test the API endpoint for filtering movies by a nonexistent title.

    Verifies that the API correctly handles the case when no movies
    match the specified title. The test attempts to filter movies
    with a title that does not exist in the database.
    It asserts that the API response contains no movies in the result set.

    :param api_client: A fixture providing the Django test client for API requests.
    :param first_test_movie: A fixture providing the first test movie object.
    :param filtering_field: The filtering field for the title,
           first one is 'title' field and the second one 'search' field
    :return: None
    """

    filter_params = {filtering_field: 'Nonexistent Title'}
    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 0


# @pytest.mark.xfail
@pytest.mark.parametrize(
    'filtering_field',
    ('title', 'search'),
)
def test_get_movies_by_filter_empty_title_should_return_movie_list(
    api_client, first_test_movie, second_test_movie, filtering_field
) -> None:

    """
    Test the API endpoint for filtering movies by an empty title.

    Verifies that the API returns the full list of movies when filtering
    by an empty title.
    The test creates two movie objects and filters them by an empty title.
    It asserts that the API response contains all the movies in the result set.

    :param api_client: A fixture providing the Django test client for API requests.
    :param first_test_movie: A fixture providing the first test movie object.
    :param second_test_movie: A fixture providing the second test movie object.
    :param filtering_field: The filtering field for the title,
           first one is 'title' field and the second one 'search' field.
    :return: None
    """

    filter_params = {filtering_field: ''}

    response = api_client.get(path=MOVIE_LIST_URL, data=filter_params)
    assert response.status_code == status.HTTP_200_OK

    movie_list_count = len((first_test_movie, second_test_movie))
    assert len(response.data['results']) == movie_list_count


# def test_filter_movies_by_multiple_titles(api_client, five_test_movies):
#     titles = [movie.title for movie in five_test_movies]
#     response = api_client.get(
#       path=MOVIE_LIST_URL, data={'title': ','.join(titles)}
#     )
#
#     assert response.status_code == status.HTTP_200_OK
#
#     filtered_movies = Movie.objects.filter(title__in=titles)
#     filtered_movies_output_serializer = MovieOutPutModelSerializer(
#       filtered_movies, many=True
#     )
#     assert response.data['results'] == filtered_movies_output_serializer.data
#
#
#
# @pytest.mark.django_db
# def test_filter_movies_by_cast_crew(api_client, create_movie):
#     # Create sample movies
#     movie1 = create_movie(title="Movie 1", cast_crew="Actor1,Actor2,Actor3")
#     movie2 = create_movie(title="Movie 2", cast_crew="Actor2,Actor3,Actor4")
#     movie3 = create_movie(title="Movie 3", cast_crew="Actor1,Actor4,Actor5")
#
#     url = reverse("movie-list")
#     filter_params = {"cast_crew__in": "Actor1,Actor2"}
#
#     # Perform the request
#     response = api_client.get(url, filter_params)
#
#     # Verify response status code
#     assert response.status_code == status.HTTP_200_OK
#
#     # Verify filtered movies
#     filtered_movies = response.json()["results"]
#     assert len(filtered_movies) == 2
#     assert movie1.title in [movie["title"] for movie in filtered_movies]
#     assert movie2.title in [movie["title"] for movie in filtered_movies]
#
#
# @pytest.mark.django_db
# def test_filter_movies_by_cast_crew_limit(api_client, create_movie):
#     # Create sample movies
#     create_movie(title="Movie 1", cast_crew="Actor1,Actor2,Actor3")
#     create_movie(title="Movie 2", cast_crew="Actor2,Actor3,Actor4")
#     create_movie(title="Movie 3", cast_crew="Actor1,Actor4,Actor5")
#
#     url = reverse("movie-list")
#     filter_params = {"cast_crew__in": "Actor1,Actor2,Actor3,Actor4,Actor5,Actor6"}
#
#     # Perform the request
#     response = api_client.get(url, filter_params)
#
#     # Verify response status code
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
