import requests

from src.backend.models.player import Player

def get_player_by_name(username: str) -> Player | None:
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if response.status_code == 200:
        return Player(**response.json())
    return None