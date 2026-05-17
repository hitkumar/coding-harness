import json
import os
import urllib.request

import pytest

from harness import VLLMClient
from harness.parsing import parse_model_response


RUN_VLLM_TESTS = os.getenv("RUN_VLLM_TESTS") == "1"
VLLM_HOST = os.getenv("VLLM_HOST", "http://127.0.0.1:8000").rstrip("/")
VLLM_MODEL = os.getenv("VLLM_MODEL")

pytestmark = pytest.mark.skipif(
    not RUN_VLLM_TESTS,
    reason="set RUN_VLLM_TESTS=1 to run vLLM integration tests",
)


def served_model_id() -> str:
    request = urllib.request.Request(VLLM_HOST + "/v1/models", method="GET")

    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    model_ids = {item["id"] for item in data["data"]}
    assert model_ids
    if VLLM_MODEL:
        assert VLLM_MODEL in model_ids
        return VLLM_MODEL
    return sorted(model_ids)[0]


def test_vllm_models_endpoint_exposes_a_model():
    assert served_model_id()


def test_vllm_client_can_return_final_protocol_response():
    client = VLLMClient(model=served_model_id(), host=VLLM_HOST, temperature=0, timeout=60)

    text = client.complete(
        "Reply exactly with this text and nothing else: <final>ok-vllm</final>",
        max_new_tokens=32,
    )

    kind, payload = parse_model_response(text)
    assert kind == "final"
    assert payload == "ok-vllm"


def test_vllm_client_can_return_json_tool_protocol_response():
    client = VLLMClient(model=served_model_id(), host=VLLM_HOST, temperature=0, timeout=60)

    text = client.complete(
        'Reply exactly with this text and nothing else: <tool>{"name":"list_files","args":{"path":"."}}</tool>',
        max_new_tokens=64,
    )

    kind, payload = parse_model_response(text)
    assert kind == "tool"
    assert payload == {"name": "list_files", "args": {"path": "."}}
