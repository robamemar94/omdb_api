import os
import requests
import logging

logger = logging.getLogger(__name__)


class OMDBService:
    """
    A service class to interact with the OMDB API.
    """
    BASE_URL = 'http://www.omdbapi.com/'

    def __init__(self):
        self.api_key = os.getenv('OMDB_API_KEY')
        if not self.api_key:
            logger.critical(
                "OMDB API key is not set in the environment variables."
            )
            raise ValueError("OMDB API key is required.")

    def fetch_movie_by_id(self, imdb_id):
        """
        Fetch a movie's details by IMDb ID.

        Args:
            imdb_id (str): The IMDb ID of the movie to fetch.

        Returns:
            dict: A dictionary containing movie information.

        Raises:
            ValueError: If the API response indicates an error.
        """
        params = {
            'i': imdb_id,
            'apikey': self.api_key
        }
        return self._fetch_movie_data(params)

    def fetch_movie_by_title(self, title, year=None, movie_type=None):
        """
        Fetch a movie's details by title.

        Args:
            title (str): The title of the movie to search for.
            year (str, optional): The year of release.
            movie_type (str, optional): The type of result (movie, series).

        Returns:
            dict: A dictionary containing movie information.

        Raises:
            ValueError: If the API response indicates an error.
        """
        params = {
            't': title,
            'apikey': self.api_key
        }

        if year:
            params['y'] = year
        if movie_type:
            params['type'] = movie_type

        return self._fetch_movie_data(params)

    def search_movies(self, title, year=None, movie_type=None, page=1):
        """
        Search for movies by title with optional parameters.

        Args:
            title (str): The title of the movie to search for.
            year (str, optional): The year of release.
            movie_type (str, optional): The type of result (movie, series).
            page (int, optional): The page number to return (default is 1).

        Returns:
            dict: A dictionary containing a list of dictionaries with movie
            information and the total number of results.

        Raises:
            ValueError: If the API response indicates an error.
        """
        params = {
            's': title,
            'apikey': self.api_key,
            'page': page
        }

        if year:
            params['y'] = year
        if movie_type:
            params['type'] = movie_type

        response = self._fetch_movie_data(params)

        if response.get('Response') == 'False':
            raise ValueError(
                f"API Error: {response.get('Error', 'Unknown error')}"
            )

        total_results = int(response.get('totalResults', 0))
        movies = response.get('Search', [])
        next_page = (
            page + 1 if len(movies) + (page - 1) * 10 < total_results else
            None)

        return {
            'total_results': total_results,
            'movies': movies,
            'next_page': next_page
        }

    def _fetch_movie_data(self, params):
        """
        Helper function to fetch movie data from OMDB API.

        Args:
            params (dict): Parameters to pass to the API.

        Returns:
            dict: API response data.

        Raises:
            ValueError: If the API response indicates an error.
        """
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()

            if 'Error' in data:
                logger.error("Error fetching data: %s", data['Error'])
                raise ValueError(data['Error'])

            return data

        except requests.RequestException as e:
            logger.error("Request failed: %s", e)
            raise
        except ValueError as ve:
            logger.error("ValueError: %s", ve)
            raise
