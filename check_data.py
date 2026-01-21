import sqlite3

# Connect to database
conn = sqlite3.connect('database.db')
cur = conn.cursor()

try:
    # SQL Query: Fetch every column and every row stored in the 'searches' table
    cur.execute("SELECT * FROM searches")
    rows = cur.fetchall()

    # Determine if the database has any records yet
    if not rows:
        print("The table is empty. Try submitting a search on your website first!")
    else:
        print("--- Saved Searches ---")
        for row in rows:
            print(f"ID: {row[0]} | Date: {row[1]} | Location: {row[2]} | Score: {row[3]}")
except sqlite3.OperationalError:
    # if no database table yet 
    print("Error: The 'searches' table doesn't exist yet. Did you run init_db.py?")

conn.close()