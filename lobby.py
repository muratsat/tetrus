
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
    return f"{random_item(adjectives)}-{random_item(nouns)}-{random_num()}"

class Player:
    def __init__(self, id: str):
        self.username = random_name()
        self.id = id

class Lobby:
    def __init__(self):
        self.player_id: Dict[str, int] = {}
        self.active_connections: Dict[id, WebSocket] = {}
        self.players: Dict[str, Player] = {}
        self.next_player_id = 1
    
    def add_player(self, client_address: str):
        client_id = self.next_player_id
        self.next_player_id += 1
        self.player_id[client_address] = client_id
        self.players[client_id] = Player(client_id)
        return client_id

    async def start_websocket(self, websocket: WebSocket):
        await websocket.accept()
        addr = f"{websocket.client.host}:{websocket.client.port}"
        client_id = self.add_player(addr)

        connection = self.active_connections.get(client_id)
        if connection:
            await connection.close()

        self.active_connections[client_id] = websocket
        await self.broadcast(json.dumps({
            "type": "player_connected", 
            "data": {
                "id": client_id,
                "username": self.players.get(client_id).username
            }
        }))
        await self.send_personal_message(client_id=client_id, message=json.dumps({
            "type": "welcome",
            "data": {
                "players": [
                    {"id": player.id, "username": player.username} for player in self.players.values()
                ]
            }
        }))

    async def disconnect(self, client_address: str):
        client_id = self.player_id.get(client_address)
        player = self.players.get(client_id)
        self.active_connections.pop(client_id)
        self.players.pop(client_id)
        await self.broadcast(json.dumps({
            "type": "player_disconnected", 
            "data": {
                "id": client_id,
                "username": player.username
            }
        }))

    async def send_personal_message(self, client_id: str, message: str):
        connection = self.active_connections.get(client_id)
        if connection: 
            await connection.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    def handle_message(self, client_address: str, message: str):
        player_id = self.player_id.get(client_address)
        player = self.players.get(player_id)
        print(f"Got message from {player.username}: {message}")