
from enum import Enum
import json
import random
import time
from typing import Dict
import threading

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

    random_item = lambda arr: arr[random.SystemRandom().randint(0, len(arr) - 1)]
    random_num = lambda: random.randint(1000, 9999)
    return f"{random_item(adjectives)}_{random_item(nouns)}"


directions = {
    "ArrowUp": (0, -1),
    "ArrowDown": (0, 1),
    "ArrowLeft": (-1, 0),
    "ArrowRight": (1, 0),
}

class Player:
    def __init__(self, id: int):
        self.username = random_name()
        self.id = id
        self.ready = False
        self.x = 0
        self.y = 0

    def move(self, direction):
        self.x += directions[direction][0]
        self.y += directions[direction][1]


class Game:

    def __init__(self):
        self.state = "IDLE"
        self.players: Dict[str, Player] = {}


    def start(self):
        self.state = "RUNNING"
        self.game_thread = threading.Thread(target=self._game_loop)
        self.game_thread.start()

    def current_state(self):
        return {
            "tick": self.tick,
            "players": [
                {
                    "id": player.id,
                    "username": player.username,
                    "x": player.x,
                    "y": player.y,
                } for player in self.players.values()
            ]
        }

    TICKS_PER_SECOND = 60

    def _reset_game(self):
        self.state = "IDLE"
        for id in self.players.keys():
            self.players[id].x = 0
            self.players[id].y = 0
            self.players[id].ready = False

    def _game_loop(self):
        self.tick = 0
        while self.state == "RUNNING":
            time.sleep(1 / self.TICKS_PER_SECOND)
            self.tick += 1
            if (self.tick > 100):
                self._reset_game()


    def add_player(self, client_id: int):
        self.players[client_id] = Player(client_id)

    def remove_player(self, client_id: int):
        self.players.pop(client_id)

    def update_player(self, client_id: int, username: str | None, ready: bool | None):
        if self.state == "RUNNING":
            return

        if username:
            self.players[client_id].username = username
        if ready:
            self.players[client_id].ready = ready


class Lobby:
    def __init__(self, ):
        self.game = Game()

    def handle_message(self, client_id: int, message):

        if message["type"] == "chat_message":
            return {
                "type": "broadcast",
                "data": {
                    "type": "chat_message",
                    "data": {
                        "id": client_id,
                        "username": self.game.players[client_id].username,
                        "message_text": message["data"]["message_text"],
                    }
                }
            }

        elif message["type"] == "move":
            if self.game.state != "RUNNING":
                return
            self.game.players[client_id].move(message["data"]["direction"])

        elif message["type"] == "edit_user":
            if self.game.state != "IDLE":
                return

            self.game.update_player(client_id, message["data"]["username"], message["data"]["ready"])
            everyone_ready = all([player.ready for player in self.game.players.values()]) and len(self.game.players) > 1
            if everyone_ready:
                self.game.state = "READY"

            return {
                "type": "broadcast",
                "data": {
                    "type": "player_updated",
                    "data": {
                        "id": client_id,
                        "username": self.game.players[client_id].username,
                        "ready": self.game.players[client_id].ready,
                    }
                }
            }
