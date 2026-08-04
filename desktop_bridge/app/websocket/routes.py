import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.session_store import session_store

router = APIRouter()


@router.websocket("/ws")
async def websocket_events(websocket: WebSocket) -> None:
    session_id = websocket.query_params.get("sessionId")
    after_event_id = websocket.query_params.get("afterEventId")
    await websocket.accept()
    try:
        await websocket.send_json(
            {
                "type": "connection.ready",
                "payload": {
                    "message": "Desktop bridge POC websocket connected.",
                    "bufferedEvents": len(session_store.list_events()),
                    "sessionId": session_id,
                },
            }
        )
        while True:
            events = (
                session_store.list_events_for_session(
                    session_id,
                    after_event_id=after_event_id,
                    limit=100,
                )
                if session_id
                else session_store.list_events()
            )
            for event in events:
                await websocket.send_json(event.model_dump(by_alias=True, mode="json"))
                after_event_id = event.event_id
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
