from pathlib import Path

from ghost_talent import github_auth


def test_connected_token_is_saved_outside_repository(tmp_path, monkeypatch):
    auth_dir = tmp_path / ".ghost-talent"
    auth_file = auth_dir / "github-auth.json"
    monkeypatch.setattr(github_auth, "AUTH_DIR", auth_dir)
    monkeypatch.setattr(github_auth, "AUTH_FILE", auth_file)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    github_auth.save_connected_token("gho_test_token")

    assert auth_file.exists()
    assert github_auth.load_connected_token() == "gho_test_token"
    assert github_auth.auth_mode() == "github_connected"


def test_environment_token_takes_precedence(tmp_path, monkeypatch):
    auth_dir = tmp_path / ".ghost-talent"
    auth_file = auth_dir / "github-auth.json"
    monkeypatch.setattr(github_auth, "AUTH_DIR", auth_dir)
    monkeypatch.setattr(github_auth, "AUTH_FILE", auth_file)
    monkeypatch.setenv("GITHUB_TOKEN", "env_token")

    github_auth.save_connected_token("saved_token")

    assert github_auth.load_connected_token() == "env_token"
    assert github_auth.auth_mode() == "environment_token"


def test_device_flow_client_id_is_public_configuration(monkeypatch):
    monkeypatch.delenv("GITHUB_OAUTH_CLIENT_ID", raising=False)
    monkeypatch.setenv("GHOST_TALENT_GITHUB_CLIENT_ID", "Iv1.example")
    assert github_auth.github_client_id() == "Iv1.example"
