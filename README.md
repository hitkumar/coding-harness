# coding-harness

Minimal coding-agent harness backed by local models.

## vLLM client

For a single-GPU coding-agent setup, prefer the FP8 checkpoint and skip the
vision encoder:

```bash
vllm serve Qwen/Qwen3.6-27B-FP8 \
  --host 127.0.0.1 \
  --port 8000 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --language-model-only \
  --enable-prefix-caching \
  --default-chat-template-kwargs '{"enable_thinking": false}' \
  --gpu-memory-utilization 0.70
```

If vLLM still reports insufficient free GPU memory at startup, lower
`--max-model-len` to `131072` first, then `65536` if needed.

Then call it from Python:

```python
from harness import VLLMClient

client = VLLMClient(model="Qwen/Qwen3.6-27B-FP8")
text = client.complete("Write a Python function that adds two numbers.")
print(text)
```

## Tests

Run the default test suite:

```bash
uv run pytest -q
```

Run vLLM integration tests against a local server:

```bash
RUN_VLLM_TESTS=1 uv run pytest -q tests/test_vllm_integration.py
```
