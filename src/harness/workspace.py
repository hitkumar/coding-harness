# Live Repo Context

from dataclasses import dataclass
from pathlib import Path
import subprocess

DOC_NAMES = ("AGENTS.md", "README.md", "pyproject.toml", "package.json")
PROJECT_DOC_LIMIT = 1200

@dataclass
class WorkspaceContext:
    cwd: Path
    repo_root: Path
    branch: str
    default_branch: str
    status: str
    recent_commits: list[str]
    project_docs: dict[str, str]

    @classmethod
    def build(cls, cwd):
        cwd = Path(cwd).resolve()
        if not cwd.exists():
            raise FileNotFoundError(f"cwd does not exist: {cwd}")
        if not cwd.is_dir():
            raise NotADirectoryError(f"cwd is not a directory: {cwd}")

        def git(args, fallback=""):
            try:
                res = subprocess.run(
                    ["git", *args],
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=5,
                )
                return res.stdout.strip() or fallback
            except Exception:
                return fallback

        repo_root_text = git(["rev-parse", "--show-toplevel"])
        repo_root = Path(repo_root_text).resolve() if repo_root_text else cwd

        default_branch = git(
            ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
            "origin/main",
        ).removeprefix("origin/")

        project_docs = {}
        for base in (repo_root, cwd):
            for name in DOC_NAMES:
                path = base / name
                if not path.is_file():
                    continue
                key = str(path.relative_to(repo_root))
                if key in project_docs:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                project_docs[key] = text[:PROJECT_DOC_LIMIT]

        return cls(
            cwd=cwd,
            repo_root=repo_root,
            branch=git(["branch", "--show-current"], "-") or "-",
            default_branch=default_branch or "main",
            status=git(["status", "--short"], "clean") or "clean",
            recent_commits=[
                line
                for line in git(["log", "--oneline", "-5"]).splitlines()
                if line
            ],
            project_docs=project_docs,
        )

    def text(self):
        commits = "\n".join(f"- {line}" for line in self.recent_commits) or "- none"
        docs = "\n".join(
            f"- {path}\n{snippet}" for path, snippet in self.project_docs.items()
        ) or "- none"
        return "\n".join(
            [
                "Workspace:",
                f"- cwd: {self.cwd}",
                f"- repo_root: {self.repo_root}",
                f"- branch: {self.branch}",
                f"- default_branch: {self.default_branch}",
                "- status:",
                self.status,
                "- recent_commits:",
                commits,
                "- project_docs:",
                docs,
            ]
        )
