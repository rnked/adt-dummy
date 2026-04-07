"""Minimal AI Gateway helpers."""

import requests

from adt_dummy.core import env
from adt_dummy.core.errors import AppError

DEFAULT_MODEL = "base"
DEFAULT_BASE_URL = "https://gateway-ai.raiffeisen.ru"
CHAT_COMPLETIONS_ENDPOINT = "/v1/chat/completions"


def chat_completion_text(messages, model=DEFAULT_MODEL, temperature=None, timeout=30):
    base_url = env.get_env("ADT_DUMMY_LLM_BASE_URL", default=DEFAULT_BASE_URL).rstrip("/")
    api_key = env.get_env("ADT_DUMMY_LLM_API_KEY", required=True)
    payload = {
        "model": model,
        "messages": messages,
    }
    if temperature is not None:
        payload["temperature"] = temperature

    try:
        response = requests.post(
            f"{base_url}{CHAT_COMPLETIONS_ENDPOINT}",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise AppError(f"AI Gateway request failed: {exc}") from exc

    if response.status_code >= 400:
        details = response.text.strip()
        message = f"AI Gateway returned HTTP {response.status_code}"
        if details:
            message += f": {details}"
        raise AppError(message)

    try:
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise AppError("AI Gateway returned an unexpected response format") from exc

    if not isinstance(content, str):
        raise AppError("AI Gateway returned an unexpected message content format")

    return content
