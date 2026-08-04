from collections import deque

from app.models.events import BridgeEvent
from app.models.sessions import SessionRecord
from app.services.audit_log import audit_log


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}
        self._events: deque[BridgeEvent] = deque(maxlen=200)

    def save(self, session: SessionRecord) -> None:
        self._sessions[session.session_id] = session
        audit_log.append("session.saved", session.model_dump(mode="json"))

    def get(self, session_id: str) -> SessionRecord | None:
        return self._sessions.get(session_id)

    def list(self) -> list[SessionRecord]:
        return list(self._sessions.values())

    def push_event(self, event: BridgeEvent) -> None:
        self._events.append(event)
        audit_log.append("event.pushed", event.model_dump(by_alias=True, mode="json"))

    def list_events(self) -> list[BridgeEvent]:
        return list(self._events)


session_store = InMemorySessionStore()
