from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from lobby import Lobby

app = FastAPI()

@app.get("/")
def read_root():
    # serve index.html
    return FileResponse("index.html")


lobby = Lobby()
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_address = f"{websocket.client.host}:{websocket.client.port}"
    await lobby.start_websocket(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            lobby.handle_message(client_address=client_address, message=data)
    except WebSocketDisconnect:
        await lobby.disconnect(client_address=client_address)