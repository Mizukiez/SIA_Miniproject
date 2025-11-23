# db.py
import sqlite3
import hashlib

DB_NAME = "my_app_db.sqlite"


def initialize_db():
    """Initialize tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # USERS TABLE (Updated with firstname, lastname)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        firstname TEXT,
        lastname TEXT,
        email TEXT,
        bio TEXT,
        display_name TEXT
    )''')

    # MOVIES TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        genre TEXT,
        image_path TEXT,
        user_id INTEGER,
        is_favorite INTEGER DEFAULT 0
    )''')

    # GAMES / CHARACTERS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        level INTEGER,
        hp INTEGER,
        xp INTEGER,
        data TEXT
    )''')

    # MUSIC SONGS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        artist TEXT,
        album TEXT, 
        preview_path TEXT,
        cover_url TEXT,
        is_manual INTEGER DEFAULT 0,
        is_favorite INTEGER DEFAULT 0
    )''')

    # PLAYLISTS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        user_id INTEGER
    )''')

    # PLAYLIST SONGS LINK TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS playlist_songs (
        playlist_id INTEGER,
        song_id INTEGER
    )''')

    conn.commit()
    conn.close()


# Run init on module load
initialize_db()


# ---------------------------------------------------------
# USER FUNCTIONS (UPDATED)
# ---------------------------------------------------------
def create_user(firstname, lastname, email, username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    p_hash = hashlib.sha256(password.encode()).hexdigest()

    # Auto-set display name to First Name
    display_name = f"{firstname} {lastname}"

    try:
        c.execute("""
            INSERT INTO users (firstname, lastname, email, username, password_hash, display_name) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (firstname, lastname, email, username, p_hash, display_name))
        conn.commit()
        uid = c.lastrowid
        return uid
    except sqlite3.IntegrityError:
        return None  # Username likely exists
    finally:
        conn.close()


def find_user(username, password=None):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if password:
        p_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, p_hash))
    else:
        c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None


def update_user_profile(uid, display_name, email, bio):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET display_name=?, email=?, bio=? WHERE id=?",
              (display_name, email, bio, uid))
    conn.commit()
    conn.close()


# ---------------------------------------------------------
# MOVIE FUNCTIONS
# ---------------------------------------------------------
def add_movie(title, genre, img_path, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO movies (title, genre, image_path, user_id) VALUES (?,?,?,?)",
              (title, genre, img_path, user_id))
    conn.commit()
    conn.close()


def list_movies(search_txt=""):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    sql = "SELECT * FROM movies"
    params = []
    if search_txt:
        sql += " WHERE title LIKE ?"
        params.append(f"%{search_txt}%")
    c.execute(sql, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def toggle_favorite(mid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE movies SET is_favorite = NOT is_favorite WHERE id=?", (mid,))
    conn.commit()
    conn.close()


def delete_movie(mid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM movies WHERE id=?", (mid,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------
# GAME FUNCTIONS
# ---------------------------------------------------------
def save_character(user_id, name, level, hp, xp, data_json):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO characters (user_id, name, level, hp, xp, data) VALUES (?,?,?,?,?,?)",
              (user_id, name, level, hp, xp, data_json))
    conn.commit()
    conn.close()


def list_characters(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM characters WHERE user_id=?", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ---------------------------------------------------------
# MUSIC FUNCTIONS
# ---------------------------------------------------------
def add_song(title, artist, album, preview_path, cover_url, is_manual=0):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM songs WHERE title=? AND artist=?", (title, artist))
    row = c.fetchone()
    if row:
        song_id = row[0]
    else:
        c.execute("INSERT INTO songs (title, artist, album, preview_path, cover_url, is_manual) VALUES (?,?,?,?,?,?)",
                  (title, artist, album, preview_path, cover_url, is_manual))
        song_id = c.lastrowid
    conn.commit()
    conn.close()
    return song_id


def toggle_song_favorite(song_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE songs SET is_favorite = NOT is_favorite WHERE id=?", (song_id,))
    conn.commit()
    conn.close()


def get_favorites():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM songs WHERE is_favorite=1")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_playlists(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM playlists WHERE user_id=?", (user_id,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def create_playlist(name, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO playlists (name, user_id) VALUES (?,?)", (name, user_id))
    conn.commit()
    conn.close()


def add_to_playlist(playlist_id, song_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?,?)", (playlist_id, song_id))
    conn.commit()
    conn.close()


def get_playlist_songs(playlist_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = '''SELECT s.* FROM songs s 
               JOIN playlist_songs p ON s.id = p.song_id 
               WHERE p.playlist_id = ?'''
    c.execute(query, (playlist_id,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows