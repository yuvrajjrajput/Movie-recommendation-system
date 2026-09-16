"""
recommender.py
----------------
This file contains all the "brain" of the project: loading movies from the
SQLite database and finding similar movies using content-based filtering.

How the algorithm works (in simple words):
1. For every movie we combine its genre + keywords + director + cast into
   one single text string called a "tag".
2. We convert all the tags into numbers using TF-IDF (Term Frequency -
   Inverse Document Frequency). This basically gives more weight to words
   that are important/rare and less weight to very common words.
3. We compare every movie's TF-IDF vector with every other movie's vector
   using Cosine Similarity. This gives us a similarity score between 0
   (nothing in common) and 1 (identical).
4. When the user picks a movie, we look up that movie's row in the
   similarity matrix and return the movies with the highest scores
   (excluding the movie itself).
"""

import os
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "movies.db")


class MovieRecommender:
    """Loads movie data once and answers search/recommendation queries."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.movies_df = None
        self.similarity_matrix = None
        self._load_data()
        self._build_similarity_matrix()

    def _load_data(self):
        """Load all movies from the SQLite database into a pandas DataFrame."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(
                "movies.db not found. Please run 'python database/create_db.py' first."
            )

        connection = sqlite3.connect(self.db_path)
        self.movies_df = pd.read_sql_query("SELECT * FROM movies", connection)
        connection.close()

        # Combine genre, keywords, director and cast into one "tags" column.
        # This combined text is what TF-IDF will use to compare movies.
        self.movies_df["tags"] = (
            self.movies_df["genre"] + " " +
            self.movies_df["keywords"] + " " +
            self.movies_df["director"] + " " +
            self.movies_df["cast"]
        ).str.lower()

    def _build_similarity_matrix(self):
        """Build the TF-IDF matrix and compute cosine similarity between all movies."""
        tfidf = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf.fit_transform(self.movies_df["tags"])
        self.similarity_matrix = cosine_similarity(tfidf_matrix)

    def get_all_titles(self):
        """Return a list of all movie titles (used for autocomplete)."""
        return self.movies_df["title"].tolist()

    def search_movies(self, query, limit=8):
        """
        Return a list of movie titles that contain the search query.
        Used for the autocomplete dropdown while typing.
        """
        if not query:
            return []

        query = query.strip().lower()
        matches = self.movies_df[self.movies_df["title"].str.lower().str.contains(query)]
        return matches["title"].head(limit).tolist()

    def get_movie_details(self, title):
        """Return a dict with the details of one movie, or None if not found."""
        row = self.movies_df[self.movies_df["title"].str.lower() == title.strip().lower()]
        if row.empty:
            return None

        row = row.iloc[0]
        return {
            "title": row["title"],
            "genre": row["genre"],
            "director": row["director"],
            "cast": row["cast"],
            "description": row["description"],
            "rating": row["rating"],
        }

    def get_recommendations(self, title, top_n=6):
        """
        Return a list of the top_n most similar movies to the given title.
        Returns None if the movie title does not exist in the dataset.
        """
        matches = self.movies_df[self.movies_df["title"].str.lower() == title.strip().lower()]
        if matches.empty:
            return None

        movie_index = matches.index[0]

        # Get similarity scores of this movie with every other movie
        similarity_scores = list(enumerate(self.similarity_matrix[movie_index]))

        # Sort by similarity score, highest first
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

        # Skip index 0 because that is always the movie itself (similarity = 1.0)
        top_matches = similarity_scores[1:top_n + 1]

        recommendations = []
        for index, score in top_matches:
            movie = self.movies_df.iloc[index]
            recommendations.append({
                "title": movie["title"],
                "genre": movie["genre"],
                "rating": movie["rating"],
                "description": movie["description"],
                "similarity": round(float(score) * 100, 1),  # shown as a % match
            })

        return recommendations
