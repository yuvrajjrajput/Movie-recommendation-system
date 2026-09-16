"""
app.py
-------
Main Flask application for the Movie Suggestion System.

Routes:
  GET  /                        -> loads the main page (search UI)
  GET  /api/search?q=<text>     -> returns matching movie titles (autocomplete)
  GET  /api/recommend/<title>   -> returns movie details + similar movies (JSON)
"""

from flask import Flask, render_template, request, jsonify
from recommender import MovieRecommender

app = Flask(__name__)

# Load the dataset and build the similarity matrix ONCE when the server starts.
# Doing this at startup (instead of on every request) keeps the app fast.
try:
    recommender = MovieRecommender()
except FileNotFoundError as error:
    # This will show a clear message in the terminal if create_db.py was not run yet.
    print(f"ERROR: {error}")
    recommender = None


@app.route("/")
def home():
    """Render the main page."""
    return render_template("index.html")


@app.route("/api/search")
def api_search():
    """
    Autocomplete endpoint.
    Example: /api/search?q=sky  ->  {"results": ["Skyward Horizon"]}
    """
    query = request.args.get("q", "")

    if recommender is None:
        return jsonify({"error": "Database not initialized. Run create_db.py first."}), 500

    results = recommender.search_movies(query)
    return jsonify({"results": results})


@app.route("/api/recommend/<title>")
def api_recommend(title):
    """
    Main recommendation endpoint.
    Returns the searched movie's details plus a list of similar movies.
    """
    if recommender is None:
        return jsonify({"error": "Database not initialized. Run create_db.py first."}), 500

    title = title.strip()
    if not title:
        return jsonify({"error": "Please enter a movie name."}), 400

    movie_details = recommender.get_movie_details(title)
    if movie_details is None:
        return jsonify({
            "error": f"'{title}' was not found in our database. Please check the spelling "
                     f"or try another movie."
        }), 404

    recommendations = recommender.get_recommendations(title)

    return jsonify({
        "movie": movie_details,
        "recommendations": recommendations
    })


if __name__ == "__main__":
    # debug=True auto-reloads the server when you edit code (useful during development).
    # Turn it off (debug=False) before submitting/deploying the project.
    app.run(debug=True)
