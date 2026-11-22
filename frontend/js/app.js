const movies = [
    {
        id: 1,
        title: "Матрица",
        originalTitle: "The Matrix",
        year: 1999,
        rating: 8.7,
        genres: ["Фантастика", "Боевик"],
        director: "Лана и Лилли Вачовски",
        description: "Программист Томас Андерсон узнаёт, что окружающий мир — искусственно созданная реальность, и присоединяется к тем, кто пытается освободить человечество.",
        cover: "matrix",
        badge: "КЛАССИКА"
    },
    {
        id: 2,
        title: "Начало",
        originalTitle: "Inception",
        year: 2010,
        rating: 8.8,
        genres: ["Фантастика", "Боевик", "Триллер"],
        director: "Кристофер Нолан",
        description: "Доминик Кобб умеет проникать в сны и красть секреты. На этот раз ему предстоит не похитить идею, а внедрить её в сознание.",
        cover: "inception",
        badge: "ВЫБОР РЕДАКЦИИ"
    },
    {
        id: 3,
        title: "1+1",
        originalTitle: "The Intouchables",
        year: 2011,
        rating: 8.8,
        genres: ["Комедия", "Драма"],
        director: "Оливье Накаш и Эрик Толедано",
        description: "Неожиданная дружба аристократа Филиппа и его помощника Дрисса меняет привычный мир обоих и доказывает, что важные встречи случаются не по плану.",
        cover: "intouchables",
        badge: "ТЁПЛАЯ ИСТОРИЯ"
    },
    {
        id: 4,
        title: "Интерстеллар",
        originalTitle: "Interstellar",
        year: 2014,
        rating: 8.7,
        genres: ["Фантастика", "Драма", "Приключения"],
        director: "Кристофер Нолан",
        description: "Когда Земля становится непригодной для жизни, команда исследователей отправляется сквозь червоточину искать новый дом для человечества.",
        cover: "interstellar",
        badge: "МАСШТАБНАЯ ИСТОРИЯ"
    },
    {
        id: 5,
        title: "Оно",
        originalTitle: "It",
        year: 2017,
        rating: 7.3,
        genres: ["Ужасы", "Триллер"],
        director: "Андрес Мускетти",
        description: "В небольшом городке компания друзей сталкивается со своими страхами и тайной, которая возвращается снова и снова.",
        cover: "it",
        badge: "ДЛЯ СМЕЛЫХ"
    }
];

const state = {
    genre: "Все",
    year: "",
    query: "",
    sort: "popular",
    favorites: new Set()
};

const movieGrid = document.querySelector("#movie-grid");
const genreList = document.querySelector("#genre-list");
const searchInput = document.querySelector("#movie-search");
const yearFilter = document.querySelector("#year-filter");
const sortSelect = document.querySelector("#sort-select");
const resultsLabel = document.querySelector("#results-label");
const resetButton = document.querySelector("#reset-filters");
const emptyState = document.querySelector("#empty-state");
const movieDialog = document.querySelector("#movie-dialog");
const movieDetail = document.querySelector("#movie-detail");
const authDialog = document.querySelector("#auth-dialog");

function getGenres() {
    return ["Все", ...new Set(movies.flatMap((movie) => movie.genres))];
}

function renderFilters() {
    genreList.innerHTML = getGenres().map((genre) => `
        <button
            class="genre-chip${state.genre === genre ? " genre-chip--active" : ""}"
            type="button"
            data-genre="${genre}"
            aria-pressed="${state.genre === genre}"
        >${genre}</button>
    `).join("");

    while (yearFilter.options.length > 1) {
        yearFilter.remove(1);
    }

    [...new Set(movies.map((movie) => movie.year))]
        .sort((a, b) => b - a)
        .forEach((year) => {
            const option = document.createElement("option");
            option.value = String(year);
            option.textContent = String(year);
            yearFilter.append(option);
        });
}

function getVisibleMovies() {
    const query = state.query.trim().toLocaleLowerCase("ru");
    const filtered = movies.filter((movie) => {
        const matchesQuery = !query
            || movie.title.toLocaleLowerCase("ru").includes(query)
            || movie.originalTitle.toLocaleLowerCase("en").includes(query);
        const matchesGenre = state.genre === "Все" || movie.genres.includes(state.genre);
        const matchesYear = !state.year || movie.year === Number(state.year);
        return matchesQuery && matchesGenre && matchesYear;
    });

    if (state.sort === "newest") {
        filtered.sort((a, b) => b.year - a.year);
    } else if (state.sort === "oldest") {
        filtered.sort((a, b) => a.year - b.year);
    } else {
        filtered.sort((a, b) => b.rating - a.rating);
    }

    return filtered;
}

function movieCard(movie, index) {
    const isFavorite = state.favorites.has(movie.id);
    return `
        <article class="movie-card" style="animation-delay:${index * 45}ms">
            <button class="movie-poster cover--${movie.cover}" type="button" data-movie-id="${movie.id}" aria-label="Подробнее о фильме «${movie.title}»">
                <span class="poster-top-tag">${movie.badge}</span>
                <span class="poster-title">${movie.originalTitle}</span>
                <span class="poster-bottom"><span>${movie.year}</span><strong>★ ${movie.rating.toFixed(1)}</strong></span>
            </button>
            <button
                class="favorite-button${isFavorite ? " favorite-button--active" : ""}"
                type="button"
                data-favorite-id="${movie.id}"
                aria-label="${isFavorite ? "Убрать из избранного" : "Добавить в избранное"}: ${movie.title}"
                aria-pressed="${isFavorite}"
            >${isFavorite ? "♥" : "♡"}</button>
            <div class="movie-info">
                <div class="movie-title-line"><h3>${movie.title}</h3><span class="movie-year">${movie.year}</span></div>
                <p class="movie-genre">${movie.genres.join(" · ")}</p>
            </div>
        </article>
    `;
}

function renderMovies() {
    const visibleMovies = getVisibleMovies();
    movieGrid.innerHTML = visibleMovies.map(movieCard).join("");
    movieGrid.hidden = visibleMovies.length === 0;
    emptyState.hidden = visibleMovies.length !== 0;

    const total = visibleMovies.length;
    resultsLabel.textContent = `${total} ${total === 1 ? "фильм" : total > 1 && total < 5 ? "фильма" : "фильмов"} в подборке`;
    resetButton.hidden = state.genre === "Все" && !state.year && !state.query;
}

function resetFilters() {
    state.genre = "Все";
    state.year = "";
    state.query = "";
    state.sort = "popular";
    searchInput.value = "";
    yearFilter.value = "";
    sortSelect.value = "popular";
    renderFilters();
    renderMovies();
}

function openMovieDetails(movieId) {
    const movie = movies.find((item) => item.id === Number(movieId));
    if (!movie) return;

    movieDetail.innerHTML = `
        <div class="detail-layout">
            <div class="detail-poster">
                <div class="movie-poster cover--${movie.cover}" aria-hidden="true">
                    <span class="poster-title">${movie.originalTitle}</span>
                    <span class="poster-bottom"><span>${movie.year}</span><strong>★ ${movie.rating.toFixed(1)}</strong></span>
                </div>
            </div>
            <div class="detail-copy">
                <p class="eyebrow"><span class="eyebrow-line"></span> ${movie.originalTitle}</p>
                <h2 id="detail-title">${movie.title}</h2>
                <p class="detail-meta">${movie.year}<span aria-hidden="true"> &nbsp;·&nbsp; </span>★ ${movie.rating.toFixed(1)}</p>
                <p class="detail-description">${movie.description}</p>
                <div class="detail-genres">${movie.genres.map((genre) => `<span>${genre}</span>`).join("")}</div>
                <p class="detail-director">Режиссёр: <strong>${movie.director}</strong></p>
            </div>
        </div>
    `;
    movieDialog.showModal();
}

function setAuthMode(mode) {
    const isRegister = mode === "register";
    document.querySelector("#auth-eyebrow").textContent = isRegister ? "Присоединяйтесь к нам" : "Рады видеть вас";
    document.querySelector("#auth-title").textContent = isRegister ? "Создать аккаунт" : "Войти в аккаунт";
    document.querySelector("#auth-submit").textContent = isRegister ? "Зарегистрироваться" : "Войти";
    document.querySelector("#auth-switch-text").textContent = isRegister ? "Уже есть аккаунт?" : "Впервые у нас?";
    document.querySelector("#auth-switch").textContent = isRegister ? "Войти" : "Создать аккаунт";
    document.querySelector("#username-field").hidden = !isRegister;
    document.querySelector("#username-field input").required = isRegister;
    document.querySelector("#auth-form [name='password']").autocomplete = isRegister ? "new-password" : "current-password";
    document.querySelector("#auth-feedback").textContent = "";
    document.querySelector("#auth-form").dataset.mode = mode;
}

genreList.addEventListener("click", (event) => {
    const button = event.target.closest("[data-genre]");
    if (!button) return;
    state.genre = button.dataset.genre;
    renderFilters();
    renderMovies();
});

searchInput.addEventListener("input", () => {
    state.query = searchInput.value;
    renderMovies();
});

yearFilter.addEventListener("change", () => {
    state.year = yearFilter.value;
    renderMovies();
});

sortSelect.addEventListener("change", () => {
    state.sort = sortSelect.value;
    renderMovies();
});

movieGrid.addEventListener("click", (event) => {
    const favoriteButton = event.target.closest("[data-favorite-id]");
    if (favoriteButton) {
        const movieId = Number(favoriteButton.dataset.favoriteId);
        if (state.favorites.has(movieId)) {
            state.favorites.delete(movieId);
        } else {
            state.favorites.add(movieId);
        }
        renderMovies();
        return;
    }

    const posterButton = event.target.closest("[data-movie-id]");
    if (posterButton) openMovieDetails(posterButton.dataset.movieId);
});

document.querySelector("#reset-filters").addEventListener("click", resetFilters);
document.querySelector("#empty-reset").addEventListener("click", resetFilters);

document.querySelectorAll("[data-open-auth]").forEach((button) => {
    button.addEventListener("click", () => {
        setAuthMode(button.dataset.openAuth);
        authDialog.showModal();
    });
});

document.querySelector("#auth-switch").addEventListener("click", () => {
    const currentMode = document.querySelector("#auth-form").dataset.mode;
    setAuthMode(currentMode === "register" ? "login" : "register");
});

document.querySelector("#auth-form").addEventListener("submit", (event) => {
    event.preventDefault();
    document.querySelector("#auth-feedback").textContent =
        "Форма готова — подключение к API будет добавлено следующим этапом.";
});

document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => button.closest("dialog").close());
});

document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) dialog.close();
    });
});

const menuToggle = document.querySelector(".menu-toggle");
const primaryNav = document.querySelector("#primary-nav");
menuToggle.addEventListener("click", () => {
    const isOpen = primaryNav.classList.toggle("primary-nav--open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Закрыть меню" : "Открыть меню");
});

primaryNav.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
        primaryNav.classList.remove("primary-nav--open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "Открыть меню");
    }
});

document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        searchInput.focus();
        searchInput.select();
    }
});

renderFilters();
renderMovies();
