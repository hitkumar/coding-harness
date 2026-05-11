from __future__ import annotations

import json
import urllib.error

import pytest

from harness import VLLMClient


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self):
        return self.body

    def close(self):
        pass


def test_complete_calls_vllm_chat_completions(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            b'{"choices":[{"message":{"content":"hello from qwen"}}]}'
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = VLLMClient(
        model="Qwen/Qwen2.5-Coder-7B-Instruct",
        host="http://localhost:8000",
        api_key="test-token",
    )

    result = client.complete("write a function", max_new_tokens=64)

    assert result == "hello from qwen"
    assert captured["url"] == "http://localhost:8000/v1/chat/completions"
    assert captured["timeout"] == 300
    assert captured["headers"]["Authorization"] == "Bearer test-token"
    assert captured["body"] == {
        "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "messages": [{"role": "user", "content": "write a function"}],
        "max_tokens": 64,
        "temperature": 0.6,
        "top_p": 0.95,
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": False},
    }


def test_complete_raises_on_http_error(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url,
            500,
            "server error",
            hdrs=None,
            fp=FakeResponse(b'{"error":"boom"}'),
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = VLLMClient(model="qwen")

    with pytest.raises(RuntimeError, match="HTTP 500"):
        client.complete("hello", max_new_tokens=32)
