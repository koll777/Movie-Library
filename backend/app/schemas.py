from pydantic import BaseModel, EmailStr, Field, PositiveInt, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {
        "from_attributes": True
    }
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class PasswordChangeResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GenreResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class GenreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Название жанра не должно быть пустым")
        return name


class MovieCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    release_year: int | None = None
    director: str | None = Field(default=None, max_length=150)
    poster_url: str | None = Field(default=None, max_length=500)
    genre_ids: list[PositiveInt] = Field(default_factory=list)

    @field_validator("genre_ids")
    @classmethod
    def genre_ids_must_be_unique(cls, genre_ids: list[int]) -> list[int]:
        if len(genre_ids) != len(set(genre_ids)):
            raise ValueError("ID жанров не должны повторяться")
        return genre_ids


class MovieUpdate(MovieCreate):
    pass


class MovieResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    release_year: int | None = None
    director: str | None = None
    poster_url: str | None = None
    genres: list[GenreResponse] = []

    model_config = {"from_attributes": True}
    
class RatingCreate(BaseModel):
    movie_id: PositiveInt
    score: int = Field(ge=1, le=10)


class RatingResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    score: int

    model_config = {"from_attributes": True}
    
class FavoriteCreate(BaseModel):
    movie_id: PositiveInt