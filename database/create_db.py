"""
create_db.py
-------------
Run this file ONCE before starting the Flask app.

What it does:
1. Reads the movie data from data/movies.csv
2. Creates a SQLite database file at database/movies.db
3. Creates a "movies" table and inserts all the rows from the CSV

Usage:
    python database/create_db.py
"""

import sqlite3
import csv
import os

# Path setup (works no matter which folder you run the script from)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "movies.csv")
DB_PATH = os.path.join(BASE_DIR, "database", "movies.db")


def create_database():
    # If an old database already exists, remove it so we always start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Create the movies table
    cursor.execute("""
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            director TEXT NOT NULL,
            cast TEXT NOT NULL,
            keywords TEXT NOT NULL,
            description TEXT NOT NULL,
            rating REAL NOT NULL
        )
    """)

    # Read the CSV file and insert every row into the table
    with open(CSV_PATH, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows_inserted = 0
        for row in reader:
            cursor.execute("""
                INSERT INTO movies (id, title, genre, director, cast, keywords, description, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["id"]),
                row["title"].strip(),
                row["genre"].strip(),
                row["director"].strip(),
                row["cast"].strip(),
                row["keywords"].strip(),
                row["description"].strip(),
                float(row["rating"]),
            ))
            rows_inserted += 1

    connection.commit()
    connection.close()

    print(f"Database created successfully at: {DB_PATH}")
    print(f"Total movies inserted: {rows_inserted}")


if __name__ == "__main__":
    create_database()
