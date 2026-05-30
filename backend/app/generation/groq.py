from collections.abc import AsyncIterator

import httpx

from app.core.config import Settings
from app.generation.models import GenerationRequest, GenerationToken


class GroqLLMProvider:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def stream_chat(
        self, request: GenerationRequest
    ) -> AsyncIterator[GenerationToken]:
        if not self._settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is required for generation.")

        payload = {
            "model": request.model,
            "messages": [message.model_dump() for message in request.messages],
            "temperature": request.temperature,
            "stream": True,
        }
        headers = {"Authorization": f"Bearer {self._settings.groq_api_key}"}
        url = f"{self._settings.groq_base_url.rstrip('/')}/chat/completions"

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line.removeprefix("data: ").strip()
                    if data == "[DONE]":
                        break
                    token = _extract_stream_token(data)
                    if token:
                        yield GenerationToken(content=token)


def _extract_stream_token(raw_json: str) -> str:
    import json

    parsed = json.loads(raw_json)
    choices = parsed.get("choices", [])
    if not choices:
        return ""
    return choices[0].get("delta", {}).get("content", "") or ""
