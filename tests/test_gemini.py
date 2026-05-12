import json
from unittest.mock import MagicMock
import pytest

from services.gemini import GeminiClient
from models import Recommendation


def test_suggest_returns_recommendation_from_json(mocker):
    response = MagicMock()
    response.text = json.dumps({
        "title": "O Iluminado",
        "year": 1980,
        "justification": "Atmosfera sombria.",
    })

    fake_model = MagicMock()
    fake_model.generate_content.return_value = response

    mocker.patch("services.gemini.genai.GenerativeModel", return_value=fake_model)
    mocker.patch("services.gemini.genai.configure")

    client = GeminiClient(api_key="test", model_name="gemini-pro",
                          system_prompt="be a movie recommender")
    rec = client.suggest("quero suspense psicológico", exclude_titles=[])

    assert isinstance(rec, Recommendation)
    assert rec.title == "O Iluminado"
    assert rec.year == 1980
    assert rec.justification == "Atmosfera sombria."


from models import OffTopicRequest


def test_suggest_empty_title_raises_off_topic(mocker):
    response = MagicMock()
    response.text = json.dumps({
        "title": "",
        "year": None,
        "justification": "Meu objetivo é apenas recomendar filmes...",
    })
    fake_model = MagicMock()
    fake_model.generate_content.return_value = response
    mocker.patch("services.gemini.genai.GenerativeModel", return_value=fake_model)
    mocker.patch("services.gemini.genai.configure")

    client = GeminiClient(api_key="test", model_name="gemini-pro", system_prompt="x")
    with pytest.raises(OffTopicRequest):
        client.suggest("qual é a capital da França?", exclude_titles=[])
