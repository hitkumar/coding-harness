"""Minimal client for vLLM's OpenAI-compatible HTTP server."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


class VLLMClient:
    def __init__(
        self,
        model: str,
        host: str = "http://127.0.0.1:8000",
        temperature: float = 0.6,
        top_p: float = 0.95,
        top_k: int = 20,
        timeout: int = 300,
        api_key: str | None = None,
    ):
        self.model = model
        self.host = host.rstrip("/")
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.timeout = timeout
        self.api_key = api_key

    def complete(self, prompt: str, max_new_tokens: int) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_new_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(
            self.host + "/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"vLLM request failed with HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not reach vLLM server at {self.host}."
            ) from exc

        if data.get("error"):
            raise RuntimeError(f"vLLM error: {data['error']}")
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected vLLM response: {data}") from exc
