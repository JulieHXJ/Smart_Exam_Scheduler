
from fastapi.testclient import TestClient

from app.main import app
from app.data.demo_plan import room_unavailability


client = TestClient(app)


def test_room_unavailability_triggers_conflict():
    room_unavailability.clear()

    try:
        # Initially the schedule is valid
        response = client.post(
            "/api/planning-cycles/plan_ws_2026/validate"
        )

        print("Status:", response.status_code)
        print("Response:", response.json())

        assert response.status_code == 200
        assert response.json()["valid"] is True

        # Block room M1.01 during Database Systems
        response = client.put(
            "/api/rooms/room_m101/unavailability",
            json={
                "id": "blocked_test",
                "room_id": "room_m101",
                "start": "2027-01-21T08:00:00",
                "end": "2027-01-21T12:00:00",
                "reason": "Test maintenance",
            },
        )

        assert response.status_code == 200

        # Validate again
        response = client.post(
            "/api/planning-cycles/plan_ws_2026/validate"
        )

        assert response.status_code == 200

        result = response.json()

        assert result["valid"] is False

        assert any(
            issue["type"] == "ROOM_UNAVAILABLE"
            for issue in result["issues"]
        )

    finally:
        room_unavailability.clear()
