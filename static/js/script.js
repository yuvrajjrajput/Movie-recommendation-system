// script.js
// Handles: autocomplete search suggestions + fetching/showing recommendations

const movieInput = document.getElementById("movieInput");
const searchBtn = document.getElementById("searchBtn");
const suggestionsList = document.getElementById("suggestionsList");
const messageBox = document.getElementById("messageBox");
const movieDetails = document.getElementById("movieDetails");
const resultsSection = document.getElementById("resultsSection");
const resultsGrid = document.getElementById("resultsGrid");

// Small helper to show/hide elements
function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden"); }

function showMessage(text) {
    messageBox.textContent = text;
    show(messageBox);
    hide(movieDetails);
    hide(resultsSection);
}

// ----- Autocomplete -----
// Whenever the user types, ask the backend for matching titles.
let debounceTimer;
movieInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const query = movieInput.value.trim();

    if (query.length === 0) {
        suggestionsList.innerHTML = "";
        return;
    }

    // Small delay so we don't fire a request on every single keystroke
    debounceTimer = setTimeout(() => {
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => renderSuggestions(data.results))
            .catch(() => {
                suggestionsList.innerHTML = "";
            });
    }, 250);
});

function renderSuggestions(titles) {
    suggestionsList.innerHTML = "";

    if (!titles || titles.length === 0) {
        return;
    }

    titles.forEach(title => {
        const item = document.createElement("li");
        item.textContent = title;
        item.addEventListener("click", () => {
            movieInput.value = title;
            suggestionsList.innerHTML = "";
            fetchRecommendations(title);
        });
        suggestionsList.appendChild(item);
    });
}

// Hide suggestions if user clicks somewhere else on the page
document.addEventListener("click", (event) => {
    if (!event.target.closest(".search-section")) {
        suggestionsList.innerHTML = "";
    }
});

// ----- Search button / Enter key -----
searchBtn.addEventListener("click", handleSearch);
movieInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        handleSearch();
    }
});

function handleSearch() {
    const title = movieInput.value.trim();
    suggestionsList.innerHTML = "";

    if (title === "") {
        showMessage("Please enter a movie name before searching.");
        return;
    }

    fetchRecommendations(title);
}

// ----- Fetch movie details + recommendations from Flask backend -----
function fetchRecommendations(title) {
    fetch(`/api/recommend/${encodeURIComponent(title)}`)
        .then(response => response.json().then(data => ({ status: response.status, data })))
        .then(({ status, data }) => {
            if (status !== 200) {
                showMessage(data.error || "Something went wrong. Please try again.");
                return;
            }
            hide(messageBox);
            renderMovieDetails(data.movie);
            renderRecommendations(data.recommendations);
        })
        .catch(() => {
            showMessage("Could not reach the server. Please make sure the Flask app is running.");
        });
}

function renderMovieDetails(movie) {
    document.getElementById("movieTitle").textContent = movie.title;
    document.getElementById("movieGenre").textContent = movie.genre;
    document.getElementById("movieRating").textContent = `⭐ ${movie.rating}`;
    document.getElementById("movieDirectorCast").textContent =
        `Director: ${movie.director}  |  Cast: ${movie.cast}`;
    document.getElementById("movieDescription").textContent = movie.description;
    show(movieDetails);
}

function renderRecommendations(recommendations) {
    resultsGrid.innerHTML = "";

    if (!recommendations || recommendations.length === 0) {
        hide(resultsSection);
        return;
    }

    recommendations.forEach(movie => {
        const card = document.createElement("div");
        card.className = "movie-card";
        card.innerHTML = `
            <h4>${movie.title}</h4>
            <p>${movie.genre}</p>
            <p>⭐ ${movie.rating} &nbsp;|&nbsp; <span class="match">${movie.similarity}% match</span></p>
            <p>${movie.description}</p>
        `;
        // Clicking a recommended movie searches for it too
        card.addEventListener("click", () => {
            movieInput.value = movie.title;
            fetchRecommendations(movie.title);
        });
        resultsGrid.appendChild(card);
    });

    show(resultsSection);
}
