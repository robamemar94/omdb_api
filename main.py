from database.database import initialize_database
from api.api_server import MovieRequestHandler
from http.server import HTTPServer


def run(server_class=HTTPServer, handler_class=MovieRequestHandler, port=8080):
    """Run the HTTP server."""
    initialize_database()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
