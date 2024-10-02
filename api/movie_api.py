import sqlalchemy.exc

from database.models import Movie
from database.database import DatabaseSession
from services.omdb_service import OMDBService


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