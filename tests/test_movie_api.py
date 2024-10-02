import unittest
from unittest.mock import patch

from api.api_server import MovieAPI
from database.models import Movie
from database.database import DatabaseSession
from services.omdb_service import OMDBService


class TestAddMovieAPI(unittest.TestCase):
    """Tests for the add movie endpoint."""

    @classmethod
    def setUpClass(cls):
        cls.api = MovieAPI()
        cls.db_session = DatabaseSession()
        cls.session = cls.db_session.get_session()

    @classmethod
    def tearDownClass(cls):
        cls.session.query(Movie).delete()
        cls.session.commit()
        cls.db_session.close(cls.session)

    @patch.object(OMDBService, 'fetch_movie_by_title')
    def test_add_movie_success(self, mock_fetch_movie):
        """Test adding a movie successfully."""
        mock_fetch_movie.return_value = {
            'Title': 'Real Betis',
            'Year': '2010',
            'imdbID': 'tt1375662',
            'Poster': 'some_poster_url',
            'Type': 'movie'
        }

        title = 'Real Betis'
        response, status_code = self.api.add_movie(title)

        self.assertEqual(status_code, 201)
        self.assertIn("message", response)
        self.assertIn("movie", response)
        self.assertEqual(response["movie"]["title"], title)

    @patch.object(OMDBService, 'fetch_movie_by_title')
    def test_add_movie_not_found(self, mock_fetch_movie):
        """Test adding a movie that is not found."""
        mock_fetch_movie.return_value = None

        title = 'NonExistentMovie'
        response, status_code = self.api.add_movie(title)

        self.assertEqual(status_code, 404)
        self.assertIn("error", response)
        self.assertEqual(
            response["error"],
            "Movie 'NonExistentMovie' not found in OMDB."
        )

    @patch.object(OMDBService, 'fetch_movie_by_title')
    def test_add_movie_already_exists(self, mock_fetch_movie):
        """Test adding a movie that already exists in the database."""
        mock_fetch_movie.return_value = {
            'Title': 'Inception',
            'Year': '2010',
            'imdbID': 'tt1375666',
            'Poster': 'some_poster_url',
            'Type': 'movie'
        }

        title = 'Inception'
        self.api.add_movie(title)

        response, status_code = self.api.add_movie(title)

        self.assertEqual(status_code, 409)
        self.assertIn("error", response)
        self.assertEqual(
            response["error"],
            "The movie 'Inception' is already registered in the database."
        )


class TestGetMovieAPI(unittest.TestCase):
    """Tests for the get movie endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.api = MovieAPI()
        cls.db_session = DatabaseSession()
        cls.session = cls.db_session.get_session()

    @classmethod
    def tearDownClass(cls):
        cls.session.query(Movie).delete()
        cls.session.commit()
        cls.db_session.close(cls.session)

    def test_get_movie_by_id_success(self):
        """Test retrieving a movie by its ID."""
        title = 'Inception'
        self.api.add_movie(title)

        movie = self.session.query(Movie).filter(Movie.title == title).first()
        response, status_code = self.api.get_movie_by_id(movie.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(response['title'], title)

    def test_get_movie_by_id_not_found(self):
        """Test retrieving a movie that does not exist."""
        response, status_code = self.api.get_movie_by_id(9999)
        self.assertEqual(status_code, 404)
        self.assertIn("error", response)
        self.assertEqual(response["error"], "Movie not found")


class TestRemoveMovieAPI(unittest.TestCase):
    """Tests for the remove movie endpoint."""

    @classmethod
    def setUpClass(cls):
        cls.api = MovieAPI()
        cls.db_session = DatabaseSession()
        cls.session = cls.db_session.get_session()

    @classmethod
    def tearDownClass(cls):
        cls.session.query(Movie).delete()
        cls.session.commit()
        cls.db_session.close(cls.session)

    def test_remove_movie_success(self):
        """Test removing a movie successfully."""
        title = 'Inception'
        self.api.add_movie(title)

        movie = self.session.query(Movie).filter(Movie.title == title).first()
        response, status_code = self.api.remove_movie(movie.id)

        self.assertEqual(status_code, 200)
        self.assertIn("message", response)
        self.assertEqual(response["message"], "Movie removed successfully")

    def test_remove_movie_not_found(self):
        """Test removing a movie that does not exist."""
        response, status_code = self.api.remove_movie(9999)
        self.assertEqual(status_code, 404)
        self.assertIn("error", response)
        self.assertEqual(response["error"], "Movie not found")


if __name__ == '__main__':
    unittest.main()
