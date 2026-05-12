import json

import google.generativeai as genai

from models import Recommendation, OffTopicRequest


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
        response = self._model.generate_content(
            full_prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": RESPONSE_SCHEMA,
            },
        )
        data = json.loads(response.text)
        if not data["title"]:
            raise OffTopicRequest()
        return Recommendation(
            title=data["title"],
            year=data.get("year"),
            justification=data["justification"],
        )

    @staticmethod
    def _build_prompt(user_prompt: str, exclude_titles: list[str]) -> str:
        base = f"Pedido do usuário: {user_prompt}"
        if exclude_titles:
            excluded = ", ".join(exclude_titles[-20:])
            base += f"\nNÃO sugerir os seguintes filmes já recomendados: {excluded}"
        return base
