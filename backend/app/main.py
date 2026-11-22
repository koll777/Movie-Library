from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.database import engine, get_db
from app.models import User, Movie, Genre, Rating, Favorite
from app.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    PasswordChange,
    PasswordChangeResponse,
    TokenResponse,
    MovieCreate,
    MovieUpdate,
    MovieResponse,
    GenreCreate,
    GenreResponse,
    RatingCreate,
    RatingResponse,
    FavoriteCreate,
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
def get_movies(
    search: str | None = None,
    genre: str | None = None,
    year: int | None = Query(default=None, gt=0),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Movie).options(selectinload(Movie.genres))

    if search is not None:
        query = query.filter(Movie.title.ilike(f"%{search}%"))

    if genre is not None:
        query = query.filter(Movie.genres.any(Genre.name == genre))

    if year is not None:
        query = query.filter(Movie.release_year == year)

    movies = query.order_by(Movie.id).offset(offset).limit(limit).all()

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

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="База данных временно недоступна"
        )


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


@app.put(
    "/users/me/password",
    response_model=PasswordChangeResponse,
)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(
        password_data.current_password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль",
        )

    if verify_password(
        password_data.new_password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый пароль должен отличаться от текущего",
        )

    current_user.password_hash = hash_password(password_data.new_password)
    db.commit()

    return PasswordChangeResponse(message="Пароль успешно изменён")


@app.get("/users/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

@app.get("/ratings", response_model=list[RatingResponse])
def get_ratings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Rating).filter(
        Rating.user_id == current_user.id
    ).order_by(Rating.id).all()


@app.post(
    "/ratings",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_rating(
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(
        Movie.id == rating_data.movie_id
    ).first()

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )

    existing_rating = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.movie_id == rating_data.movie_id
    ).first()

    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже оценили этот фильм"
        )

    new_rating = Rating(
        user_id=current_user.id,
        movie_id=rating_data.movie_id,
        score=rating_data.score
    )

    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    return new_rating


@app.put("/ratings/{rating_id}", response_model=RatingResponse)
def update_rating(
    rating_id: int,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rating = db.query(Rating).filter(
        Rating.id == rating_id,
        Rating.user_id == current_user.id
    ).first()

    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оценка не найдена"
        )

    rating.score = rating_data.score

    db.commit()
    db.refresh(rating)

    return rating


@app.delete(
    "/ratings/{rating_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_rating(
    rating_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rating = db.query(Rating).filter(
        Rating.id == rating_id,
        Rating.user_id == current_user.id
    ).first()

    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оценка не найдена"
        )

    db.delete(rating)
    db.commit()
    
@app.get("/favorites", response_model=list[MovieResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).all()

    return [
        db.query(Movie)
        .options(selectinload(Movie.genres))
        .filter(Movie.id == favorite.movie_id)
        .first()
        for favorite in favorites
    ]


@app.post(
    "/favorites",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED
)
def add_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(
        Movie.id == favorite_data.movie_id
    ).first()

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден"
        )

    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.movie_id == favorite_data.movie_id
    ).first()

    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Фильм уже добавлен в избранное"
        )

    new_favorite = Favorite(
        user_id=current_user.id,
        movie_id=favorite_data.movie_id
    )

    db.add(new_favorite)
    db.commit()

    return db.query(Movie).options(
        selectinload(Movie.genres)
    ).filter(
        Movie.id == favorite_data.movie_id
    ).first()


@app.delete(
    "/favorites/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_favorite(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.movie_id == movie_id
    ).first()

    if favorite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фильм не найден в избранном"
        )

    db.delete(favorite)
    db.commit()