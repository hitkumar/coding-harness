from pathlib import Path

from harness.workspace import WorkspaceContext


def test_build_falls_back_outside_git(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text("demo project\n", encoding="utf-8")

    def fake_run(*args, **kwargs):
        raise FileNotFoundError("git unavailable")

    monkeypatch.setattr("subprocess.run", fake_run)

    workspace = WorkspaceContext.build(tmp_path)

    assert workspace.cwd == tmp_path.resolve()
    assert workspace.repo_root == tmp_path.resolve()
    assert workspace.branch == "-"
    assert workspace.default_branch == "main"
    assert workspace.status == "clean"
    assert workspace.recent_commits == []
    assert workspace.project_docs == {"README.md": "demo project\n"}


def test_text_renders_workspace_snapshot(tmp_path):
    workspace = WorkspaceContext(
        cwd=tmp_path / "src",
        repo_root=tmp_path,
        branch="feature/demo",
        default_branch="main",
        status=" M README.md",
        recent_commits=["abc123 first commit"],
        project_docs={"README.md": "hello\n"},
    )

    text = workspace.text()

    assert text.startswith("Workspace:\n")
    assert f"- cwd: {tmp_path / 'src'}" in text
    assert f"- repo_root: {tmp_path}" in text
    assert "- branch: feature/demo" in text
    assert "- abc123 first commit" in text
    assert "- README.md\nhello\n" in text
