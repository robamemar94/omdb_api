from http.server import BaseHTTPRequestHandler
import sqlalchemy.exc
import json

from database.models import Movie
from database.database import DatabaseSession
from services.jwt_service import jwt_required
from services.omdb_service import OMDBService
from api.utils import get_query_params, extract_query_params
from api.api_auth import handle_login


class MovieAPI:
    """API class for managing movie operations."""

    @staticmethod
    def get_movies(limit=10, page=1, filters=None, order_by='title'):
        """Retrieve a list of movies from the database with pagination,
        filtering, and ordering. """
        with DatabaseSession() as session:
            offset = (page - 1) * limit
            query = session.query(Movie)

            if filters:
                for key, value in filters.items():
                    if hasattr(Movie, key):
                        query = query.filter(getattr(Movie, key) == value)

            if order_by in ['title', 'year', 'movie_type']:
                query = query.order_by(getattr(Movie, order_by))

            movies = query.limit(limit).offset(offset).all()
            total_count = query.count()

            response = {
                "status": "success",
                "data": {
                    "total_count": total_count,
                    "next_page": page + 1 if (offset + limit) < total_count
                    else None,
                    "prev_page": page - 1 if page > 1 else None,
                    "movies": [movie.to_dict() for movie in movies]
                },
                "message": "Movies retrieved successfully."
            }

            return response, 200

    @staticmethod
    def get_movie_by_id(movie_id):
        """Retrieve a single movie by its ID."""
        with DatabaseSession() as session:
            movie = session.query(Movie).filter(Movie.id == movie_id).first()

            if movie:
                return movie.to_dict(), 200
            else:
                return {'error': 'Movie not found'}, 404

    @staticmethod
    def add_movie(title):
        """Adds a movie to the database using the provided title."""
        with DatabaseSession() as session:
            movie_data = OMDBService().fetch_movie_by_title(title)

            if movie_data:
                movie = Movie(
                    title=movie_data['Title'],
                    year=movie_data['Year'],
                    imdb_id=movie_data['imdbID'],
                    poster=movie_data['Poster'],
                    movie_type=movie_data['Type']
                )

                try:
                    DatabaseSession().add_element(session, movie)
                    return {
                        "message": f"Movie '{title}' added successfully.",
                        "movie": movie.to_dict()
                    }, 201
                except sqlalchemy.exc.IntegrityError:
                    return {"error": f"The movie '{title}' is already "
                                     f"registered in the database."}, 409
            else:
                return {"error": f"Movie '{title}' not found in OMDB."}, 404

    @staticmethod
    def remove_movie(movie_id):
        """Remove a movie from the database by its ID."""
        with DatabaseSession() as session:
            movie = session.query(Movie).filter(Movie.id == movie_id).first()

            if movie:
                DatabaseSession().delete_element(session, movie)
                return {'message': 'Movie removed successfully'}, 200
            else:
                return {'error': 'Movie not found'}, 404


class MovieRequestHandler(BaseHTTPRequestHandler):
    """Handles incoming HTTP requests."""

    def __init__(self, *args, **kwargs):
        self.api = MovieAPI()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        path_parts = self.path.strip('/').split('?')
        resource_path = path_parts[0]

        if resource_path.startswith('movies/') and len(resource_path.split(
            '/')) == 2:
            movie_id = path_parts[0].split('/')[1]
            if not movie_id.isdigit():
                self.send_error(400, 'Invalid movie ID: must be a number')
                return

            response, status_code = self.api.get_movie_by_id(movie_id)
            self.send_http_response(response, status_code)

        elif path_parts[0] == 'movies':
            query_params = get_query_params(
                path_parts[1] if len(path_parts) > 1 else ''
            )
            limit, page, order_by, filters = extract_query_params(query_params)

            response, status_code = self.api.get_movies(
                limit=limit,
                page=page,
                filters=filters,
                order_by=order_by
            )

            self.send_http_response(response, status_code)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')

    @jwt_required
    def do_DELETE(self):
        path_parts = self.path.strip('/').split('/')

        if path_parts[0] == 'movies' and len(path_parts) == 2:
            movie_id = path_parts[1]

            if not movie_id.isdigit():
                self.send_error(400, 'Invalid movie ID: must be a number')
                return

            response, status_code = self.api.remove_movie(movie_id)
            self.send_http_response(response, status_code)

        else:
            self.send_error(404, 'Not Found')

    def do_POST(self):
        path_parts = self.path.strip('/').split('?')

        if path_parts[0] in ['register', 'login']:
            handle_login(self)
        elif path_parts[0] == 'movies':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            if 'title' not in data:
                self.send_error(400, 'Movie title is required')
                return

            title = data['title']
            response, status_code = self.api.add_movie(title)
            self.send_http_response(response, status_code)
        else:
            self.send_error(404, 'Not Found')

    def send_http_response(self, response, status_code):
        """Send HTTP response with the specified response and status code."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(response), 'utf-8'))

    def send_yaml_response(self, filename):
        """Send the OpenAPI YAML specification."""
        self.send_response(200)
        self.send_header('Content-type', 'application/x-yaml')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())