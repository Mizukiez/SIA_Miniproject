# api_services.py
import requests
import os

RAWG_API_KEY = "36505237ebda4160a2531e9346741eb8" # Free key

def search_rawg(query):
    if not query: return []
    try:
        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={query}&page_size=10"
        data = requests.get(url).json()
        return data.get("results", [])
    except Exception as e:
        print(f"RAWG Error: {e}")
        return []

def download_rawg_image(image_url, game_id, save_dir):
    if not image_url: return None
    try:
        if not os.path.exists(save_dir): os.makedirs(save_dir)
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