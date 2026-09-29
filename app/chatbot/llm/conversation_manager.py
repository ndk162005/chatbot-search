"""
Conversation manager for the PDF chatbot.

Maintains conversation history for each chat session.
"""

from typing import Dict, List


class ConversationManager:
    """
    Manages conversation history for multiple chat sessions.

    Each session contains a list of messages in the format:

    {
        "role": "user" | "assistant",
        "content": "message text"
    }
    """

    def __init__(self, max_messages: int = 10):
        """
        Initialize the conversation manager.

        Args:
            max_messages: Maximum number of messages retained per session.
        """
        self.max_messages = max_messages
        self.sessions: Dict[str, List[dict]] = {}

    def create_session(self, session_id: str) -> None:
        """
        Create a new conversation session if it does not already exist.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """
        Add a message to a conversation.

        Args:
            session_id: Unique ID of the conversation.
            role: Either 'user' or 'assistant'.
            content: Message content.
        """

        if role not in {"user", "assistant"}:
            raise ValueError(
                "role must be either 'user' or 'assistant'"
            )

        self.create_session(session_id)

        self.sessions[session_id].append(
            {
                "role": role,
                "content": content
            }
        )

        # Keep only the most recent messages
        if len(self.sessions[session_id]) > self.max_messages:
            self.sessions[session_id] = (
                self.sessions[session_id][-self.max_messages:]
            )

    def get_history(self, session_id: str) -> List[dict]:
        """
        Return the conversation history for a session.
        """

        return self.sessions.get(session_id, []).copy()

    def clear_session(self, session_id: str) -> None:
        """
        Delete all conversation history for a session.
        """

        self.sessions.pop(session_id, None)

    def session_exists(self, session_id: str) -> bool:
        """
        Check whether a conversation session exists.
        """

        return session_id in self.sessions

    def get_message_count(self, session_id: str) -> int:
        """
        Return the number of stored messages in a session.
        """

        return len(self.sessions.get(session_id, []))


conversation_manager = ConversationManager()