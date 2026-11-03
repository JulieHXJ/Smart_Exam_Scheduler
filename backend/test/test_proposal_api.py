import pytest

from fastapi.testclient import TestClient
from app.main import app
from app.auth.core import get_current_user, require_admin


@pytest.fixture(autouse=True)
def authenticated_proposal_test():
    admin = {
        "email": "staff@example.org",
        "role": "admin",
    }

    app.dependency_overrides[get_current_user] = lambda: admin

    yield

    app.dependency_overrides.pop(get_current_user, None)





from app.data.demo_plan import (
    current_schedules,
    schedules,
    proposals,
    proposal_metadata,
    room_unavailability,
    data_revision,
)



client = TestClient(app)

CYCLE_ID = "plan_ws_2026"


def reset_demo_state():
    room_unavailability.clear()
    proposals.clear()
    proposal_metadata.clear()

    current_schedules[CYCLE_ID] = "schedule_v1"
    data_revision["value"] = 0

    # Remove previously created confirmed revisions.
    for schedule_id in list(schedules):
        if schedule_id != "schedule_v1":
            del schedules[schedule_id]


def block_room():
    return client.put(
        "/api/rooms/room_m101/unavailability",
        json={
            "id": "block_test",
            "room_id": "room_m101",
            "start": "2027-01-21T08:00:00",
            "end": "2027-01-21T12:00:00",
            "reason": "Maintenance",
        },
    )


def test_generate_and_confirm_proposal():
    reset_demo_state()

    try:
        # 1. Update room availability
        response = block_room()
        assert response.status_code == 200

        # 2. Current V1 should become invalid
        response = client.post(
            f"/api/planning-cycles/{CYCLE_ID}/validate"
        )

        assert response.status_code == 200
        assert response.json()["valid"] is False

        # 3. Generate proposal
        response = client.post(
            f"/api/planning-cycles/{CYCLE_ID}/proposals"
        )

        assert response.status_code == 200, response.text

        result = response.json()
        proposal = result["proposal"]
        proposal_id = proposal["id"]

        assert proposal["status"] == "proposal"
        assert proposal["version_number"] is None

        # Database Systems must no longer have
        # its invalid original assignment.
        assignments = {
            assignment["exam_id"]: assignment
            for assignment in proposal["assignments"]
        }

        assert (
            assignments["exam_db"]["room_ids"]
            != ["room_m101"]
            or assignments["exam_db"]["date"] != "2027-01-21"
            or assignments["exam_db"]["start_time"] != "09:00:00"
        )

        # 4. Confirm the proposal
        response = client.post(
            f"/api/proposals/{proposal_id}/confirm"
        )

        assert response.status_code == 200, response.text

        confirmed = response.json()["schedule"]

        assert confirmed["status"] == "confirmed"
        assert confirmed["version_number"] == 2

        # 5. Current schedule should now be V2
        response = client.get(
            f"/api/planning-cycles/{CYCLE_ID}/schedules/current"
        )

        assert response.status_code == 200
        assert response.json()["id"] == confirmed["id"]

        # 6. V1 must still exist
        assert "schedule_v1" in schedules
        assert schedules["schedule_v1"].version_number == 1

        # 7. Double confirmation must fail
        response = client.post(
            f"/api/proposals/{proposal_id}/confirm"
        )

        assert response.status_code == 404

    finally:
        reset_demo_state()


def test_reject_stale_proposal():
    reset_demo_state()

    try:
        # Generate a proposal based on the original data.
        response = client.post(
            f"/api/planning-cycles/{CYCLE_ID}/proposals"
        )

        assert response.status_code == 200, response.text
        proposal_id = response.json()["proposal"]["id"]

        # Change room availability afterwards.
        response = block_room()
        assert response.status_code == 200

        # The old proposal must not be confirmed.
        response = client.post(
            f"/api/proposals/{proposal_id}/confirm"
        )

        assert response.status_code == 409

        assert current_schedules[CYCLE_ID] == "schedule_v1"

    finally:
        reset_demo_state()



def test_tester_cannot_confirm_proposal():
    reset_demo_state()

    try:
        # Create a proposal using the admin test identity.
        response = client.post(
            f"/api/planning-cycles/{CYCLE_ID}/proposals"
        )
        assert response.status_code == 200

        proposal_id = response.json()["proposal"]["id"]

        # Simulate an authenticated tester.
        app.dependency_overrides[get_current_user] = lambda: {
            "email": "tester@example.org",
            "role": "tester",
        }

        response = client.post(
            f"/api/proposals/{proposal_id}/confirm"
        )

        assert response.status_code == 403

        # The confirmed baseline must remain unchanged.
        assert current_schedules[CYCLE_ID] == "schedule_v1"
        assert proposal_id in proposals

    finally:
        app.dependency_overrides.pop(get_current_user, None)
        reset_demo_state()
