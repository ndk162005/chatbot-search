"""
LLM package for the PDF chatbot.

This package handles:
- Ollama communication
- Conversation memory
- Prompt construction
- Final answer generation
"""

from .ollama_client import OllamaClient
from .conversation_manager import ConversationManager
from .prompt_builder import PromptBuilder
from .answer_generator import AnswerGenerator

__all__ = [
    "OllamaClient",
    "ConversationManager",
    "PromptBuilder",
    "AnswerGenerator",
]