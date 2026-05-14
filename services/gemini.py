from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Optional

from models import Recommendation, OffTopicRequest, AIInternalError


# 1. Substituímos o dicionário RESPONSE_SCHEMA por uma classe Pydantic
class MovieRecommendationSchema(BaseModel):
    title: str
    year: Optional[int]  # Isso substitui o "nullable": True
    justification: str


class GeminiClient:
    def __init__(self, api_key: str, model_name: str, system_prompt: str):
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name
        self._system_prompt = system_prompt

    def suggest(self, user_prompt: str, exclude_titles: list[str]) -> Recommendation:
        full_prompt = self._build_prompt(user_prompt, exclude_titles)
        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self._system_prompt,
                    response_mime_type="application/json",
                    # 2. Passamos a classe diretamente aqui!
                    response_schema=MovieRecommendationSchema,
                ),
            )
        except Exception as e:
            print(f"Erro na API: {repr(e)}")
            raise AIInternalError() from e

        # 3. O response.parsed já é um objeto validado! Não precisa de json.loads()
        try:
            dados_gerados = response.parsed

            if not dados_gerados or not dados_gerados.title:
                raise OffTopicRequest()

            return Recommendation(
                title=dados_gerados.title,
                year=dados_gerados.year,
                justification=dados_gerados.justification,
            )
        except Exception as e:
            print(f"Erro ao ler a resposta: {repr(e)}")
            raise AIInternalError() from e

    @staticmethod
    def _build_prompt(user_prompt: str, exclude_titles: list[str]) -> str:
        base = f"Pedido do usuário: {user_prompt}"
        if exclude_titles:
            excluded = ", ".join(exclude_titles[-20:])
            base += f"\nNÃO sugerir os seguintes filmes já recomendados: {excluded}"
        return base
