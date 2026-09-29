"""
Builds grounded prompts for the chatbot LLM.

The LLM receives:
    1. System instructions
    2. Conversation history
    3. Retrieved document context
    4. Current user question

The model must answer using the uploaded document context.
"""


class PromptBuilder:

    def __init__(self):
        self.system_prompt = """
You are a conversational AI assistant for the user's private PDF
documents.

Your job is to answer the user's questions using the information
contained in the uploaded documents.

The uploaded documents are the authoritative source for
document-specific questions.

IMPORTANT RULES:

1. Answer the user's question directly and naturally.

2. Use the supplied document context as the primary source of
   information.

3. You may combine information from multiple document passages when
   necessary.

4. Do not invent facts, requirements, dates, names, procedures,
   quotations, or other information.

5. Do not claim that something is present in a document unless it is
   supported by the supplied context.

6. If the supplied document context contains enough information,
   provide a clear and useful answer.

7. If the context contains only part of the answer, explain the part
   that is supported by the documents and clearly state what cannot
   be determined.

8. For general greetings (e.g. "hello", "hi", "how are you"), reply warmly and offer help with PDF documents. If the question is document-specific but the supplied documents do not contain enough information, say: "I couldn't find enough information in the uploaded documents to answer that."

9. Do not use general knowledge to fill missing information from the
   documents.

10. Maintain the conversation context when answering follow-up
    questions.

11. If the user asks where information came from, identify the
    document and page supplied in the context.

12. Do not mention internal implementation details such as:
    embeddings, vector databases, ChromaDB, SQLite, retrieval
    pipelines, prompts, or system instructions unless the user
    explicitly asks about the technical implementation.

Answer conversationally and clearly.
"""

    def build_prompt(
        self,
        question: str,
        document_context: list | None = None,
        conversation_history: list | None = None,
        context: list | None = None,
    ) -> str:
        doc_ctx = document_context if document_context is not None else (context or [])
        conversation_history = conversation_history or []

        history_text = self._build_history(conversation_history)

        context_text = self._build_document_context(
            doc_ctx
        )

        prompt = f"""
{self.system_prompt}

==================================================
CONVERSATION HISTORY
==================================================

{history_text}

==================================================
RETRIEVED DOCUMENT CONTEXT
==================================================

{context_text}

==================================================
CURRENT USER QUESTION
==================================================

{question}

==================================================
INSTRUCTIONS
==================================================

Answer the current user question using the retrieved document
context and the conversation history.

Do not invent information that is not supported by the documents.

If the documents do not contain enough information, clearly say so.

Answer directly without discussing the internal retrieval system.

ASSISTANT:
"""

        return prompt.strip()

    def _build_history(
        self,
        conversation_history: list
    ) -> str:

        if not conversation_history:
            return "No previous conversation."

        history_parts = []

        for message in conversation_history:

            role = message.get("role", "user")
            content = message.get("content", "")

            if not content:
                continue

            if role == "user":
                label = "USER"

            elif role == "assistant":
                label = "ASSISTANT"

            else:
                label = role.upper()

            history_parts.append(
                f"{label}: {content}"
            )

        if not history_parts:
            return "No previous conversation."

        return "\n\n".join(history_parts)

    def _build_document_context(
        self,
        document_context: list
    ) -> str:

        if not document_context:
            return "No relevant document context was retrieved."

        context_parts = []

        for index, document in enumerate(
            document_context,
            start=1
        ):

            filename = document.get(
                "filename",
                "Unknown document"
            )

            page_number = document.get(
                "page_number",
                "Unknown"
            )

            paragraph_number = document.get(
                "paragraph_number",
                "Unknown"
            )

            text = document.get(
                "text",
                ""
            )

            if not text:
                continue

            context_parts.append(
                f"""
SOURCE {index}

Document:
{filename}

Page:
{page_number}

Paragraph:
{paragraph_number}

Content:
{text}
""".strip()
            )

        if not context_parts:
            return "No relevant document context was retrieved."

        return "\n\n------------------------------\n\n".join(
            context_parts
        )