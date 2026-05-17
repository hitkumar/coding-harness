import json
from pathlib import Path


class SessionStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def session_path(self, session_id: str) -> Path:
        return self.root / f"{session_id}.json"

    def save(self, session: dict) -> Path:
        path = self.session_path(session["id"])
        path.write_text(json.dumps(session, indent=2), encoding="utf-8")
        return path

    def load(self, session_id: str) -> dict:
        return json.loads(
            self.session_path(session_id).read_text(encoding="utf-8")
        )

    def latest(self) -> str | None:
        files = sorted(
            self.root.glob("*.json"),
            key=lambda path: path.stat().st_mtime,
        )
        return files[-1].stem if files else None
