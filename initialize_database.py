import sqlite3
import requests
import re

# Top 10 Most Known Books with their Gutenberg URLs
books = {
    "Pride and Prejudice": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
    "Moby Dick": "https://www.gutenberg.org/cache/epub/2701/pg2701.txt",
    "Dracula": "https://www.gutenberg.org/cache/epub/345/pg345.txt",
    "Frankenstein": "https://www.gutenberg.org/cache/epub/84/pg84.txt",
    "The Adventures of Sherlock Holmes": "https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
    "Alice's Adventures in Wonderland": "https://www.gutenberg.org/cache/epub/11/pg11.txt",
    "The Picture of Dorian Gray": "https://www.gutenberg.org/cache/epub/174/pg174.txt",
    "Jane Eyre": "https://www.gutenberg.org/cache/epub/1260/pg1260.txt",
    "The Count of Monte Cristo": "https://www.gutenberg.org/cache/epub/1184/pg1184.txt",
    "Little Women": "https://www.gutenberg.org/cache/epub/37106/pg37106.txt"
}


def initialize_database():
    # Create the database file if it doesn't exist
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS books(
                       title TEXT PRIMARY KEY,
                       word_frequencies TEXT
                   )
                   """)
    conn.commit()

    # Prepopulate the database with the top 10 most known books
    for title, url in books.items():
        try:
            print(f"Fetching '{title}'...")
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            text = response.text

            # Extracts & counts the top 10 most frequent words
            words = re.findall(r'\b\w{5,}\b', text.lower())
            frequency = {}
            for word in words:
                frequency[word] = frequency.get(word, 0) + 1

            # Get the top 10 most frequent words
            top_words = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            result = "\n".join([f"{word}: {count}" for word, count in top_words])

            # Save to the database
            cursor.execute("INSERT OR IGNORE INTO books (title, word_frequencies) VALUES (?, ?)", (title, result))
            print(f"'{title}' added to the database.")

        except Exception as e:
            print(f"Failed to add '{title}': {e}")

    # Close the database connection at the end
    conn.commit()
    conn.close()
    print("\n Database initialization and prepopulation complete!")


initialize_database()
