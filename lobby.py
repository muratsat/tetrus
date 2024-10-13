
import json
import random
from typing import Dict

from fastapi import WebSocket


def random_name():
    adjectives = [
      "Adorable",
      "Charming",
      "Exquisite",
      "Elegant",
      "Fantastic",
      "Fabulous",
      "Glamorous",
      "Incredible",
      "Magnificent",
      "Marvelous",
      "Pretty",
      "Radiant",
      "Stunning",
      "Demure",
    ]
    nouns = [
      "Boorsoque",
      "Beshbarmak",
      "Kymyz",
      "Karshkyr",
      "Arstan",
      "Torpok",
      "Kozu",
    ]

    random_item = lambda arr: arr[random.randint(0, len(arr) - 1)]
    random_num = lambda: random.randint(1000, 9999)
    return f"{random_item(adjectives)}_{random_item(nouns)}"


class Player:
    def __init__(self, id: int):
        self.username = random_name()
        self.id = id
        self.ready = False


class Lobby:
    def __init__(self, ):
        self.players: Dict[str, Player] = {}
    
    def add_player(self, client_id: int):
        self.players[client_id] = Player(client_id)
    
    def remove_player(self, client_id: int):
        self.players.pop(client_id)

    def update_player(self, client_id: int, username: str | None, ready: bool | None):
        # update if not None
        if username:
            self.players[client_id].username = username
        if ready:
            self.players[client_id].ready = ready
    
    def handle_message(self, client_id: int, message):
        print(f"Got message from {client_id}: {message}")

        if message["type"] == "chat_message":
            return {
                "type": "broadcast",
                "data": {
                    "type": "chat_message",
                    "data": {
                        "id": client_id,
                        "username": self.players[client_id].username,
                        "message_text": message["data"]["message_text"],
                    }
                }
            }
        
        if message["type"] == "edit_user":
            self.players[client_id].username = message["data"]["username"]
            self.players[client_id].ready = message["data"]["ready"]
            return {
                "type": "broadcast",
                "data": {
                    "type": "player_updated",
                    "data": {
                        "id": client_id,
                        "username": self.players[client_id].username,
                        "ready": self.players[client_id].ready,
                    }
                }
            }
