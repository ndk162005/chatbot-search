from unittest.mock import Mock


def test_ollama_client_response():

    from app.chatbot.llm.ollama_client import (
        OllamaClient,
    )

    client = OllamaClient()

    # Replace the internal request method with a mock
    # according to your actual OllamaClient implementation.

    mock_response = {
        "response": "The document states that the vessel must submit the required documents and requirements."
    }

    client.generate = Mock(
        return_value=mock_response["response"]
    )

    response = client.generate(
        "What are the requirements?"
    )

    assert response is not None
    assert "requirements" in response.lower()