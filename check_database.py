import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("SELECT title FROM books")
titles = cursor.fetchall()
conn.close()

print("\n Books in Database:")
for title in titles:
    print(title[0])
