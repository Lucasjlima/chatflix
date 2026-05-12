import json

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

from models import Recommendation, OffTopicRequest, AIQuotaExceeded, AIInternalError


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "year": {"type": ["integer", "null"]},
        "justification": {"type": "string"},
    },
    "required": ["title", "justification"],
}


class GeminiClient:
    def __init__(self, api_key: str, model_name: str, system_prompt: str):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
        )

    def suggest(self, user_prompt: str, exclude_titles: list[str]) -> Recommendation:
        full_prompt = self._build_prompt(user_prompt, exclude_titles)
        try:
            response = self._model.generate_content(
                full_prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": RESPONSE_SCHEMA,
                },
            )
        except ResourceExhausted as e:
            raise AIQuotaExceeded() from e
        except Exception as e:
            raise AIInternalError() from e

        try:
            data = json.loads(response.text)
            title = data["title"]
            justification = data["justification"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise AIInternalError() from e

        if not title:
            raise OffTopicRequest()
        return Recommendation(
            title=title,
            year=data.get("year"),
            justification=justification,
        )

    @staticmethod
    def _build_prompt(user_prompt: str, exclude_titles: list[str]) -> str:
        base = f"Pedido do usuário: {user_prompt}"
        if exclude_titles:
            excluded = ", ".join(exclude_titles[-20:])
            base += f"\nNÃO sugerir os seguintes filmes já recomendados: {excluded}"
        return base
