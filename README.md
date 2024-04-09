# movie_recommendation_api

The Movie Recommendation API Project is a Django REST Framework(DRF)
based web application that allows users to rate movies, write reviews,
and view their activity on the platform through user profiles.
It utilizes popular tools and libraries such as pytest, flake8,
Docker, and Docker Compose for development and deployment.

## Features

- **User Authentication**: Users can register, log in, and manage their profiles.
- **Movie Rating and Review**: Users can rate movies and write reviews for them.
- **User Profile**: Users can view their activity and interactions with the platform through their profiles.
- **Testing**: Pytest is used for testing to ensure the reliability and functionality of the application.
- **Linting and Code Quality**: Flake8 is used for linting to maintain code quality.
- **Containerization**: Docker and Docker Compose are used for containerization and managing development environments.

## Project Setup

To run this project locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/FArooghOghba/The-movie-recommendation-API-project.git
    ```

2. Navigate to the project directory:

    ```bash
    cd The-movie-recommendation-API-project
    ```

3. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv env
    ```

4. Activate the virtual environment:

    - On Windows:

    ```bash
    .\env\Scripts\activate
    ```

    - On macOS and Linux:

    ```bash
    source env/bin/activate
    ```

5. Install dependencies:

    ```bash
    pip install -r requirements_dev.txt
    ```

6. Spin off Docker Compose
   ```bash
   docker compose -f docker-compose.dev.yml up -d
   ```

The project should now be up and running, allowing you to access various API endpoints for movie recommendations.

## APIs

The API offers the following endpoints:

- /api/movies/: Retrieve a list of movies.
- /api/user/{user_id}/ratings/: Retrieve a user's movie ratings.
- /api/user/{user_id}/watchlist/: Retrieve a user's watchlist.
- /api/user/{user_id}/recommendations/: Get movie recommendations
for a specific user based on their interactions and preferences.

## Models

The project uses the following main models:

- Movie: Represents a movie with attributes like title, genre, cast/crew, synopsis, and more.
- UserProfile: Stores user-specific data such as first name, last name, picture, biography, favorite genres, watchlist, ratings, and reviews.
- Rating: Represents a user's rating of a movie, including the user, movie, and rating value.

- Feel free to adapt this README according to your specific project
requirements, providing more details about the API endpoints, models, and any other important information about the project.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the [FALAFEL-WARE LICENSE](https://github.com/FArooghOghba/The-movie-recommendation-API-project/blob/master/LICENSE)