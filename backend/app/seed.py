
from app.database import SessionLocal
from app.models import Movie, Genre


def seed_data():
    db = SessionLocal()

    try:
        # Добавляем жанры
        genres_data = [
            "Фантастика",
            "Боевик",
            "Комедия",
            "Драма",
            "Триллер",
            "Ужасы",
            "Приключения",
            "Мультфильм"
        ]

        genres = {}

        for genre_name in genres_data:
            genre = db.query(Genre).filter(
                Genre.name == genre_name
            ).first()

            if not genre:
                genre = Genre(name=genre_name)
                db.add(genre)

            genres[genre_name] = genre

        db.flush()

        # Добавляем фильмы
        movies_data = [
            {
                "title": "Матрица",
                "description": "Программист узнаёт, что окружающий мир является симуляцией.",
                "release_year": 1999,
                "director": "Лана и Лилли Вачовски",
                "poster_url": "https://example.com/matrix.jpg",
                "genres": ["Фантастика", "Боевик"]
            },
            {
                "title": "Начало",
                "description": "История о проникновении в сны и краже секретов.",
                "release_year": 2010,
                "director": "Кристофер Нолан",
                "poster_url": "https://example.com/inception.jpg",
                "genres": ["Фантастика", "Боевик", "Триллер"]
            },
            {
                "title": "1+1",
                "description": "История дружбы аристократа и его помощника.",
                "release_year": 2011,
                "director": "Оливье Накаш и Эрик Толедано",
                "poster_url": "https://example.com/intouchables.jpg",
                "genres": ["Комедия", "Драма"]
            },
            {
                "title": "Интерстеллар",
                "description": "Путешествие через космос в поисках нового дома для человечества.",
                "release_year": 2014,
                "director": "Кристофер Нолан",
                "poster_url": "https://example.com/interstellar.jpg",
                "genres": ["Фантастика", "Драма", "Приключения"]
            },
            {
                "title": "Оно",
                "description": "Группа детей сталкивается с древним злом.",
                "release_year": 2017,
                "director": "Андрес Мускетти",
                "poster_url": "https://example.com/it.jpg",
                "genres": ["Ужасы", "Триллер"]
            }
        ]

        for movie_data in movies_data:
            movie = db.query(Movie).filter(
                Movie.title == movie_data["title"]
            ).first()

            if not movie:
                movie = Movie(
                    title=movie_data["title"],
                    description=movie_data["description"],
                    release_year=movie_data["release_year"],
                    director=movie_data["director"],
                    poster_url=movie_data["poster_url"]
                )

                movie.genres = [
                    genres[name] for name in movie_data["genres"]
                ]

                db.add(movie)

        db.commit()
        print("Тестовые данные успешно добавлены!")

    except Exception as error:
        db.rollback()
        print("Ошибка при добавлении данных:", error)

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
