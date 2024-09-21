import sqlite3

def setup_database():
    conn = sqlite3.connect('inspection_data.db')
    c = conn.cursor()

    # Create a table for sides and their questions
    c.execute('''CREATE TABLE IF NOT EXISTS sides (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 side_name TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS questions (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 side_id INTEGER,
                 question TEXT,
                 FOREIGN KEY (side_id) REFERENCES sides(id))''')

    # Create a table for users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT,
                 password TEXT)''')

    # Insert admin user
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'pass')")

    # Insert some dummy data
    c.execute("INSERT INTO sides (side_name) VALUES ('Side A')")
    c.execute("INSERT INTO sides (side_name) VALUES ('Side B')")
    c.execute("INSERT INTO sides (side_name) VALUES ('Side C')")

    # Add questions for each side
    c.execute("INSERT INTO questions (side_id, question) VALUES (1, 'What is the site name?')")
    c.execute("INSERT INTO questions (side_id, question) VALUES (1, 'What is the elevation?')")
    c.execute("INSERT INTO questions (side_id, question) VALUES (1, 'What is the noise level?')")

    c.execute("INSERT INTO questions (side_id, question) VALUES (2, 'What is the area size?')")
    c.execute("INSERT INTO questions (side_id, question) VALUES (2, 'What is the wind direction?')")
    c.execute("INSERT INTO questions (side_id, question) VALUES (2, 'Are there terrain changes?')")

    c.execute("INSERT INTO questions (side_id, question) VALUES (3, 'What is the station type?')")
    c.execute("INSERT INTO questions (side_id, question) VALUES (3, 'Is there visible corrosion?')")
    c.execute("INSERT INTO questions (side_id, question) VALUES (3, 'Are there signs of condensation?')")

    conn.commit()
    conn.close()

setup_database()
