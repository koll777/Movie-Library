from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import text
from sqlalchemy.orm import Session, selectinload

from app.database import engine, get_db
from app.models import User, Movie, Genre, Rating, Favorite
from app.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    MovieCreate,
    MovieUpdate,
    MovieResponse,
    GenreCreate,
    GenreResponse,
)
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


app = FastAPI(title="Кинотека")
bearer_scheme = HTTPBearer(auto_error=False)


@app.get("/")
def home():
    return {
        "message": "Кинотека работает!"
    }

@app.get("/movies", response_model=list[MovieResponse])
def get_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).options(
        selectinload(Movie.genres)
    ).all()

    return movies


@app.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).options(
        selectinload(Movie.genres)
    ).filter(Movie.id == movie_id).first()

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )

    return movie


@app.post(
    "/movies",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED
)
def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db)
):
    genres = []
    if movie_data.genre_ids:
        genres = db.query(Genre).filter(
            Genre.id.in_(movie_data.genre_ids)
        ).all()

        if len(genres) != len(movie_data.genre_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Один или несколько жанров не найдены"
            )

    new_movie = Movie(
        title=movie_data.title,
        description=movie_data.description,
        release_year=movie_data.release_year,
        director=movie_data.director,
        poster_url=movie_data.poster_url,
        genres=genres,
    )

    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)

    return new_movie


@app.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).options(
        selectinload(Movie.genres)
    ).filter(Movie.id == movie_id).first()

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )

    genres = []
    if movie_data.genre_ids:
        genres = db.query(Genre).filter(
            Genre.id.in_(movie_data.genre_ids)
        ).all()

        if len(genres) != len(movie_data.genre_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Один или несколько жанров не найдены"
            )

    movie.title = movie_data.title
    movie.description = movie_data.description
    movie.release_year = movie_data.release_year
    movie.director = movie_data.director
    movie.poster_url = movie_data.poster_url
    movie.genres = genres

    db.commit()
    db.refresh(movie)

    return movie


@app.delete(
    "/movies/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_movie(movie_id: int, db: Session = Depends(get_db)) -> None:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )

    has_ratings = db.query(Rating).filter(
        Rating.movie_id == movie_id
    ).first()
    has_favorites = db.query(Favorite).filter(
        Favorite.movie_id == movie_id
    ).first()

    if has_ratings or has_favorites:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Нельзя удалить фильм, связанный с оценками или избранным"
        )

    db.delete(movie)
    db.commit()


@app.get("/genres", response_model=list[GenreResponse])
def get_genres(db: Session = Depends(get_db)):
    genres = db.query(Genre).order_by(Genre.id).all()
    return genres


@app.get("/genres/{genre_id}", response_model=GenreResponse)
def get_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = db.query(Genre).filter(Genre.id == genre_id).first()

    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Жанр не найден"
        )

    return genre


@app.post(
    "/genres",
    response_model=GenreResponse,
    status_code=status.HTTP_201_CREATED
)
def create_genre(
    genre_data: GenreCreate,
    db: Session = Depends(get_db)
):
    existing_genre = db.query(Genre).filter(
        Genre.name == genre_data.name
    ).first()

    if existing_genre is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Жанр с таким названием уже существует"
        )

    new_genre = Genre(name=genre_data.name)
    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)

    return new_genre


@app.delete(
    "/genres/{genre_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_genre(genre_id: int, db: Session = Depends(get_db)) -> None:
    genre = db.query(Genre).options(
        selectinload(Genre.movies)
    ).filter(Genre.id == genre_id).first()

    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Жанр не найден"
        )

    db.delete(genre)
    db.commit()


@app.get("/db-check")
def db_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "message": "PostgreSQL подключен успешно!"
        }

    except Exception as e:
        return {
            "message": "Ошибка подключения",
            "error": str(e)
        }


@app.post(
    "/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        (User.email == user_data.email) |
        (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email или именем уже существует"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/users/login", response_model=TokenResponse)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == login_data.email).first()

    if user is None or not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(user.id))


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется токен Bearer",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.isdecimal():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(subject)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@app.get("/users/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user