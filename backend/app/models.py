
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Table,
)
from sqlalchemy.orm import relationship

from app.database import Base


# Промежуточная таблица для связи фильмов и жанров
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column(
        "movie_id",
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        Integer,
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# Пользователи
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    ratings = relationship("Rating", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")


# Фильмы
class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    release_year = Column(Integer)
    director = Column(String(150))
    poster_url = Column(String(500))

    ratings = relationship("Rating", back_populates="movie")
    favorites = relationship("Favorite", back_populates="movie")

    genres = relationship(
        "Genre",
        secondary=movie_genres,
        back_populates="movies",
    )


# Жанры
class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    movies = relationship(
        "Movie",
        secondary=movie_genres,
        back_populates="genres",
    )


# Оценки фильмов
class Rating(Base):
    __tablename__ = "ratings"

    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 10", name="check_score"),
        UniqueConstraint("user_id", "movie_id", name="unique_user_movie_rating"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    score = Column(Integer, nullable=False)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")


# Избранное
class Favorite(Base):
    __tablename__ = "favorites"

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_user_movie_favorite"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)

    user = relationship("User", back_populates="favorites")
    movie = relationship("Movie", back_populates="favorites")
