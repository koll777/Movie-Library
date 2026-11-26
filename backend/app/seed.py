
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
                "description": "Программист Томас Андерсон узнаёт, что окружающий мир является искусственной реальностью.",
                "release_year": 1999,
                "director": "Лана и Лилли Вачовски",
                "poster_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "genres": ["Фантастика", "Боевик"]
            },
            {
                "title": "Начало",
                "description": "История о проникновении в сны и краже секретов.",
                "release_year": 2010,
                "director": "Кристофер Нолан",
                "poster_url": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
                "genres": ["Фантастика", "Боевик", "Триллер"]
            },
            {
                "title": "1+1",
                "description": "История дружбы аристократа и его помощника.",
                "release_year": 2011,
                "director": "Оливье Накаш и Эрик Толедано",
                "poster_url": "https://image.tmdb.org/t/p/w500/1QUvT7Hq6f3lD3l0p5i8v9mP7zA.jpg",
                "genres": ["Комедия", "Драма"]
            },
            {
                "title": "Интерстеллар",
                "description": "Путешествие через космос в поисках нового дома для человечества.",
                "release_year": 2014,
                "director": "Кристофер Нолан",
                "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
                "genres": ["Фантастика", "Драма", "Приключения"]
            },
            {
                "title": "Оно",
                "description": "Группа детей сталкивается с древним злом.",
                "release_year": 2017,
                "director": "Андрес Мускетти",
                "poster_url": "https://image.tmdb.org/t/p/w500/9NX9LFuQUtH9pR1zRJuXQq4iQv.jpg",
                "genres": ["Ужасы", "Триллер"]
            },
            {
                "title": "Темный рыцарь",
                "description": "Бэтмен противостоит хаосу, который приносит Джокер.",
                "release_year": 2008,
                "director": "Кристофер Нолан",
                "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
                "genres": ["Боевик", "Триллер", "Драма"]
            },
            {
                "title": "Паразиты",
                "description": "Семья находит способ проникнуть в богатый дом.",
                "release_year": 2019,
                "director": "Пон Джун Хо",
                "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
                "genres": ["Триллер", "Драма", "Комедия"]
            },
            {
                "title": "Дюна",
                "description": "Пол Атрейдес становится ключевой фигурой в судьбе далёкой пустынной планеты.",
                "release_year": 2021,
                "director": "Дени Вильнёв",
                "poster_url": "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
                "genres": ["Фантастика", "Приключения", "Драма"]
            },
            {
                "title": "Джокер",
                "description": "Трагическая история превращения Артура Флека в символ хаоса.",
                "release_year": 2019,
                "director": "Тодд Филлипс",
                "poster_url": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
                "genres": ["Триллер", "Драма"]
            },
            {
                "title": "Побег из Шоушенка",
                "description": "История дружбы и надежды за стенами тюрьмы.",
                "release_year": 1994,
                "director": "Фрэнк Дарабонт",
                "poster_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
                "genres": ["Драма"]
            },
            {
                "title": "Крестный отец",
                "description": "Сага о семье Корлеоне и мире организованной преступности.",
                "release_year": 1972,
                "director": "Фрэнсис Форд Коппола",
                "poster_url": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
                "genres": ["Драма"]
            },
            {
                "title": "Форрест Гамп",
                "description": "Простодушный Форрест проходит через ключевые события американской истории.",
                "release_year": 1994,
                "director": "Роберт Земекис",
                "poster_url": "https://image.tmdb.org/t/p/w500/saHP97rTPS5eLmrLQEcANmJRSll.jpg",
                "genres": ["Драма", "Комедия"]
            },
            {
                "title": "Властелин колец: Братство кольца",
                "description": "Хоббит Фродо отправляется разрушить Кольцо Всевластия.",
                "release_year": 2001,
                "director": "Питер Джексон",
                "poster_url": "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
                "genres": ["Фантастика", "Приключения"]
            },
            {
                "title": "Гладиатор",
                "description": "Римский военачальник превращается в гладиатора ради мести.",
                "release_year": 2000,
                "director": "Ридли Скотт",
                "poster_url": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
                "genres": ["Боевик", "Драма", "Приключения"]
            },
            {
                "title": "Зелёная миля",
                "description": "Надзиратель знакомится с заключённым, обладающим необычной силой.",
                "release_year": 1999,
                "director": "Фрэнк Дарабонт",
                "poster_url": "https://image.tmdb.org/t/p/w500/8VG8fDNiy50H4FedGwdSVUPoaJe.jpg",
                "genres": ["Драма", "Фантастика"]
            },
            {
                "title": "Интерстеллар",
                "description": "Команда исследователей отправляется искать новый дом для человечества.",
                "release_year": 2014,
                "director": "Кристофер Нолан",
                "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
                "genres": ["Фантастика", "Драма", "Приключения"]
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
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
