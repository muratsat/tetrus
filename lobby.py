
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
    # random_num = lambda: random.randint(1000, 9999)
    return f"{random_item(adjectives)}_{random_item(nouns)}"


directions = {
    "ArrowUp": (0, -1),
    "ArrowDown": (0, 1),
    "ArrowLeft": (-1, 0),
    "ArrowRight": (1, 0),
}
CLOCKWISE = 'x'
COUNTER_CLOCKWISE = 'z'

SHAPES = [
    [
        [1, 1, 1, 1]
    ],
    [ 
        [1, 1],
        [1, 1] 
    ],
    [ 
        [1, 1, 1],
        [0, 1, 0],
    ],
    [ 
        [1, 1, 0],
        [0, 1, 1],
    ],
    [ 
        [0, 1, 1],
        [1, 1, 0],
    ],
    [ 
        [1, 0, 0],
        [1, 1, 1],
    ],
    [ 
        [0, 0, 1],
        [1, 1, 1],
    ],
]

def rotate_clockwise(matrix):
    # Step 1: Transpose the matrix
    transposed = [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
    # Step 2: Reverse each row
    rotated = [row[::-1] for row in transposed]
    return rotated


def rotate_counterclockwise(matrix):
    # Step 1: Transpose the matrix
    transposed = [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
    # Step 2: Reverse each column
    rotated = transposed[::-1]
    return rotated


class Piece:
    def __init__(self, shape, x, y):
        self.shape = shape
        self.x = x
        self.y = y

class Player:
    def __init__(self, id: int):
        self.username = random_name()
        self.id = id
        self.ready = False
        self.piece: Piece | None = None

    # def move(self, direction):
    #     self.x += directions[direction][0]
    #     self.y += directions[direction][1]


class Game:
    BOARD_WIDTH = 10
    BOARD_HEIGHT = 20

    def __init__(self):
        self.state = "IDLE"
        self.players: Dict[str, Player] = {}

    def start(self):
        self.state = "RUNNING"
        self.board = [[0 for _ in range(self.BOARD_WIDTH)] for _ in range(self.BOARD_HEIGHT)]
        self.game_thread = threading.Thread(target=self._game_loop)
        self.game_thread.start()

    def current_state(self):
        return {
            "tick": self.tick,
            "board": self.board,
            "players": [
                {
                    "id": player.id,
                    "username": player.username,
                } for player in self.players.values()
            ]
        }


    def _reset_game(self):
        self.state = "IDLE"
        for id in self.players.keys():
            self.players[id].x = 0
            self.players[id].y = 0
            self.players[id].ready = False


    def _can_place_shape(self, shape, x, y):
        for dy in range(len(shape)):
            for dx in range(len(shape[dy])):
                if shape[dy][dx] == 0:
                    continue
                within_bounds = x + dx >= 0 and x + dx < self.BOARD_WIDTH and y + dy >= 0 and y + dy < self.BOARD_HEIGHT
                if not within_bounds:
                    return False
                if self.board[y + dy][x + dx] != 0:
                    return False

        return True

    def _spawn_piece(self, player_id):
        cannot_spawn = True
        shape = SHAPES[random.SystemRandom().randint(0, len(SHAPES) - 1)]
        for i in range(self.BOARD_WIDTH):
            x = self.BOARD_WIDTH // 2
            x += i if i % 2 == 0 else -i
            y = 0
            if self._can_place_shape(shape, x, y):
                cannot_spawn = False
                self.players[player_id].piece = Piece(shape, x, y)
                for dy in range(len(shape)):
                    for dx in range(len(shape[dy])):
                        self.board[y + dy][x + dx] = player_id * shape[dy][dx]
                break
        if cannot_spawn:
            self._reset_game()

    def _gravitate(self):
        for player in self.players.values():
            if not player.piece:
                continue
            shape = player.piece.shape
            x = player.piece.x
            y = player.piece.y
            for dy in range(len(shape)):
                for dx in range(len(shape[dy])):
                    if shape[dy][dx] != 0:
                        self.board[y + dy][x + dx] = 0

            if self._can_place_shape(shape, x, y + 1):
                player.piece.y += 1
                y = player.piece.y
            else:
                player.piece = None

            for dy in range(len(shape)):
                for dx in range(len(shape[dy])):
                    if shape[dy][dx] != 0:
                        self.board[y + dy][x + dx] = player.id

    def gravitate_row(self, row: int):
        current_row = row
        for y in range(row + 1, self.BOARD_HEIGHT):
            empty = all(self.board[y][x] == 0 for x in range(self.BOARD_WIDTH))
            # if empty swap row with current row
            if empty:
                self.board[current_row], self.board[y] = self.board[y], self.board[current_row]
                current_row = y


    def _burn_lines(self):
        for player in self.players.values():
            if not player.piece:
                continue
            shape = player.piece.shape
            for dy in range(len(shape)):
                for dx in range(len(shape[dy])):
                    if shape[dy][dx] != 0:
                        self.board[player.piece.y + dy][player.piece.x + dx] = 0

        for y in range(self.BOARD_HEIGHT):
            full = all(self.board[y][x] == 1 for x in range(self.BOARD_WIDTH))
            if full:
                for x in range(self.BOARD_WIDTH):
                    self.board[y][x] = 0

        for y in range(self.BOARD_HEIGHT -1, -1, -1):
            empty = all(self.board[y][x] == 0 for x in range(self.BOARD_WIDTH))
            if not empty:
                self.gravitate_row(y)

        for player in self.players.values():
            if not player.piece:
                continue
            shape = player.piece.shape
            for dy in range(len(shape)):
                for dx in range(len(shape[dy])):
                    if shape[dy][dx] != 0:
                        self.board[player.piece.y + dy][player.piece.x + dx] = player.id


    def _update_board(self):
        for player in self.players.values():
            if not player.piece:
                self._spawn_piece(player.id)
                continue
        self._gravitate()
        self._burn_lines()


    def player_rotate(self, player_id, direction):
        if not self.players[player_id].piece:
            return
        shape = self.players[player_id].piece.shape
        rotated_shape = rotate_clockwise(shape) if direction == CLOCKWISE else rotate_counterclockwise(shape)

        for dy in range(len(shape)):
            for dx in range(len(shape[dy])):
                if shape[dy][dx] != 0:
                    self.board[self.players[player_id].piece.y + dy][self.players[player_id].piece.x + dx] = 0

        if self._can_place_shape(rotated_shape, self.players[player_id].piece.x, self.players[player_id].piece.y):
            self.players[player_id].piece.shape = rotated_shape
            shape = self.players[player_id].piece.shape

        for dy in range(len(shape)):
            for dx in range(len(shape[dy])):
                if shape[dy][dx] != 0:
                    self.board[self.players[player_id].piece.y + dy][self.players[player_id].piece.x + dx] = player_id


    def player_move(self, player_id, direction):
        if not self.players[player_id].piece:
            return

        if direction != "ArrowLeft" and direction != "ArrowRight" and direction != "ArrowDown":
            return

        shape = self.players[player_id].piece.shape
        x = self.players[player_id].piece.x
        y = self.players[player_id].piece.y

        for dy in range(len(shape)):
            for dx in range(len(shape[dy])):
                if shape[dy][dx] != 0:
                    self.board[y + dy][x + dx] = 0

        tx, ty = directions[direction]
        if self._can_place_shape(shape, x + tx, y + ty):
            self.players[player_id].piece.x += tx
            self.players[player_id].piece.y += ty

        x = self.players[player_id].piece.x
        y = self.players[player_id].piece.y
        for dy in range(len(shape)):
            for dx in range(len(shape[dy])):
                if shape[dy][dx] != 0:
                    self.board[y + dy][x + dx] += player_id


    TICKS_PER_SECOND = 2
    def _game_loop(self):
        self.tick = 0
        while self.state == "RUNNING":
            time.sleep(1 / self.TICKS_PER_SECOND)
            self._update_board()
            self.tick += 1
            # if (self.tick > 100):
            #     self._reset_game()


    def add_player(self, client_id: int):
        self.players[client_id] = Player(client_id)

    def remove_player(self, client_id: int):
        piece = self.players[client_id].piece
        if piece:
            for dy in range(len(piece.shape)):
                for dx in range(len(piece.shape[dy])):
                    if piece.shape[dy][dx] != 0:
                        self.board[piece.y + dy][piece.x + dx] = 0
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
            if message["data"]["direction"] == "ArrowLeft" or message["data"]["direction"] == "ArrowRight" or message["data"]["direction"] == "ArrowDown":
                self.game.player_move(client_id, message["data"]["direction"])
            elif message["data"]["direction"] == "z" or message["data"]["direction"] == "x":
                self.game.player_rotate(client_id, message["data"]["direction"])

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
