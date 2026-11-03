import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import core

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setenv("AUTH_SECRET", "x" * 64)
    monkeypatch.setenv("AUTH_SECURE_COOKIE", "false")
    monkeypatch.setenv("ALLOWED_ADMIN_EMAIL", "staff@example.org")
    monkeypatch.setenv("ALLOWED_TEST_EMAIL", "tester@example.org")
    core._challenges.clear()
    core._sessions.clear()
    core._requests.clear()
    codes = []
    monkeypatch.setattr(core, "send_code", lambda email, code: codes.append((email, code)))
    yield codes

def test_login_and_reuse_rejected(setup):
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/auth/request-code", json={"email":"staff@example.org"}).status_code == 200
    code = setup[0][1]
    result = client.post("/api/auth/verify-code",json={"email":"staff@example.org","code":code})
    assert result.status_code == 200
    assert client.get("/api/auth/me").json()["role"] == "admin"
    assert client.post("/api/auth/verify-code",json={"email":"staff@example.org","code":code}).status_code == 401
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").status_code == 401

def test_unknown_email_is_generic(setup):
    assert client.post("/api/auth/request-code",json={"email":"unknown@example.org"}).status_code == 200
    assert setup == []

def test_bad_code_exhausts_attempts(setup):
    client.post("/api/auth/request-code",json={"email":"staff@example.org"})
    for _ in range(5):
        assert client.post("/api/auth/verify-code",json={"email":"staff@example.org","code":"AAAAAA"}).status_code == 401
    assert client.post("/api/auth/verify-code",json={"email":"staff@example.org","code":setup[0][1]}).status_code == 401

def test_protected_api(setup):
    assert client.post("/api/planning-cycles/plan_ws_2026/proposals").status_code == 401
