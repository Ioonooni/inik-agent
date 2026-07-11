import pytest
from fastapi.testclient import TestClient

import inik_api
from inik_api import app

client = TestClient(app)

USER_ID = "v3-routing-test-user"

cases = [
    (
        "emotional",
        "วันนี้เหนื่อยมาก อยากระบาย",
        "inik",
    ),
    (
        "strategic",
        "ฉันมีเงินเก็บ 5 แสน ควรลงทุนหรือเรียนต่อ",
        "rick_royce",
    ),
    (
        "mixed",
        "ฉันเครียดมากและกำลังคิดจะลาออกไปทำ startup",
        "hybrid",
    ),
]


@pytest.mark.parametrize("name,message,expected", cases)
def test_api_routing(monkeypatch, name, message, expected):
    monkeypatch.setattr(inik_api, "model", None)
    monkeypatch.setattr(inik_api, "API_KEY", None)

    response = client.post(
        "/api/chat",
        json={
            "user_id": USER_ID,
            "username": "traveler",
            "message": message,
            "agent_mode": "auto",
        },
    )

    assert response.status_code == 200, f"{name}: {response.text}"

    data = response.json()

    actual = data["agent_mode"]

    assert actual == expected, (
        f"{name}: expected {expected}, got {actual}"
    )
