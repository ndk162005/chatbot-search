"""
Unified query API.

The same user query is sent to:

1. Chatbot
2. Semantic Search

The response contains the chatbot answer first,
followed by semantic search results.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api",
    tags=["Query"],
)


class QueryRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        description="User question",
    )

    session_id: str = Field(
        default="default",
        description="Conversation session ID",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class QueryResponse(BaseModel):

    chatbot: dict[str, Any]

    semantic_search: dict[str, Any]


@router.post(
    "/query",
    response_model=QueryResponse,
)
def query(
    request: QueryRequest,
) -> QueryResponse:

    user_query = request.query.strip()

    if not user_query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    try:

        # ====================================================
        # 1. CHATBOT
        # ====================================================

        chatbot_response = run_chatbot(
            query=user_query,
            session_id=request.session_id,
        )

        # ====================================================
        # 2. SEMANTIC SEARCH
        # ====================================================

        search_response = run_semantic_search(
            query=user_query,
            top_k=request.top_k,
        )

        # ====================================================
        # 3. COMBINED RESPONSE
        # ====================================================

        return QueryResponse(
            chatbot=chatbot_response,
            semantic_search=search_response,
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


def run_chatbot(
    query: str,
    session_id: str,
) -> dict[str, Any]:
    """
    Connect this function to chatbot LLM answer generator.
    """
    try:
        from app.chatbot.retrieval.retriever import Retriever
        from app.chatbot.database.vector_store import vector_store
        from app.chatbot.embeddings.embedding import get_embedding_model
        from app.chatbot.llm.answer_generator import AnswerGenerator
        from app.chatbot.llm.ollama_client import OllamaClient
        from app.chatbot.llm.conversation_manager import conversation_manager
        from app.chatbot.llm.prompt_builder import PromptBuilder

        retriever = Retriever(vector_store=vector_store, embedding_generator=get_embedding_model())
        chunks = retriever.retrieve(query=query)

        generator = AnswerGenerator(
            ollama_client=OllamaClient(),
            conversation_manager=conversation_manager,
            prompt_builder=PromptBuilder()
        )

        res = generator.generate_answer(
            session_id=session_id,
            question=query,
            context=chunks
        )

        return {
            "session_id": session_id,
            "answer": res.get("answer", "") or f"I am ready to help! Please upload a PDF to ask questions about your documents.",
            "sources": res.get("sources", []),
        }
    except Exception as e:
        return {
            "session_id": session_id,
            "answer": f"I received your question: '{query}'. Please upload a PDF document to start querying.",
            "error": str(e),
            "sources": [],
        }


def run_semantic_search(
    query: str,
    top_k: int,
) -> dict[str, Any]:
    """
    Connect this function to existing semantic search system.
    """
    try:
        from app.semantic_search.search.semantic_search import semantic_search
        results = semantic_search(query=query, top_k=top_k)
        return {
            "results": results
        }
    except Exception as e:
        return {
            "results": [],
            "error": str(e)
        }