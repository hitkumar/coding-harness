import json
from typing import Any


def parse_model_response(raw: str) -> tuple[str, dict[str, Any] | str]:
    raw = str(raw)
    if "<tool>" in raw and ("<final>" not in raw or raw.find("<tool>") < raw.find("<final>")):
        body = extract_tag(raw, "tool")
        try:
            payload = json.loads(body)
        except Exception:
            return "retry", retry_notice("model returned malformed tool JSON")
        if not isinstance(payload, dict):
            return "retry", retry_notice("tool payload must be a JSON object")
        if not str(payload.get("name", "")).strip():
            return "retry", retry_notice("tool payload is missing a tool name")
        args = payload.get("args", {})
        if args is None:
            payload["args"] = {}
        elif not isinstance(args, dict):
            return "retry", retry_notice()
        return "tool", payload

    if "<tool" in raw and ("<final>" not in raw or raw.find("<tool") < raw.find("<final>")):
        return "retry", retry_notice("tool calls must use <tool>{json}</tool>")

    if "<final>" in raw:
        final = extract_tag(raw, "final").strip()
        if final:
            return "final", final
        return "retry", retry_notice("model returned an empty <final> answer")

    raw = raw.strip()
    if raw:
        return "final", raw
    return "retry", retry_notice("model returned an empty response")


def retry_notice(problem: str | None = None) -> str:
    prefix = "Runtime notice"
    if problem:
        prefix += f": {problem}"
    else:
        prefix += ": model returned malformed tool output"
    return (
        f"{prefix}. Reply with a valid <tool> call or a non-empty <final> answer. "
        'Tool calls must use <tool>{"name":"tool_name","args":{...}}</tool>.'
    )


def extract_tag(text: str, tag: str) -> str:
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start = text.find(start_tag)
    if start == -1:
        return text
    start += len(start_tag)
    end = text.find(end_tag, start)
    if end == -1:
        return text[start:].strip()
    return text[start:end].strip()
