from fastapi import APIRouter, WebSocket

from app.services.session_store import session_store

router = APIRouter()


@router.websocket("/ws")
async def websocket_events(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        await websocket.send_json(
            {
                "type": "connection.ready",
                "payload": {
                    "message": "Desktop bridge POC websocket connected.",
                    "bufferedEvents": len(session_store.list_events()),
                },
            }
        )
        for event in session_store.list_events():
            await websocket.send_json(event.model_dump(by_alias=True, mode="json"))
    finally:
        await websocket.close()
