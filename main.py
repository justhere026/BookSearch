"""
Gutenberg Book Search
Author: Lizbet Caballero Zarate
Date: 5/10/25

Description:
A GUI-based tool for searching book content in a local database or
Project Gutenberg. It allows users to find the 10 most frequent words
in a book, save results locally, and view stored data.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
import requests
import re

BG_COLOR = "#C7A6D9"
BUTTON_COLOR = "#D4B7E0"
BUTTON_TEXT_COLOR = "#ffffff"
TEXT_FIELD_BG = "#E3D1EF"
TEXT_FIELD_FG = "#C7A6D9"
TITLE_COLOR = "#FFFFFF"
ACCENT_COLOR = "#E8C5E9"
SECONDARY_BG_COLOR = "#F2E5F7"
FONT_FAMILY = "Comic Sans MS"


def search_local_database(title):
    """Searches the local SQLite database for a given book title. Returns
    the word frequency if found"""
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT word_frequencies FROM books WHERE title = ?", (title,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to access the database: {e}")
        return None


def save_to_database(title, frequencies):
    """Saves the book title & word frequencies to a SQLite database"""
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, word_frequencies) VALUES (?, ?)", (title, frequencies))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"'{title}' saved to the local database.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Database Error", f"'{title}' is already in the database.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to save data to the database: {e}")


def fetch_book_from_gutenberg(url):
    """Fetches book information from the Gutenberg Project Website"""
    try:
        if not url.startswith("http"):
            raise ValueError("Invalid URL. Make sure it starts with 'http://' or 'https://'.")

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        text = response.text
        words = re.findall(r'\b\w+\b', text.lower())

        frequency = {}
        for word in words:
            frequency[word] = frequency.get(word, 0) + 1

        top_words = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        result = "\n".join([f"{word}: {count}" for word, count in top_words])
        return result

    except requests.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to fetch the book: {e}")
        return None
    except ValueError as e:
        messagebox.showerror("URL Error", str(e))
        return None


def on_search_click():
    """This ensures that there is something in the search bar"""
    title = title_entry.get().strip()
    if not title:
        messagebox.showwarning("Input Error", "Please enter a book title.")
        return

    result = search_local_database(title)
    if result:
        display_result(title, result)
    else:
        messagebox.showinfo("Not Found", f"'{title}' not found in the local database.")


def on_url_search_click():
    """This ensure that there is an URL link in the URL search bar"""
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a book URL.")
        return

    result = fetch_book_from_gutenberg(url)
    if result:
        # Extract title from URL for database storage
        title = url.split("/")[-1].replace(".txt", "").replace("-", " ").title()
        save_to_database(title, result)
        display_result(title, result)


def on_clear_click():
    """This enables the click button to work"""
    title_entry.delete(0, tk.END)
    url_entry.delete(0, tk.END)
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.config(state=tk.DISABLED)


def display_result(title, result):
    """This is what the results display"""
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"** These are the 10 most common words for '{title}' **\n\n{result}")
    result_text.config(state=tk.DISABLED)


# Initialize main window
app = tk.Tk()
app.title("Gutenberg Book Search")
app.geometry("750x900")
app.configure(bg=BG_COLOR)

# Title Input Section
title_frame = tk.Frame(app, bg=BG_COLOR)
title_frame.pack(pady=20)

title_label = tk.Label(title_frame, text="Enter Book Title:", font=(FONT_FAMILY, 14, "bold"), bg=BG_COLOR,
                       fg=TITLE_COLOR)
title_label.pack(anchor="w")
title_entry = tk.Entry(title_frame, width=50, font=(FONT_FAMILY, 12), bg=TEXT_FIELD_BG, fg=TEXT_FIELD_FG)
title_entry.pack(pady=5)

button_frame = tk.Frame(title_frame, bg=BG_COLOR)
button_frame.pack(pady=10)

search_button = tk.Button(button_frame, text="Search", command=on_search_click, bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR,
                          font=(FONT_FAMILY, 12, "bold"), bd=0, padx=20, pady=10, relief="flat", highlightthickness=0)
search_button.pack(side=tk.LEFT, padx=10)


clear_button = tk.Button(button_frame, text="Clear", command=on_clear_click, bg=SECONDARY_BG_COLOR, fg=TEXT_FIELD_FG,
                         font=(FONT_FAMILY, 12, "bold"), bd=0, padx=20, pady=10, relief="flat", highlightthickness=0)
clear_button.pack(side=tk.LEFT, padx=10)

# URL Input Section
url_frame = tk.Frame(app, bg=BG_COLOR)
url_frame.pack(pady=20)

url_label = tk.Label(url_frame, text="Enter Book URL:", font=(FONT_FAMILY, 14, "bold"), bg=BG_COLOR, fg=TITLE_COLOR)
url_label.pack(anchor="w")
url_entry = tk.Entry(url_frame, width=50, font=(FONT_FAMILY, 12), bg=TEXT_FIELD_BG, fg=TEXT_FIELD_FG)
url_entry.pack(pady=5)

url_button = tk.Button(url_frame, text="Fetch and Save", command=on_url_search_click, bg=ACCENT_COLOR,
                       fg=BUTTON_TEXT_COLOR, font=(FONT_FAMILY, 12, "bold"), bd=0, padx=20, pady=10, relief="flat",
                       highlightthickness=0)
url_button.pack(pady=10)
# Result Display Section
result_frame = tk.Frame(app, bg=BG_COLOR)
result_frame.pack(pady=20)

result_text = scrolledtext.ScrolledText(result_frame, width=70, height=25, font=(FONT_FAMILY, 10), wrap=tk.WORD, state=tk.DISABLED, bg=TEXT_FIELD_BG, fg=TEXT_FIELD_FG)
result_text.pack()

app.mainloop()