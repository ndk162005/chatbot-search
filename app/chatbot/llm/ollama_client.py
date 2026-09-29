"""
Ollama LLM client for generating responses.
"""

from typing import Any
import json
import urllib.request

from app.chatbot.config import OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_TIMEOUT


class OllamaClient:
    """
    Client for interacting with the Ollama local API service.
    """

    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout: float = OLLAMA_TIMEOUT,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """
        Generate text response for a given prompt.
        """
        if not prompt or not prompt.strip():
            return ""

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "24h",
            "options": {
                "num_ctx": 4096,
                "temperature": 0.2
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:

                result = json.loads(response.read().decode("utf-8"))
                res_text = result.get("response", "")
                if res_text and res_text.strip():
                    return res_text.strip()
        except Exception as e:
            print(f"[Ollama Client Error]: {e}")

        # Smart fallback when local Ollama service is offline/unreachable
        if "RETRIEVED DOCUMENT CONTEXT" in prompt:
            context_section = prompt.split("RETRIEVED DOCUMENT CONTEXT")[-1].split("CURRENT USER QUESTION")[0]
            if "No relevant document context" in context_section or not context_section.strip():
                return "I couldn't find enough information in your uploaded documents to answer that question. Please upload a PDF document containing the relevant details."

            # Extract content lines from context
            lines = [
                l.strip()
                for l in context_section.split("\n")
                if l.strip()
                and not l.startswith("SOURCE")
                and not l.startswith("Document:")
                and not l.startswith("Page:")
                and not l.startswith("Paragraph:")
                and not l.startswith("Content:")
                and not l.startswith("---")
            ]
            extracted = " ".join(lines[:4])
            if extracted:
                return f"Based on your uploaded document:\n\n{extracted}"

        return "I'm ready to answer questions about your documents! Please upload a PDF file using the left sidebar to get started."
