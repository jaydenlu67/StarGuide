import sqlite3

connection = sqlite3.connect('database.db')
cur = connection.cursor()

# Create a table to store searches (Success Criterion 5)
cur.execute('''
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_date TEXT,
        location TEXT,
        score INTEGER
    )
''')

connection.commit()
connection.close()
print("Database initialized!")