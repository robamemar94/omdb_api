from http.server import BaseHTTPRequestHandler
import json

from api.movie_api import MovieAPI
from services.jwt_service import jwt_required
from api.utils import get_query_params, extract_query_params
from api.api_auth import handle_login


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