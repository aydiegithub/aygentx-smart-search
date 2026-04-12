from typing import List, Dict
from app.llm.base import ChatMessage
from app.constants import MAX_HISTORY
from app.core.logging import Logger

logging = Logger()


class MemoryStore:
    def __init__(self):
        self.sessions: Dict[str, List[ChatMessage]] = {}
        self.max_history = MAX_HISTORY

    def add_message(self, session_id: str, role: str, content: str):
        try:
            logging.info(f"Adding message to session: {session_id}")

            if session_id not in self.sessions:
                logging.info(f"Creating new session: {session_id}")
                self.sessions[session_id] = []

            self.sessions[session_id].append(ChatMessage(
                role=role,
                content=content
            ))

            logging.info(
                f"Message added. Total messages: {len(self.sessions[session_id])}")

            if len(self.sessions[session_id]) > self.max_history:
                logging.warning(
                    f"Session {session_id} exceeded max history. Trimming...")
                self.sessions[session_id] = self.sessions[session_id][-self.max_history:]

        except Exception as e:
            logging.error(
                f"Error adding message to session {session_id}: {str(e)}")

    def get_history(self, session_id: str) -> List[ChatMessage]:
        try:
            logging.info(f"Fetching history for session: {session_id}")
            return self.sessions.get(session_id, [])
        except Exception as e:
            logging.error(
                f"Error fetching history for session {session_id}: {str(e)}")
            return []


memory_store = MemoryStore()
