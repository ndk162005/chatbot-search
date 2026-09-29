# PDF AI Assistant

A document-intelligence application that allows users to upload PDF documents,
ask questions about them, receive an AI-generated answer using Ollama, and
view independently ranked semantic-search results.

---

## Architecture

The application contains two independent processing systems.

### 1. Chatbot

The chatbot has its own:

- document processing
- embeddings
- database
- retrieval
- context builder
- Ollama LLM
- answer generator

Its purpose is to generate a direct answer to the user's question.

### 2. Semantic Search

The semantic-search system has its own:

- PDF processing
- paragraph/chunking
- embeddings
- vector database
- semantic retrieval
- ranking

Its purpose is to return the most semantically similar document passages.

The two systems use separate processing pipelines and databases.

---

## Application Flow

```text
                         PDF
                          |
              +-----------+-----------+
              |                       |
              v                       v
          CHATBOT               SEMANTIC SEARCH
              |                       |
        Chatbot DB              Search DB
              |                       |
              v                       v
           Retrieval              Embedding
              |                       |
              v                       v
          Context                Vector Search
              |                       |
              v                       v
            Ollama                 Ranking
              |                       |
              v                       v
         AI ANSWER               RESULTS
              |                       |
              +-----------+-----------+
                          |
                          v
                       FRONTEND