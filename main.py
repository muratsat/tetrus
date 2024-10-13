from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from lobby import Lobby

app = FastAPI()

@app.get("/")
def read_root():
    return FileResponse("index.html")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.next_client_id = 1
        self.lobby = Lobby()
        self.client_id: Dict[str, int] = {}

    async def connect(self, websocket: WebSocket, client_ip: str):
        await websocket.accept()
        client_id = self.next_client_id
        self.active_connections[client_id] = websocket
        self.next_client_id += 1
        self.client_id[client_ip] = client_id
        self.lobby.add_player(client_id)
        player = self.lobby.players[client_id]

        await self.send_personal_message(client_id=client_id, message={
            "type": "welcome",
            "data": {
                "client_id": player.id,
                "username": player.username,
                "players": [
                    {"id": player.id, "username": player.username, "ready": player.ready} for player in self.lobby.players.values()
                ]
            }
        })

        await self.broadcast({
            "type": "player_connected",
            "data": {
                "id": player.id,
                "username": player.username,
                "ready": player.ready
            }
        })

    def get_client_id(self, client_ip: str):
        return self.client_id.get(client_ip)

    async def disconnect(self, client_ip):
        client_id = self.get_client_id(client_ip)
        self.lobby.remove_player(client_id)
        self.active_connections.pop(client_id)
        self.client_id.pop(client_ip)

        await manager.broadcast({
            "type": "player_disconnected",
            "data": {
                "client_id": client_id
            }
        })

    async def send_personal_message(self, client_id, message):
        websocket = self.active_connections.get(client_id)
        print("Sending message to client", client_id, message)
        if websocket:
            await websocket.send_json(message)

    async def broadcast(self, message):
        for _, connection in self.active_connections.items():
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ip = f"{websocket.client.host}:{websocket.client.port}"
    await manager.connect(websocket, client_ip=ip)
    client_id = manager.get_client_id(ip)

    try:
        while True:
            data = await websocket.receive_json()
            response = manager.lobby.handle_message(client_id, data)
            if response and response["type"] == "broadcast":
                await manager.broadcast(response["data"])

    except WebSocketDisconnect:
        await manager.disconnect(client_ip=ip)
