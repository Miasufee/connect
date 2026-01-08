from typing import Dict, Set
from fastapi import WebSocket
from beanie import PydanticObjectId


class ConnectionManager:
    def __init__(self):
        self.active: Dict[PydanticObjectId, Set[WebSocket]] = {}

    async def connect(self, obj_id: PydanticObjectId, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(obj_id, set()).add(ws)

    def disconnect(self, obj_id: PydanticObjectId, ws: WebSocket):
        self.active.get(obj_id, set()).discard(ws)

    async def broadcast(self, obj_id: PydanticObjectId, data: dict):
        for ws in list(self.active.get(obj_id, [])):
            try:
                await ws.send_json(data)
            except:
                self.disconnect(obj_id, ws)


manager = ConnectionManager()
