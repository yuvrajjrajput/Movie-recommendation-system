#  CineMatch – Movie Suggestion System

A simple web-based movie recommendation system built as a college mini-project.
The user types or selects a movie, and the system suggests similar movies using
**content-based filtering** (TF-IDF + Cosine Similarity).

---

## 1. Project Overview

CineMatch lets a user search for a movie from a small local database and instantly
see:
- The movie's genre, rating, director, cast and description
- A list of similar movies, ranked by how closely they match (as a % similarity score)

The project is intentionally kept simple (no user accounts, no external APIs, no
paid services) so that it is easy to understand, run, and explain in a viva.

---

## 2. Features

-  Search bar with **live autocomplete** while typing a movie name
-  Content-based recommendations using **genre + keywords + director + cast**
-  Displays title, genre, rating, description and cast/director for the searched movie
-  Shows a similarity percentage for every recommended movie
-  Handles empty search and invalid/unknown movie names with clear messages
-  Clean, dark-themed, responsive UI built with plain HTML/CSS/JS (no frontend framework)
-  Uses a real SQLite database (not just a CSV read every time)

---

## 3. Technology Stack

| Layer          | Technology                              |
|----------------|------------------------------------------|
| Frontend       | HTML5, CSS3, Vanilla JavaScript (fetch API) |
| Backend        | Python, Flask                           |
| Database       | SQLite                                  |
| Recommendation | pandas, scikit-learn (TF-IDF + Cosine Similarity) |

All libraries used are free and open-source.

---

## 4. System Workflow

```
User types movie name
        │
        ▼
JavaScript sends request to /api/search  ──▶  Flask queries pandas DataFrame ──▶ returns matching titles
        │ (user selects / presses search)
        ▼
JavaScript sends request to /api/recommend/<title>
        │
        ▼
Flask -> recommender.py
   1. Look up the movie in the DataFrame (loaded from SQLite at startup)
   2. Use the precomputed TF-IDF + Cosine Similarity matrix
   3. Sort other movies by similarity score, take top 6
        │
        ▼
JSON response {movie details, recommendations} sent back to browser
        │
        ▼
JavaScript renders movie details + recommendation cards on the page
```

---

## 5. Folder Structure

```
movie-suggestion-system/
│
├── app.py                  # Flask app & routes (entry point)
├── recommender.py          # Content-based filtering logic (TF-IDF + cosine similarity)
├── requirements.txt        # Python dependencies
├── .gitignore
├── README.md
│
├── database/
│   └── create_db.py        # One-time script: builds movies.db from data/movies.csv
│                            # (movies.db itself is created here after you run the script)
│
├── data/
│   └── movies.csv          # Sample dataset (40 movies) — replace/extend with your own
│
├── static/
│   ├── css/
│   │   └── style.css       # Page styling
│   └── js/
│       └── script.js       # Autocomplete + fetch calls + rendering logic
│
└── templates/
    └── index.html          # Single-page UI (search box + results)
```

---

## 6. Complete Code

All source files are included in this project folder exactly as listed above:
`app.py`, `recommender.py`, `database/create_db.py`, `data/movies.csv`,
`templates/index.html`, `static/css/style.css`, `static/js/script.js`,
`requirements.txt`, `.gitignore`.

---

## 7. Dataset Setup

A sample dataset of **40 movies** is already included at `data/movies.csv` with
these columns:

```
id, title, genre, director, cast, keywords, description, rating
```

The movie titles, genres, and crew names are original/fictional examples created
for this project, and the short descriptions were written in plain original
wording — so there is no copyright issue in submitting this as-is.

### To use your own dataset (optional but recommended):
1. Open `data/movies.csv` in Excel/Sheets or a text editor.
2. Keep the same 8 columns and header row.
3. Add/replace rows with real movies (you can find genre/cast/director info from
   any public movie website and write your own one-line description).
4. Save the file, then re-run `python database/create_db.py` to rebuild the database.

You can also use a public dataset such as the "TMDB 5000 Movies" dataset from
Kaggle — just map its columns to match the CSV format above.

---

## 8. Installation

```bash
# 1. Clone or download this project, then move into the folder
cd movie-suggestion-system

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Build the SQLite database from the CSV dataset (run this once)
python database/create_db.py
```

You should see:
```
Database created successfully at: .../database/movies.db
Total movies inserted: 40
```

---

## 9. How to Run

```bash
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000/
```

Type a movie name (e.g. `Dragon's Peak`, `Skyward Horizon`, `Coffee and Rain`),
pick a suggestion or click Search, and see the recommendations appear below.

---

## 10. How the Recommendation Algorithm Works

This project uses **content-based filtering**:

1. **Combine features** – For every movie, its `genre`, `keywords`, `director`
   and `cast` are combined into one text string (called a "tag").
2. **TF-IDF Vectorization** – `TfidfVectorizer` from scikit-learn converts each
   movie's tag string into a numeric vector. TF-IDF gives higher weight to
   words that are distinctive (e.g. "dragons") and lower weight to very common
   words.
3. **Cosine Similarity** – `cosine_similarity` compares every movie's vector
   with every other movie's vector and produces a score between 0 (completely
   different) and 1 (identical).
4. **Ranking** – When a user searches for a movie, the app looks up that
   movie's row in the similarity matrix, sorts all other movies by score, and
   returns the top 6 as recommendations (shown as a similarity %).

This is the same basic idea used by many real-world "you might also like"
systems, just applied to a small, simple dataset.

---

## 11. Notes

- This is a student mini-project built for learning purposes, not a production
  application. The Flask development server (`debug=True`) should not be used
  for real deployment.
- The dataset is intentionally small (40 movies) so the logic is easy to trace
  and explain — feel free to expand it.
