const API_URL = "http://127.0.0.1:8000";
const TOKEN_KEY = "kinoteka_access_token";
const app = document.querySelector("#app");
const headerActions = document.querySelector("#header-actions");
const toastStack = document.querySelector("#toast-stack");

const state = {
  token: localStorage.getItem(TOKEN_KEY),
  user: null,
  movies: [],
  genres: [],
  favorites: new Set(),
  ratings: [],
  catalog: { search: "", genre: "", year: "", sort: "id", page: 1 },
};

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (response.status === 204) return null;
  let data = null;
  try { data = await response.json(); } catch (_) {}
  if (!response.ok) {
    if (response.status === 401) {
      clearSession();
      throw new Error(data?.detail || "Сессия истекла. Войдите снова.");
    }
    throw new Error(data?.detail || "Не удалось выполнить запрос");
  }
  return data;
}

function toast(message, type = "success") {
  const item = document.createElement("div");
  item.className = `toast ${type}`;
  item.textContent = message;
  toastStack.append(item);
  setTimeout(() => item.remove(), 3500);
}

function clearSession() {
  state.token = null;
  state.user = null;
  state.favorites.clear();
  state.ratings = [];
  localStorage.removeItem(TOKEN_KEY);
  renderHeader();
}

function setToken(token) {
  state.token = token;
  localStorage.setItem(TOKEN_KEY, token);
  renderHeader();
}

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;" }[char]));
}

function posterFallback(movie) {
  return `<div class="poster-fallback"><span>${escapeHtml(movie.title)}</span><small>${movie.release_year || ""}</small></div>`;
}

function posterMarkup(movie, interactive = true) {
  const isFavorite = state.favorites.has(movie.id);
  const image = movie.poster_url && !movie.poster_url.includes("example.com")
    ? `<img class="poster-image" src="${escapeHtml(movie.poster_url)}" alt="${escapeHtml(movie.title)}" loading="lazy" onerror="this.hidden=true;this.nextElementSibling.hidden=false"><span class="poster-fallback" hidden><span>${escapeHtml(movie.title)}</span><small>${movie.release_year || ""}</small></span>`
    : posterFallback(movie);
  return `<article class="movie-card">
    <div class="poster" ${interactive ? `data-open-movie="${movie.id}" role="button" tabindex="0"` : ""}>
      ${image}
      ${interactive ? `<button class="favorite-fab ${isFavorite ? "active" : ""}" type="button" data-favorite="${movie.id}" aria-label="${isFavorite ? "Убрать из избранного" : "Добавить в избранное"}" aria-pressed="${isFavorite}">
        <svg viewBox="0 0 24 24"><path d="M20.8 4.6a5.5 5.5 0 00-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 00-7.8 7.8l1.1 1.1L12 21l7.8-7.5 1.1-1.1a5.5 5.5 0 000-7.8z"/></svg>
      </button>` : ""}
    </div>
    <div class="movie-meta">
      <h3>${escapeHtml(movie.title)}</h3>
      <div class="movie-meta-row"><span>${escapeHtml(movie.genres?.map(g => g.name).join(" · ") || "Жанр не указан")}</span><span>${movie.release_year || "—"}</span></div>
    </div>
  </article>`;
}

function skeletonGrid(count = 10) {
  return `<div class="movie-grid">${Array.from({ length: count }, () => `<div class="skeleton skeleton-card"></div>`).join("")}</div>`;
}

function renderHeader() {
  if (state.token) {
    headerActions.innerHTML = `<a class="button button-ghost" href="#/profile">${escapeHtml(state.user?.username || "Профиль")}</a><button class="button button-secondary" type="button" data-action="logout">Выйти</button>`;
  } else {
    headerActions.innerHTML = `<a class="button button-ghost" href="#/login">Войти</a><a class="button button-primary" href="#/register">Создать аккаунт</a>`;
  }
  updateActiveNav();
}

function updateActiveNav() {
  const route = location.hash.replace("#", "") || "/";
  document.querySelectorAll("[data-nav]").forEach(link => {
    const active = link.dataset.nav === "/" ? route === "/" : route.startsWith(link.dataset.nav);
    link.classList.toggle("active", active);
  });
}

async function loadSession() {
  if (!state.token) return;
  try {
    state.user = await api("/users/me");
  } catch (_) {
    clearSession();
  }
  renderHeader();
}

async function loadPrivateLists() {
  if (!state.token) return;
  try {
    const [favorites, ratings] = await Promise.all([api("/favorites"), api("/ratings")]);
    state.favorites = new Set(favorites.map(movie => movie.id));
    state.ratings = ratings;
  } catch (_) {}
}

async function toggleFavorite(movieId) {
  if (!state.token) {
    location.hash = "/login";
    toast("Для избранного нужно войти", "error");
    return;
  }
  try {
    if (state.favorites.has(movieId)) {
      await api(`/favorites/${movieId}`, { method: "DELETE" });
      state.favorites.delete(movieId);
      toast("Удалено из избранного");
    } else {
      await api("/favorites", { method: "POST", body: JSON.stringify({ movie_id: movieId }) });
      state.favorites.add(movieId);
      toast("Добавлено в избранное");
    }
  } catch (error) {
    toast(error.message, "error");
  }
  refreshVisibleFavoriteButtons();
  if (location.hash === "#/favorites") route();
}

function refreshVisibleFavoriteButtons() {
  document.querySelectorAll("[data-favorite]").forEach(button => {
    const id = Number(button.dataset.favorite);
    const active = state.favorites.has(id);
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
    button.setAttribute("aria-label", active ? "Убрать из избранного" : "Добавить в избранное");
  });
  document.querySelectorAll("[data-detail-favorite]").forEach(button => {
    const id = Number(button.dataset.detailFavorite);
    const active = state.favorites.has(id);
    button.textContent = active ? "В избранном" : "В избранное";
  });
}

async function homePage() {
  app.innerHTML = `<section class="container hero">
    <div class="hero-copy"><p class="eyebrow">Cinema Premium</p><h1>Твой личный <em>мир кино</em></h1><p class="hero-description">Находите истории по настроению, собирайте любимые фильмы и возвращайтесь к тем, которые остаются с вами.</p><div class="hero-actions"><a class="button button-primary" href="#/catalog">Перейти к каталогу</a></div></div>
    <div class="hero-art"><div class="hero-art-grid" id="hero-art-grid">${Array.from({length:3},()=>`<div class="skeleton poster"></div>`).join("")}</div></div>
  </section>
  <section class="container home-section"><div class="section-head"><h2>Популярное в Кинотеке</h2><a href="#/catalog">Весь каталог →</a></div><div id="popular-grid">${skeletonGrid(5)}</div></section>`;
  try {
    const movies = await api("/movies?limit=100&offset=0");
    state.movies = movies;
    const art = movies.slice(0, 3);
    if (art.length) document.querySelector("#hero-art-grid").innerHTML = art.map(movie => posterMarkup(movie, true)).join("");
    document.querySelector("#popular-grid").innerHTML = movies.length ? `<div class="movie-grid">${movies.slice(0,5).map(movie => posterMarkup(movie)).join("")}</div>` : emptyMarkup("Каталог пока пуст");
  } catch (error) {
    document.querySelector("#popular-grid").innerHTML = emptyMarkup("Не удалось загрузить каталог", error.message);
  }
}

async function catalogPage() {
  app.innerHTML = `<div class="container catalog-layout">
    <div class="catalog-header"><div><h1>Каталог фильмов</h1><p>Ищите и фильтруйте свою подборку.</p></div></div>
    <aside class="catalog-filters" aria-label="Фильтры каталога">
      <h2>Фильтры</h2><div class="filter-group"><span class="filter-group-title">Жанр</span><div class="filter-options" id="genre-options"></div></div>
      <div class="field"><label for="year-select">Год выпуска</label><select id="year-select"><option value="">Любой год</option></select></div>
      <button class="button button-secondary" type="button" id="reset-catalog">Сбросить</button>
    </aside>
    <section class="catalog-results">
      <div class="catalog-toolbar"><div class="field search-field"><label class="visually-hidden" for="catalog-search">Поиск</label><input id="catalog-search" type="search" placeholder="Поиск по названию" value="${escapeHtml(state.catalog.search)}"></div><div class="field"><label class="visually-hidden" for="catalog-sort">Сортировка</label><select id="catalog-sort"><option value="id" ${state.catalog.sort==="id"?"selected":""}>По каталогу</option><option value="newest" ${state.catalog.sort==="newest"?"selected":""}>Сначала новые</option><option value="oldest" ${state.catalog.sort==="oldest"?"selected":""}>Сначала старые</option></select></div></div>
      <div class="results-count" id="results-count"></div><div id="catalog-grid">${skeletonGrid(10)}</div><div class="pagination" id="catalog-pagination"></div>
    </section>
  </div>`;

  try {
    const [movies, genres] = await Promise.all([api("/movies?limit=100&offset=0"), api("/genres")]);
    state.movies = movies;
    state.genres = genres;
    const genreOptions = `<button class="chip ${!state.catalog.genre ? "active" : ""}" type="button" data-genre="">Все</button>` + genres.map(g => `<button class="chip ${state.catalog.genre===g.name ? "active" : ""}" type="button" data-genre="${escapeHtml(g.name)}">${escapeHtml(g.name)}</button>`).join("");
    document.querySelector("#genre-options").innerHTML = genreOptions;
    const yearSelect = document.querySelector("#year-select");
    [...new Set(movies.map(m => m.release_year).filter(Boolean))].sort((a,b)=>b-a).forEach(year => yearSelect.add(new Option(year, year)));
    yearSelect.value = state.catalog.year;
  } catch (error) {
    document.querySelector("#catalog-grid").innerHTML = emptyMarkup("Не удалось загрузить каталог", error.message);
    return;
  }
  renderCatalog();
}

function renderCatalog() {
  let movies = [...state.movies];
  const query = state.catalog.search.trim().toLocaleLowerCase("ru");
  if (query) movies = movies.filter(m => m.title.toLocaleLowerCase("ru").includes(query));
  if (state.catalog.genre) movies = movies.filter(m => m.genres.some(g => g.name === state.catalog.genre));
  if (state.catalog.year) movies = movies.filter(m => String(m.release_year) === state.catalog.year);
  if (state.catalog.sort === "newest") movies.sort((a,b)=>(b.release_year||0)-(a.release_year||0));
  if (state.catalog.sort === "oldest") movies.sort((a,b)=>(a.release_year||0)-(b.release_year||0));

  const pageSize = 10;
  const pages = Math.max(1, Math.ceil(movies.length / pageSize));
  state.catalog.page = Math.min(state.catalog.page, pages);
  const visible = movies.slice((state.catalog.page-1)*pageSize, state.catalog.page*pageSize);
  document.querySelector("#results-count").textContent = `${movies.length} ${movies.length===1?"фильм":movies.length<5?"фильма":"фильмов"}`;
  document.querySelector("#catalog-grid").innerHTML = visible.length ? `<div class="movie-grid">${visible.map(movie => posterMarkup(movie)).join("")}</div>` : emptyMarkup("Ничего не найдено", "Попробуйте изменить параметры поиска.");
  document.querySelector("#catalog-pagination").innerHTML = pages > 1 ? `<button class="icon-button" type="button" data-page="${state.catalog.page-1}" ${state.catalog.page<=1?"disabled":""} aria-label="Предыдущая">‹</button><span>${state.catalog.page} / ${pages}</span><button class="icon-button" type="button" data-page="${state.catalog.page+1}" ${state.catalog.page>=pages?"disabled":""} aria-label="Следующая">›</button>` : "";
}

function emptyMarkup(title, text = "Вернитесь к каталогу и выберите фильм.") {
  return `<div class="empty-state"><h2>${escapeHtml(title)}</h2><p>${escapeHtml(text)}</p><a class="button button-primary" href="#/catalog">Перейти в каталог</a></div>`;
}

async function detailPage(id) {
  app.innerHTML = `<div class="detail-hero"><div class="container">${skeletonGrid(1)}</div></div>`;
  try {
    const movie = await api(`/movies/${id}`);
    const existing = state.ratings.find(r => r.movie_id === movie.id);
    app.innerHTML = `<section class="detail-hero"><div class="container detail-layout">
      ${posterMarkup(movie, false)}
      <div class="detail-copy"><p class="eyebrow">Фильм</p><h1>${escapeHtml(movie.title)}</h1>
      <div class="detail-meta"><span>${movie.release_year || "Год не указан"}</span><span>${escapeHtml(movie.director || "Режиссёр не указан")}</span></div>
      <p class="detail-description">${escapeHtml(movie.description || "Описание к этому фильму пока не добавлено.")}</p>
      <div class="genre-tags">${movie.genres.map(g=>`<span>${escapeHtml(g.name)}</span>`).join("")}</div>
      <div class="detail-actions"><button class="button ${state.favorites.has(movie.id)?"button-primary":"button-secondary"}" type="button" data-detail-favorite="${movie.id}">${state.favorites.has(movie.id)?"В избранном":"В избранное"}</button></div>
      ${state.token ? `<div class="rating-panel"><div class="rating-panel-label">${existing ? `Ваша оценка: ${existing.score}/10` : "Оцените фильм"}</div><div class="rating-control" id="rating-control">${Array.from({length:10},(_,i)=>`<button type="button" class="${existing?.score===i+1?"active":""}" data-score="${i+1}" aria-label="Оценка ${i+1}">${i+1}</button>`).join("")}</div>${existing?`<button class="button button-danger" type="button" id="delete-rating" data-rating-id="${existing.id}" style="margin-top:10px">Удалить оценку</button>`:""}</div>` : `<p class="detail-description"><a class="button button-secondary" href="#/login">Войдите, чтобы оценить</a></p>`}
      </div></div></section>`;
  } catch (error) {
    app.innerHTML = `<div class="container" style="padding:48px 0">${emptyMarkup("Фильм не найден", error.message)}</div>`;
  }
}

async function authPage(mode) {
  const register = mode === "register";
  app.innerHTML = `<div class="auth-page"><div class="auth-card"><p class="eyebrow">${register?"Новая коллекция":"Welcome back"}</p><h1>${register?"Создать аккаунт":"Войти"}</h1><p>${register?"Собирайте избранное и оценивайте фильмы.":"Продолжите собирать свой мир кино."}</p>
  <form class="auth-form" id="auth-form" novalidate>${register?`<div class="field" data-field="username"><label for="username">Имя пользователя</label><input id="username" name="username" minlength="3" maxlength="50" autocomplete="username" required><div class="field-error"></div></div>`:""}
  <div class="field" data-field="email"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" placeholder="name@example.com" required><div class="field-error"></div></div>
  <div class="field" data-field="password"><label for="password">Пароль</label><div class="password-field"><input id="password" name="password" type="password" minlength="8" maxlength="128" autocomplete="${register?"new-password":"current-password"}" required><button class="password-toggle" type="button" data-password-toggle aria-label="Показать пароль">Показать</button></div><div class="field-error">${register?"От 8 до 128 символов":" "}</div></div>
  <button class="button button-primary button-wide" type="submit">${register?"Зарегистрироваться":"Войти"}</button></form><p class="auth-switch">${register?"Уже есть аккаунт?":"Впервые у нас?"} <a href="#/${register?"login":"register"}">${register?"Войти":"Создать аккаунт"}</a></p></div></div>`;
}

async function favoritesPage() {
  if (!state.token) { app.innerHTML = emptyMarkup("Нужен вход", "Войдите, чтобы увидеть избранное."); return; }
  app.innerHTML = `<div class="container" style="padding:48px 0 72px"><div class="section-head"><h1 style="margin:0;font-family:var(--font-display);font-size:36px">Избранное</h1></div><div id="favorites-grid">${skeletonGrid(5)}</div></div>`;
  try {
    const movies = await api("/favorites");
    state.favorites = new Set(movies.map(m=>m.id));
    document.querySelector("#favorites-grid").innerHTML = movies.length ? `<div class="movie-grid">${movies.map(movie => posterMarkup(movie)).join("")}</div>` : emptyMarkup("Избранное пусто");
  } catch (error) {
    document.querySelector("#favorites-grid").innerHTML = emptyMarkup("Не удалось загрузить избранное", error.message);
  }
}

async function ratingsPage() {
  if (!state.token) { app.innerHTML = `<div class="container" style="padding:48px 0">${emptyMarkup("Нужен вход", "Войдите, чтобы увидеть оценки.")}</div>`; return; }
  app.innerHTML = `<div class="container" style="padding:48px 0 72px"><div class="section-head"><h1 style="margin:0;font-family:var(--font-display);font-size:36px">Мои оценки</h1></div>${skeletonGrid(5)}</div>`;
  try {
    const ratings = await api("/ratings");
    state.ratings = ratings;
    const movies = await api("/movies?limit=100&offset=0");
    const rated = ratings.map(r => ({...movies.find(m=>m.id===r.movie_id), _rating:r})).filter(m=>m.id);
    app.innerHTML = `<div class="container" style="padding:48px 0 72px"><div class="section-head"><h1 style="margin:0;font-family:var(--font-display);font-size:36px">Мои оценки</h1></div>${rated.length?`<div class="movie-grid">${rated.map(movie=>`<div>${posterMarkup(movie).replace("</article>",`<div class="rating-panel-label" style="margin-top:8px">Моя оценка: ${movie._rating.score}/10</div></article>`)}</div>`).join("")}`:emptyMarkup("Оценок пока нет","Оцените фильмы на их страницах.")}</div>`;
  } catch (error) { app.innerHTML = `<div class="container" style="padding:48px 0">${emptyMarkup("Не удалось загрузить оценки",error.message)}</div>`; }
}

async function profilePage() {
  if (!state.token) { location.hash = "/login"; return; }
  app.innerHTML = `<div class="container profile-layout"><aside class="profile-card"><div class="profile-avatar" id="profile-avatar">?</div><h1 id="profile-name">Загрузка...</h1><p id="profile-email"></p><button class="button button-danger" type="button" data-action="logout">Выйти из аккаунта</button></aside><section class="password-card"><h2>Смена пароля</h2><form class="password-form" id="password-form" novalidate><div class="field"><label for="current-password">Текущий пароль</label><input id="current-password" name="current_password" type="password" minlength="1" required><div class="field-error"></div></div><div class="field"><label for="new-password">Новый пароль</label><input id="new-password" name="new_password" type="password" minlength="8" maxlength="128" required><div class="field-error"></div></div><button class="button button-primary" type="submit">Изменить пароль</button></form></section></div>`;
  try {
    state.user = await api("/users/me");
    document.querySelector("#profile-name").textContent = state.user.username;
    document.querySelector("#profile-email").textContent = state.user.email;
    document.querySelector("#profile-avatar").textContent = state.user.username.charAt(0).toUpper?.() || state.user.username.charAt(0);
  } catch (error) { toast(error.message, "error"); }
}

async function route() {
  const path = (location.hash.replace("#", "") || "/").split("?")[0];
  updateActiveNav();
  window.scrollTo({top:0,behavior:"instant"});
  if (path === "/") return homePage();
  if (path === "/catalog") return catalogPage();
  if (path === "/login") return authPage("login");
  if (path === "/register") return authPage("register");
  if (path === "/favorites") return favoritesPage();
  if (path === "/ratings") return ratingsPage();
  if (path === "/profile") return profilePage();
  if (path.startsWith("/movies/")) return detailPage(path.split("/")[2]);
  app.innerHTML = `<div class="container" style="padding:48px 0">${emptyMarkup("Страница не найдена")}</div>`;
}

document.addEventListener("click", async event => {
  const favoriteButton = event.target.closest("[data-favorite]");
  if (favoriteButton) { event.stopPropagation(); await toggleFavorite(Number(favoriteButton.dataset.favorite)); return; }

  const openMovie = event.target.closest("[data-open-movie]");
  if (openMovie) { location.hash = `/movies/${openMovie.dataset.openMovie}`; return; }

  const detailFavorite = event.target.closest("[data-detail-favorite]");
  if (detailFavorite) { await toggleFavorite(Number(detailFavorite.dataset.detailFavorite)); return; }

  const logout = event.target.closest("[data-action='logout']");
  if (logout) { clearSession(); location.hash = "/"; toast("Вы вышли из аккаунта"); return; }

  const passwordToggle = event.target.closest("[data-password-toggle]");
  if (passwordToggle) { const input=passwordToggle.parentElement.querySelector("input"); input.type=input.type==="password"?"text":"password"; passwordToggle.textContent=input.type==="password"?"Показать":"Скрыть"; return; }

  const genreButton = event.target.closest("[data-genre]");
  if (genreButton) { state.catalog.genre=genreButton.dataset.genre; state.catalog.page=1; document.querySelectorAll("[data-genre]").forEach(b=>b.classList.toggle("active",b===genreButton)); renderCatalog(); return; }

  if (event.target.closest("#reset-catalog")) {
    state.catalog = { search:"", genre:"", year:"", sort:"id", page:1 };
    route();
    return;
  }

  const pageButton = event.target.closest("[data-page]");
  if (pageButton && !pageButton.disabled) { state.catalog.page=Number(pageButton.dataset.page); renderCatalog(); return; }

  const scoreButton = event.target.closest("[data-score]");
  if (scoreButton) {
    const movieId = Number(location.hash.split("/").pop());
    const existing = state.ratings.find(r=>r.movie_id===movieId);
    const score = Number(scoreButton.dataset.score);
    try {
      if (existing) await api(`/ratings/${existing.id}`, { method:"PUT", body:JSON.stringify({movie_id:movieId,score}) });
      else await api("/ratings",{method:"POST",body:JSON.stringify({movie_id:movieId,score})});
      await loadPrivateLists();
      toast(existing?"Оценка изменена":"Оценка сохранена");
      route();
    } catch (error) { toast(error.message,"error"); }
  }

  const deleteRating = event.target.closest("#delete-rating");
  if (deleteRating) {
    try { await api(`/ratings/${deleteRating.dataset.ratingId}`,{method:"DELETE"}); await loadPrivateLists(); toast("Оценка удалена"); route(); } catch(error){toast(error.message,"error");}
  }
});

window.addEventListener("hashchange", route);

function initApp() {
  renderHeader();
  route();
  if (state.token) {
    loadSession();
    loadPrivateLists();
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp, { once: true });
} else {
  initApp();
}

document.addEventListener("keydown", event => {
  if ((event.key==="Enter"||event.key===" ") && event.target.matches("[data-open-movie]")) { event.preventDefault(); location.hash=`/movies/${event.target.dataset.openMovie}`; }
});

document.addEventListener("input", event => {
  if (event.target.id==="catalog-search") {
    state.catalog.search=event.target.value; state.catalog.page=1;
    clearTimeout(window.catalogTimer); window.catalogTimer=setTimeout(renderCatalog,180);
  }
});

document.addEventListener("change", event => {
  if (event.target.id==="year-select") { state.catalog.year=event.target.value; state.catalog.page=1; renderCatalog(); }
  if (event.target.id==="catalog-sort") { state.catalog.sort=event.target.value; state.catalog.page=1; renderCatalog(); }
});

document.addEventListener("submit", async event => {
  if (event.target.id==="auth-form") {
    event.preventDefault();
    const mode=(location.hash||"#/login").includes("register")?"register":"login";
    const form=event.target;
    const submit=form.querySelector("[type='submit']");
    submit.disabled=true;
    const formData=new FormData(form);
    const body={email:String(formData.get("email")).trim(),password:String(formData.get("password"))};
    if(mode==="register") body.username=String(formData.get("username")).trim();
    form.querySelectorAll(".field").forEach(field=>field.classList.remove("invalid"));
    let valid=true;
    form.querySelectorAll("[required]").forEach(input=>{
      if(!input.checkValidity()){ valid=false; const field=input.closest(".field"); field?.classList.add("invalid"); const error=field?.querySelector(".field-error"); if(error) error.textContent=input.validity.typeMismatch?"Введите корректный email":input.name==="password"?"Пароль должен содержать от 8 до 128 символов":"Заполните это поле"; }
    });
    if(!valid){submit.disabled=false;return;}
    try {
      if(mode==="register"){ await api("/users/register",{method:"POST",body:JSON.stringify(body)}); toast("Аккаунт создан"); }
      const token=await api("/users/login",{method:"POST",body:JSON.stringify({email:body.email,password:body.password})});
      setToken(token.access_token);
      await loadSession();
      await loadPrivateLists();
      location.hash="/favorites";
      toast(mode==="register"?"Добро пожаловать":"С возвращением");
    } catch(error){
      const feedback=form.querySelector('[data-field="password"] .field-error');
      if(feedback) feedback.textContent=error.message;
      toast(error.message,"error");
    } finally { submit.disabled=false; }
  }

  if (event.target.id==="password-form") {
    event.preventDefault();
    const form = event.target;
    const submit=form.querySelector("[type='submit']");
    submit.disabled = true;
    const currentPassword = form.elements.current_password.value;
    const newPassword = form.elements.new_password.value;
    form.querySelectorAll(".field").forEach(field => field.classList.remove("invalid"));
    let valid = true;
    form.querySelectorAll("[required]").forEach(input => {
      if (!input.checkValidity()) {
        valid = false;
        const field = input.closest(".field");
        field?.classList.add("invalid");
        const error = field?.querySelector(".field-error");
        if (error) error.textContent = input.name === "new_password"
          ? "Новый пароль должен содержать от 8 до 128 символов"
          : "Введите текущий пароль";
      }
    });

    if (!valid) { submit.disabled = false; return; }
    try {
      await api("/users/me/password", {
        method:"PUT",
        body: JSON.stringify({current_password:currentPassword,new_password:newPassword})
      });
      form.reset();
      toast("Пароль успешно изменён");
    } catch (error) {
      const errorField = form.querySelector(".field:last-of-type");
      errorField?.classList.add("invalid");
      const errorText = errorField?.querySelector(".field-error");
      if (errorText) errorText.textContent = error.message;
      toast(error.message, "error");
    } finally {
      submit.disabled = false;
    }
  }
});
