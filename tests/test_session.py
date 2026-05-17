import os
import time

from harness.session import SessionStore


def test_save_and_load_session(tmp_path):
    store = SessionStore(tmp_path / "sessions")
    session = {
        "id": "session-1",
        "history": [{"role": "user", "content": "hello"}],
        "memory": {"task": "demo", "files": [], "notes": []},
    }

    path = store.save(session)

    assert path == tmp_path / "sessions" / "session-1.json"
    assert store.load("session-1") == session


def test_latest_returns_most_recent_session(tmp_path):
    store = SessionStore(tmp_path / "sessions")
    store.save({"id": "older"})
    older_path = store.session_path("older")

    time.sleep(0.01)
    store.save({"id": "newer"})
    newer_path = store.session_path("newer")

    assert os.path.getmtime(newer_path) > os.path.getmtime(older_path)
    assert store.latest() == "newer"
