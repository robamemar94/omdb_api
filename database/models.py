from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    year = Column(String(4), nullable=True)
    movie_type = Column(String(50), nullable=True)
    imdb_id = Column(String(20), nullable=True, unique=True)
    poster = Column(String(255), nullable=True)

    def __repr__(self):
        return (
            f"<Movie(title={self.title}, year={self.year}, "
            f"type={self.movie_type}, imdb_id={self.imdb_id}, "
            f"poster={self.poster})>"
        )

    def to_dict(self):
        movie_dict = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        return movie_dict


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }