import logging
import os
from services.omdb_service import OMDBService

logger = logging.getLogger(__name__)

MOVIES_TITLES_DEFAULT = os.getenv('MOVIE_TITLES', 'Andalucia,Sevilla,Malaga')


def fetch_movies(title, total_movies=100, year=None, movie_type=None):
    """
    Fetch a specific number of movies by title with pagination support.
    This function searches for movies using the specified title and optional
    parameters, fetching results across multiple pages if necessary. It
    stops fetching when the desired number of movies is reached or when
    there are no more results.

    Args:
        title (str): The title of the movie to search for.
        total_movies (int): The total number of movies to fetch
        year (str, optional): The year of release to filter the search.
        movie_type (str, optional): The type of result to filter (ex: movie).

    Returns:
        list: A list of dictionaries containing movie information up to the
        specified total_movies.
    """
    movies = []
    page = 1
    while len(movies) < total_movies:
        try:
            response = OMDBService().search_movies(
                title,
                year=year,
                movie_type=movie_type,
                page=page
            )
            page_movies = response.get('movies', [])
            if not page_movies:
                break
            movies.extend(page_movies)

            if (len(movies) >= total_movies or
                response.get('next_page') is None):
                break
            page = response['next_page']
        except ValueError as e:
            logger.error("Error fetching movies: %s", e)
            break
    return movies[:total_movies]


def find_unique_movies(target_count=100):
    """
    Fetch unique movies from the OMDB API until reaching the target count.

    Args:
        target_count (int): The target number of unique movies to fetch.

    Returns:
        list: A list of unique movie data fetched.
    """
    unique_movies = []

    movie_titles = [title.strip() for title in MOVIES_TITLES_DEFAULT.split(',')
                    if title.strip()]

    for title in movie_titles:
        if len(unique_movies) >= target_count:
            logger.info("Target count reached: %d movies", target_count)
            break

        movies = fetch_movies(title)

        for movie in movies:
            if len(unique_movies) < target_count:
                if movie not in unique_movies:
                    unique_movies.append(movie)
            else:
                break

    return unique_movies
