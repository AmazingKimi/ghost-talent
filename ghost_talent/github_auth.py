from __future__ import annotations

import json
import os
import secrets
from pathlib import Path
from typing import Any

import httpx

DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
API_ROOT = "https://api.github.com"
AUTH_DIR = Path.home() / ".ghost-talent"
AUTH_FILE = AUTH_DIR / "github-auth.json"
_FLOWS: dict[str, dict[str, Any]] = {}


def github_client_id() -> str | None:
    return os.getenv("GHOST_TALENT_GITHUB_CLIENT_ID") or os.getenv("GITHUB_OAUTH_CLIENT_ID")


def load_connected_token() -> str | None:
    env_token = os.getenv("GITHUB_TOKEN")
    if env_token:
        return env_token.strip() or None
    try:
        payload = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        token = str(payload.get("access_token") or "").strip()
        return token or None
    except (OSError, json.JSONDecodeError):
        return None


def auth_mode() -> str:
    if os.getenv("GITHUB_TOKEN"):
        return "environment_token"
    if load_connected_token():
        return "github_connected"
    return "public_limited"


def save_connected_token(token: str, token_type: str = "bearer", scope: str = "") -> None:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"access_token": token, "token_type": token_type, "scope": scope}
    AUTH_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    try:
        AUTH_FILE.chmod(0o600)
    except OSError:
        pass


def disconnect_github() -> bool:
    if os.getenv("GITHUB_TOKEN"):
        return False
    try:
        AUTH_FILE.unlink()
        return True
    except FileNotFoundError:
        return True


async def start_device_flow() -> dict[str, Any]:
    client_id = github_client_id()
    if not client_id:
        raise RuntimeError("GitHub OAuth client ID is not configured for this build.")
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            DEVICE_CODE_URL,
            data={"client_id": client_id},
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
    flow_id = secrets.token_urlsafe(18)
    _FLOWS[flow_id] = {
        "device_code": data["device_code"],
        "interval": int(data.get("interval", 5)),
        "expires_in": int(data.get("expires_in", 900)),
        "client_id": client_id,
    }
    return {
        "flow_id": flow_id,
        "user_code": data["user_code"],
        "verification_uri": data.get("verification_uri", "https://github.com/login/device"),
        "expires_in": int(data.get("expires_in", 900)),
        "interval": int(data.get("interval", 5)),
    }


async def poll_device_flow(flow_id: str) -> dict[str, Any]:
    flow = _FLOWS.get(flow_id)
    if not flow:
        return {"status": "expired"}
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            ACCESS_TOKEN_URL,
            data={
                "client_id": flow["client_id"],
                "device_code": flow["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
    if data.get("access_token"):
        save_connected_token(data["access_token"], data.get("token_type", "bearer"), data.get("scope", ""))
        _FLOWS.pop(flow_id, None)
        return {"status": "connected"}
    error = data.get("error")
    if error == "authorization_pending":
        return {"status": "pending", "interval": flow["interval"]}
    if error == "slow_down":
        flow["interval"] = int(flow["interval"]) + 5
        return {"status": "pending", "interval": flow["interval"]}
    _FLOWS.pop(flow_id, None)
    return {"status": "failed", "error": error or "authorization_failed"}


async def github_auth_status() -> dict[str, Any]:
    token = load_connected_token()
    result: dict[str, Any] = {
        "connected": bool(token),
        "mode": auth_mode(),
        "client_configured": bool(github_client_id()),
        "limit": 60,
        "remaining": None,
        "reset": None,
        "login": None,
    }
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ghost-talent/0.3.3"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
            rate = await client.get(f"{API_ROOT}/rate_limit")
            rate.raise_for_status()
            core = ((rate.json().get("resources") or {}).get("core") or {})
            result.update({"limit": core.get("limit"), "remaining": core.get("remaining"), "reset": core.get("reset")})
            if token:
                user = await client.get(f"{API_ROOT}/user")
                if user.status_code == 200:
                    result["login"] = user.json().get("login")
    except Exception as exc:
        result["status_error"] = str(exc)
    return result
