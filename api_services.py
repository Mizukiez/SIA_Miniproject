# api_services.py
import requests
import os

# --- API KEYS ---
TMDB_API_KEY = "7ab8c5f88c473cc1334e2ccee43d801d"
RAWG_API_KEY = "36505237ebda4160a2531e9346741eb8"

# --- MOVIES (TMDB) ---
def search_tmdb(query):
    """Searches TMDB for movies."""
    if not query: return []
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        data = requests.get(url).json()
        return data.get("results", [])
    except Exception as e:
        print(f"TMDB Error: {e}")
        return []

def download_tmdb_image(poster_path, movie_id, save_dir):
    """Downloads a poster from TMDB and saves it locally."""
    if not poster_path: return None
    try:
        url = "https://image.tmdb.org/t/p/w500" + poster_path
        fname = f"{movie_id}.jpg"
        local_path = os.path.join(save_dir, fname)

        response = requests.get(url)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return local_path
    except Exception as e:
        print(f"Download Error: {e}")
    return None

# --- GAMES (RAWG) ---
def search_rawg(query):
    """Searches RAWG for games."""
    if not query: return []
    try:
        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={query}&page_size=10"
        data = requests.get(url).json()
        return data.get("results", [])
    except Exception as e:
        print(f"RAWG Error: {e}")
        return []

def download_rawg_image(image_url, game_id, save_dir):
    """Downloads a game background image."""
    if not image_url: return None
    try:
        fname = f"game_{game_id}.jpg"
        local_path = os.path.join(save_dir, fname)

        response = requests.get(image_url)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return local_path
    except Exception as e:
        print(f"Download Error: {e}")
    return None

# --- MUSIC (DEEZER) ---
def search_deezer(query):
    """Searches Deezer for tracks."""
    if not query: return []
    try:
        url = f"https://api.deezer.com/search?q={query}"
        response = requests.get(url)
        data = response.json()
        return data.get('data', [])
    except Exception as e:
        print(f"Deezer Error: {e}")
        return []