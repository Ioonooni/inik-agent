from fastapi.testclient import TestClient
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

for name, message, expected in cases:
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

print("api routing ok")
