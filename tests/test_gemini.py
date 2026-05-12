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


from google.api_core.exceptions import ResourceExhausted
from models import AIQuotaExceeded


def test_suggest_quota_exceeded_raises_ai_quota_exceeded(mocker):
    fake_model = MagicMock()
    fake_model.generate_content.side_effect = ResourceExhausted("429 quota")
    mocker.patch("services.gemini.genai.GenerativeModel", return_value=fake_model)
    mocker.patch("services.gemini.genai.configure")

    client = GeminiClient(api_key="test", model_name="gemini-pro", system_prompt="x")
    with pytest.raises(AIQuotaExceeded):
        client.suggest("teste", exclude_titles=[])


from models import AIInternalError


def test_suggest_invalid_json_raises_ai_internal_error(mocker):
    response = MagicMock()
    response.text = "isto não é JSON {{ "
    fake_model = MagicMock()
    fake_model.generate_content.return_value = response
    mocker.patch("services.gemini.genai.GenerativeModel", return_value=fake_model)
    mocker.patch("services.gemini.genai.configure")

    client = GeminiClient(api_key="test", model_name="gemini-pro", system_prompt="x")
    with pytest.raises(AIInternalError):
        client.suggest("teste", exclude_titles=[])


def test_suggest_missing_required_field_raises_ai_internal_error(mocker):
    response = MagicMock()
    response.text = json.dumps({"year": 1980})  # falta title e justification
    fake_model = MagicMock()
    fake_model.generate_content.return_value = response
    mocker.patch("services.gemini.genai.GenerativeModel", return_value=fake_model)
    mocker.patch("services.gemini.genai.configure")

    client = GeminiClient(api_key="test", model_name="gemini-pro", system_prompt="x")
    with pytest.raises(AIInternalError):
        client.suggest("teste", exclude_titles=[])


def test_suggest_generic_sdk_exception_raises_ai_internal_error(mocker):
    fake_model = MagicMock()
    fake_model.generate_content.side_effect = RuntimeError("falha genérica")
    mocker.patch("services.gemini.genai.GenerativeModel", return_value=fake_model)
    mocker.patch("services.gemini.genai.configure")

    client = GeminiClient(api_key="test", model_name="gemini-pro", system_prompt="x")
    with pytest.raises(AIInternalError):
        client.suggest("teste", exclude_titles=[])
