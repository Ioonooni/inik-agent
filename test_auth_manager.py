from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from auth_manager import (
    build_username_from_email,
    create_blank_memory_for_user,
    login_with_email,
    normalize_email,
    normalize_username,
    sign_up_with_email,
    upsert_app_user,
)


class FakeTable:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.inserted = []
        self.updated = []
        self.filters = {}

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def insert(self, payload):
        self.inserted.append(payload)
        return self

    def update(self, payload):
        self.updated.append(payload)
        return self

    def execute(self):
        if self.inserted:
            return SimpleNamespace(data=[self.inserted[-1]])
        if self.updated and self.rows:
            return SimpleNamespace(data=[self.rows[0]])
        key, value = next(iter(self.filters.items()), (None, None))
        if key:
            return SimpleNamespace(data=[r for r in self.rows if r.get(key) == value])
        return SimpleNamespace(data=self.rows)


class FakeAuth:
    def __init__(self):
        self.signup_calls = []
        self.login_calls = []

    def sign_up(self, payload):
        self.signup_calls.append(payload)
        return SimpleNamespace(
            user=SimpleNamespace(id="auth_user_1"),
            session=SimpleNamespace(access_token="signup_token"),
        )

    def sign_in_with_password(self, payload):
        self.login_calls.append(payload)
        return SimpleNamespace(
            user=SimpleNamespace(id="auth_user_1"),
            session=SimpleNamespace(access_token="login_token"),
        )


class FakeClient:
    def __init__(self):
        self.auth = FakeAuth()
        self.users = FakeTable([])
        self.memory = FakeTable([])

    def table(self, name):
        if name == "i_nik_users":
            return self.users
        if name == "i_nik_memory":
            return self.memory
        raise AssertionError(f"unexpected table: {name}")


def test_normalize_username_and_email():
    assert normalize_username("  AiOon  ") == "aioon"
    assert normalize_email("  TEST@Example.COM ") == "test@example.com"
    assert build_username_from_email("User.Name@example.com") == "user.name"

    with pytest.raises(ValueError):
        normalize_username("x")

    with pytest.raises(ValueError):
        normalize_email("not-an-email")


def test_create_blank_memory_for_user_inserts_when_missing():
    client = FakeClient()

    with patch("auth_manager.get_supabase_client", return_value=client):
        ok = create_blank_memory_for_user("u1")

    assert ok is True
    assert client.memory.inserted
    assert client.memory.inserted[-1]["user_id"] == "u1"
    assert "user_profile" in client.memory.inserted[-1]
    assert "relationship_state" in client.memory.inserted[-1]


def test_upsert_app_user_inserts_new_user():
    client = FakeClient()

    with patch("auth_manager.get_supabase_client", return_value=client):
        user = upsert_app_user("u1", "ไออุ่น")

    assert user["id"] == "u1"
    assert user["username"] == "ไออุ่น"
    assert client.users.inserted


def test_sign_up_with_email_creates_auth_user_and_blank_memory():
    client = FakeClient()

    with patch("auth_manager.get_supabase_client", return_value=client):
        result = sign_up_with_email("Test@Example.com", "123456")

    assert result["id"] == "auth_user_1"
    assert result["email"] == "test@example.com"
    assert result["username"] == "test"
    assert client.auth.signup_calls
    assert client.users.inserted
    assert client.memory.inserted


def test_login_with_email_creates_session_and_blank_memory():
    client = FakeClient()

    with patch("auth_manager.get_supabase_client", return_value=client):
        result = login_with_email("Test@Example.com", "123456")

    assert result["id"] == "auth_user_1"
    assert result["email"] == "test@example.com"
    assert result["username"] == "test"
    assert client.auth.login_calls
    assert client.users.inserted
    assert client.memory.inserted


def test_auth_password_validation():
    with pytest.raises(ValueError):
        sign_up_with_email("test@example.com", "12345")

    with pytest.raises(ValueError):
        login_with_email("test@example.com", "")
