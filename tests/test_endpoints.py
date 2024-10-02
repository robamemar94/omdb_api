import unittest
import threading
import json
from http.server import HTTPServer
import http.client
from unittest.mock import patch

from api.api_server import MovieRequestHandler
from database.database import DatabaseSession, initialize_database
from database.models import User, Movie
from services.omdb_service import OMDBService


class TestMovieAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()
        cls.server = HTTPServer(('localhost', 8000), MovieRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.start()
        cls.db_session = DatabaseSession()
        cls.session = cls.db_session.get_session()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.session.query(User).delete()
        cls.session.query(Movie).delete()
        cls.session.commit()
        cls.db_session.close(cls.session)

    def setUp(self):
        """Prepare each test by setting up the HTTP connection."""
        self.conn = http.client.HTTPConnection('localhost', 8000)


    def test_get_movies(self):
        """Test for the GET /movies endpoint."""

        self.conn.request('GET', '/movies')
        response = self.conn.getresponse()
        self.assertEqual(response.status, 200)
        data = response.read()
        json_data = json.loads(data)

        # Validate the structure of the JSON response
        self.assertIn("status", json_data)
        self.assertEqual(json_data["status"], "success")

        self.assertIn("data", json_data)
        self.assertIn("total_count", json_data["data"])
        self.assertIn("next_page", json_data["data"])
        self.assertIn("prev_page", json_data["data"])
        self.assertIn("movies", json_data["data"])

        # Validate that movies is a list and has at least one movie
        self.assertIsInstance(json_data["data"]["movies"], list)
        self.assertGreater(len(json_data["data"]["movies"]), 0)

    @patch.object(OMDBService, 'fetch_movie_by_title')
    def test_add_movie(self, mock_fetch):
        """Test for the POST /movies endpoint."""
        mock_fetch.return_value = {'Title': 'Betis',
                                   'Year': '2010',
                                   'imdbID': 'tt1375662',
                                   'Poster': 'some_poster_url',
                                   'Type': 'movie'}
        headers = {
            'Content-Type': 'application/json'
        }
        payload = '{"title": "Betis"}'
        self.conn.request('POST', '/movies', payload, headers)
        response = self.conn.getresponse()
        self.assertEqual(response.status, 201)

    @patch('services.jwt_service.verify_jwt')
    def test_delete_movie_authorized(self, mock_verify_jwt):
        """
        Test for the DELETE /movies/{id} endpoint with valid authorization.
        """

        # Mock the verify_jwt to simulate successful verification
        mock_verify_jwt.return_value = 'test_user_id'

        movie_id = 1
        headers = {'Authorization': 'Bearer fake_token'}
        self.conn.request('DELETE', f'/movies/{movie_id}', headers=headers)

        response = self.conn.getresponse()
        self.assertEqual(response.status, 200)

        self.conn.request('GET', f'/movies/{movie_id}')
        get_response = self.conn.getresponse()
        self.assertEqual(get_response.status, 404)

    @patch('services.jwt_service.verify_jwt')
    def test_delete_movie_unauthorized(self, mock_verify_jwt):
        """
        Test for the DELETE /movies/{id} endpoint with invalid authorization.
        """

        mock_verify_jwt.return_value = None  # Simulate invalid token

        movie_id = 1
        headers = {'Authorization': 'Bearer fake_token'}
        self.conn.request('DELETE', f'/movies/{movie_id}', headers=headers)

        response = self.conn.getresponse()
        self.assertEqual(response.status, 401)


if __name__ == '__main__':
    unittest.main()
