"""
Answer generation module for the PDF chatbot.

This module coordinates:
    User question
        +
    Retrieved document context
        +
    Conversation history
        ↓
    PromptBuilder
        ↓
    Ollama
        ↓
    Final grounded answer
"""

from typing import Any

from .ollama_client import OllamaClient
from .conversation_manager import ConversationManager
from .prompt_builder import PromptBuilder


class AnswerGenerator:
    """
    Generates document-grounded answers using Ollama.
    """

    def __init__(
        self,
        ollama_client: OllamaClient,
        conversation_manager: ConversationManager,
        prompt_builder: PromptBuilder,
    ) -> None:

        self.ollama_client = ollama_client
        self.conversation_manager = conversation_manager
        self.prompt_builder = prompt_builder

    def generate_answer(
        self,
        session_id: str,
        question: str,
        context: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Generate an answer using the retrieved document context.

        Parameters
        ----------
        session_id:
            Unique identifier for the current conversation.

        question:
            Current user question.

        context:
            Retrieved document chunks.

        Returns
        -------
        dict
            Contains the generated answer and source information.
        """

        is_greeting = question.strip().lower() in [
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
            "good evening", "how are you", "who are you", "what can you do", "help"
        ]

        if is_greeting:
            greeting_resp = "Hello! I am your PDF AI Assistant. How can I help you with your documents today?"
            self.conversation_manager.add_message(
                session_id=session_id, role="user", content=question
            )
            self.conversation_manager.add_message(
                session_id=session_id, role="assistant", content=greeting_resp
            )
            return {"answer": greeting_resp, "sources": []}

        # ---------------------------------------------------------
        # 1. Get previous conversation history
        # ---------------------------------------------------------

        history = self.conversation_manager.get_history(session_id)

        # ---------------------------------------------------------
        # 2. Build the grounded prompt
        # ---------------------------------------------------------

        prompt = self.prompt_builder.build_prompt(
            question=question,
            context=context,
            conversation_history=history,
        )

        # ---------------------------------------------------------
        # 3. Send prompt to Ollama
        # ---------------------------------------------------------

        answer = self.ollama_client.generate(
            prompt=prompt
        )

        # ---------------------------------------------------------
        # 4. Store the conversation
        # ---------------------------------------------------------

        self.conversation_manager.add_message(
            session_id=session_id,
            role="user",
            content=question,
        )

        self.conversation_manager.add_message(
            session_id=session_id,
            role="assistant",
            content=answer,
        )

        # ---------------------------------------------------------
        # 5. Extract source information
        # ---------------------------------------------------------

        sources = self._extract_sources(context)

        # ---------------------------------------------------------
        # 6. Return final response
        # ---------------------------------------------------------

        return {
            "answer": answer,
            "sources": sources,
        }

    @staticmethod
    def _extract_sources(
        context: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Extract source metadata from retrieved document chunks.

        The LLM does NOT generate the source information.
        Sources come directly from the retrieval system.
        """

        sources = []

        seen = set()

        for item in context:

            filename = item.get("filename")
            page_number = item.get("page_number")
            paragraph_number = item.get("paragraph_number")
            text = item.get("text")

            source_key = (
                filename,
                page_number,
                paragraph_number,
            )

            # Prevent duplicate sources
            if source_key in seen:
                continue

            seen.add(source_key)

            sources.append(
                {
                    "filename": filename,
                    "page_number": page_number,
                    "paragraph_number": paragraph_number,
                    "text": text,
                }
            )

        return sources