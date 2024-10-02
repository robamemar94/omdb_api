import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database.models import Movie, Base
from services.movie_service import find_unique_movies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_path = os.path.join(os.getcwd(), 'local_movies.db')
DATABASE_URL = f'sqlite:///{db_path}'


class DatabaseSession:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()
        self._session = None

    def get_session(self):
        """Get a new session."""
        return self.Session()

    def create_tables(self):
        """Create the tables if they do not already exist."""
        Base.metadata.create_all(self.engine)

    def commit(self, session):
        """Commit the current session."""
        session.commit()

    def rollback(self, session):
        """Rollback the current session."""
        session.rollback()

    def close(self, session):
        """Close the session."""
        session.close()

    def add_element(self, session, element):
        """Add a single element to the database."""
        try:
            session.add(element)
            self.commit(session)
            logger.info(f"Successfully added {element}.")
        except IntegrityError as ie:
            self.rollback(session)
            logger.error(
                "Integrity error occurred while adding element: %s",
                ie
            )
            raise
        except Exception as e:
            self.rollback(session)
            logger.error(
                "An error occurred while adding element: %s",
                e
            )
            raise

    def bulk_save(self, session, elements):
        """Insert a list of elements into the database using bulk save."""
        try:
            session.bulk_save_objects(elements)
            self.commit(session)
            logger.info(
                f"Successfully inserted {len(elements)} elements into the "
                "database."
            )
        except Exception as e:
            self.rollback(session)
            logger.error(
                "An error occurred while bulk saving elements: %s",
                e
            )
            raise

    def delete_element(self, session, element):
        """Delete a single element from the database."""
        try:
            session.delete(element)
            self.commit(session)
            logger.info(f"Successfully deleted {element}.")
        except Exception as e:
            self.rollback(session)
            logger.error(
                "An error occurred while deleting element: %s",
                e
            )
            raise

    def __enter__(self):
        """Enter the runtime context related to this object."""
        self._session = self.Session()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context related to this object."""
        if exc_type is not None:
            self._session.rollback()
        self._session.close()


def initialize_database():
    """
    Initialize the database by creating the movies table and inserting unique
    movies.

    This function checks if the movies table is empty. If it is, it calls a
    function to find unique movies and inserts them into the database.
    """

    db_session = DatabaseSession()

    with db_session as session:
        try:
            if session.query(Movie).count() == 0:
                movies = find_unique_movies()
                movie_objects = [
                    Movie(
                        title=movie_data.get('Title'),
                        year=movie_data.get('Year'),
                        movie_type=movie_data.get('Type'),
                        imdb_id=movie_data.get('imdbID'),
                        poster=movie_data.get('Poster')
                    )
                    for movie_data in movies
                ]
                db_session.bulk_save(session, movie_objects)

        except Exception as e:
            logger.exception(
                "An error occurred during database initialization: %s",
                e
            )
            raise
