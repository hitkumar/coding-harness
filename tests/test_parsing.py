from harness.parsing import parse_model_response


def test_parse_json_tool_call():
    kind, payload = parse_model_response(
        '<tool>{"name":"read_file","args":{"path":"README.md","start":1}}</tool>'
    )

    assert kind == "tool"
    assert payload == {
        "name": "read_file",
        "args": {"path": "README.md", "start": 1},
    }


def test_parse_final_answer():
    kind, payload = parse_model_response("<final>Done.</final>")

    assert kind == "final"
    assert payload == "Done."


def test_malformed_tool_json_returns_retry():
    kind, payload = parse_model_response('<tool>{"name":"read_file"</tool>')

    assert kind == "retry"
    assert "malformed tool JSON" in payload


def test_xml_style_tool_call_returns_retry():
    kind, payload = parse_model_response(
        '<tool name="write_file" path="hello.py"><content>print("hi")\n</content></tool>'
    )

    assert kind == "retry"
    assert "must use <tool>{json}</tool>" in payload


def test_parse_json_tool_with_multiline_content():
    kind, payload = parse_model_response(
        '<tool>{"name":"write_file","args":{"path":"hello.py","content":"print(\\"hi\\")\\n"}}</tool>'
    )

    assert kind == "tool"
    assert payload == {
        "name": "write_file",
        "args": {"path": "hello.py", "content": 'print("hi")\n'},
    }
