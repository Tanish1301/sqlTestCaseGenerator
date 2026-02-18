import os
from typing import Optional

import requests


class OllamaService:
    def __init__(self):
        self.default_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.default_endpoint = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.default_timeout_seconds = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> str:
        payload = {"model": model or self.default_model, "prompt": prompt, "stream": False}
        response = requests.post(
            endpoint or self.default_endpoint,
            json=payload,
            timeout=timeout_seconds or self.default_timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        return str(body.get("response", ""))
