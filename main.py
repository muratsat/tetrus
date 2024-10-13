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
        self.active_connections: list[WebSocket] = []
        self.next_client_id = 1
        self.client_id: Dict[str, int] = {}

    async def connect(self, websocket: WebSocket, client_ip: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.client_id[client_ip] = self.next_client_id
        self.next_client_id += 1
        self.broadcast({
            "type": "player_connected",
            "data": {
                "client_id": self.client_id[client_ip],
            }
        })

    def get_client_id(self, client_ip: str):
        return self.client_id.get(client_ip)

    def disconnect(self, websocket: WebSocket, client_ip):
        self.active_connections.remove(websocket)
        client_id = self.client_id.get(client_ip)
        self.client_id.pop(client_ip)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ip = f"{websocket.client.host}:{websocket.client.port}"
    await manager.connect(websocket, client_ip=ip)
    client_id = manager.get_client_id(ip)
    await manager.broadcast({
        "type": "player_connected",
        "data": {
            "client_id": client_id
        }
    })

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({
                "type": "message",
                "data": {
                    "client_id": client_id,
                    "message": data
                }
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket, client_ip=ip)

        await manager.broadcast({
            "type": "player_disconnected",
            "data": {
                "client_id": client_id
            }
        })