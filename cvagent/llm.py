"""LLM provider wrapper — supports Ollama (local) and Anthropic API."""

from __future__ import annotations

import os

import anthropic
import ollama

DEFAULT_MODEL = "mistral"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_PROVIDER = "ollama"


def _generate_ollama(prompt: str, model: str) -> str:
    response = ollama.generate(model=model, prompt=prompt)
    return response["response"].strip()


def _generate_anthropic(prompt: str, model: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def generate(prompt: str, model: str = DEFAULT_MODEL, provider: str = DEFAULT_PROVIDER) -> str:
    """Send a prompt to the configured LLM provider and return the response text.

    provider='ollama': communicates with local Ollama daemon (localhost:11434).
    provider='anthropic': calls Anthropic API; requires ANTHROPIC_API_KEY env var.
    """
    if provider == "ollama":
        return _generate_ollama(prompt, model)
    if provider == "anthropic":
        return _generate_anthropic(prompt, model)
    raise ValueError(f"Unknown provider: {provider!r}. Choose 'ollama' or 'anthropic'.")
