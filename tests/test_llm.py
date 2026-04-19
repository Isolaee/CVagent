"""Tests for the LLM wrapper — all external calls are mocked."""

import os

import pytest

from cvagent.llm import generate


# --- Ollama ---


def test_generate_ollama_returns_stripped_string(mocker):
    mock_response = {"response": "  This is the cover letter.  "}
    mocker.patch("cvagent.llm.ollama.generate", return_value=mock_response)
    result = generate("some prompt", model="mistral", provider="ollama")
    assert result == "This is the cover letter."


def test_generate_ollama_passes_model(mocker):
    mock_fn = mocker.patch("cvagent.llm.ollama.generate", return_value={"response": "ok"})
    generate("prompt", model="llama3", provider="ollama")
    mock_fn.assert_called_once_with(model="llama3", prompt="prompt")


def test_generate_uses_default_model_and_provider(mocker):
    mock_fn = mocker.patch("cvagent.llm.ollama.generate", return_value={"response": "ok"})
    generate("prompt")
    assert mock_fn.call_args.kwargs["model"] == "mistral"


# --- Anthropic ---


def test_generate_anthropic_returns_text(mocker, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_content = mocker.MagicMock()
    mock_content.text = "  Claude cover letter.  "
    mock_message = mocker.MagicMock()
    mock_message.content = [mock_content]
    mock_client = mocker.MagicMock()
    mock_client.messages.create.return_value = mock_message
    mocker.patch("cvagent.llm.anthropic.Anthropic", return_value=mock_client)

    result = generate("prompt", model="claude-sonnet-4-6", provider="anthropic")
    assert result == "Claude cover letter."


def test_generate_anthropic_passes_model(mocker, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_content = mocker.MagicMock()
    mock_content.text = "ok"
    mock_message = mocker.MagicMock()
    mock_message.content = [mock_content]
    mock_client = mocker.MagicMock()
    mock_client.messages.create.return_value = mock_message
    mocker.patch("cvagent.llm.anthropic.Anthropic", return_value=mock_client)

    generate("prompt", model="claude-opus-4-7", provider="anthropic")
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-opus-4-7"


def test_generate_anthropic_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        generate("prompt", provider="anthropic")


# --- Unknown provider ---


def test_generate_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        generate("prompt", provider="openai")
