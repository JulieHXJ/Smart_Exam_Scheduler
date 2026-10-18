
from datetime import date, time, datetime

from app.data.mock_data import exams, rooms
from app.models.schedule import (
    Schedule,
    ScheduleAssignment,
    ScheduleStatus,
)
from app.models.planning_cycle import PlanningCycle
from app.models.room import RoomUnavailability
from app.models.validator import ConflictType
from app.validator.schedule import validate_schedule


# helpers
def create_test_cycle():
    return PlanningCycle(
        id="plan_ws_2026",
        name="WS 2026/27",
        exam_period_start=date(2027, 1, 18),
        exam_period_end=date(2027, 2, 12),
    )


def create_test_schedule(assignments):
    return Schedule(
        id="schedule_test",
        name="Test Schedule",
        planning_cycle_id="plan_ws_2026",
        status=ScheduleStatus.PROPOSAL,
        assignments=assignments,
    )


def run_validation(
    assignments,
    expected_students=None,
    unavailable=None,
):
    schedule = create_test_schedule(assignments)

    return validate_schedule(
        schedule=schedule,
        exams=exams,
        rooms=rooms,
        cycle=create_test_cycle(),
        unavailable=unavailable or [],
        expected_students=expected_students or {},
    )


def has_conflict(issues, conflict_type):
    return any(
        issue.type == conflict_type
        for issue in issues
    )


# Test 1: Exam period
def test_exam_outside_period():

    assignment = ScheduleAssignment(
        exam_id="exam_db",
        date=date(2027, 3, 1),
        start_time=time(9, 0),
        room_ids=["room_m101"],
    )

    issues = run_validation([assignment])

    assert has_conflict(
        issues,
        ConflictType.OUTSIDE_EXAM_PERIOD,
    )


# Test 2: Room capacity
def test_room_capacity_insufficient():

    # M1.01 has capacity 45.
    # Database Systems requires 60 seats.

    assignment = ScheduleAssignment(
        exam_id="exam_db",
        date=date(2027, 1, 21),
        start_time=time(9, 0),
        room_ids=["room_m101"],
    )

    issues = run_validation(
        assignments=[assignment],
        expected_students={"exam_db": 60},
    )

    assert has_conflict(
        issues,
        ConflictType.INSUFFICIENT_CAPACITY,
    )


def test_room_capacity_sufficient():

    # M1.01 + M1.02 = 90 seats.
    # Database Systems requires 60 seats.

    assignment = ScheduleAssignment(
        exam_id="exam_db",
        date=date(2027, 1, 21),
        start_time=time(9, 0),
        room_ids=["room_m101", "room_m102"],
    )

    issues = run_validation(
        assignments=[assignment],
        expected_students={"exam_db": 60},
    )

    assert not has_conflict(
        issues,
        ConflictType.INSUFFICIENT_CAPACITY,
    )


# Test 3: Room availability
def test_room_unavailable():

    # Database Systems:
    # 09:00–10:30, Room M1.01
    #
    # Room M1.01 unavailable:
    # 08:00–12:00

    assignment = ScheduleAssignment(
        exam_id="exam_db",
        date=date(2027, 1, 21),
        start_time=time(9, 0),
        room_ids=["room_m101"],
    )

    blocked_room = RoomUnavailability(
        id="blocked_001",
        room_id="room_m101",
        start=datetime(2027, 1, 21, 8, 0),
        end=datetime(2027, 1, 21, 12, 0),
        reason="Maintenance",
    )

    issues = run_validation(
        assignments=[assignment],
        unavailable=[blocked_room],
    )

    assert has_conflict(
        issues,
        ConflictType.ROOM_UNAVAILABLE,
    )


def test_room_available_after_block():

    # Room unavailable until 09:00.
    # Exam starts exactly at 09:00.
    # No overlap.

    assignment = ScheduleAssignment(
        exam_id="exam_db",
        date=date(2027, 1, 21),
        start_time=time(9, 0),
        room_ids=["room_m101"],
    )

    blocked_room = RoomUnavailability(
        id="blocked_001",
        room_id="room_m101",
        start=datetime(2027, 1, 21, 8, 0),
        end=datetime(2027, 1, 21, 9, 0),
    )

    issues = run_validation(
        assignments=[assignment],
        unavailable=[blocked_room],
    )

    assert not has_conflict(
        issues,
        ConflictType.ROOM_UNAVAILABLE,
    )


# Test 4: Room overlap
def test_room_overlap():

    # Mathematics 1: 09:00–10:00
    # Programming 1: 09:30–10:30
    # Both use M1.01.

    assignments = [
        ScheduleAssignment(
            exam_id="exam_math1",
            date=date(2027, 1, 21),
            start_time=time(9, 0),
            room_ids=["room_m101"],
        ),
        ScheduleAssignment(
            exam_id="exam_prog1",
            date=date(2027, 1, 21),
            start_time=time(9, 30),
            room_ids=["room_m101"],
        ),
    ]

    issues = run_validation(assignments)

    assert has_conflict(
        issues,
        ConflictType.ROOM_OVERLAP,
    )


def test_no_room_overlap_different_rooms():

    # Same time, different rooms.
    assignments = [
        ScheduleAssignment(
            exam_id="exam_math1",
            date=date(2027, 1, 21),
            start_time=time(9, 0),
            room_ids=["room_m101"],
        ),
        ScheduleAssignment(
            exam_id="exam_prog1",
            date=date(2027, 1, 21),
            start_time=time(9, 0),
            room_ids=["room_m102"],
        ),
    ]

    issues = run_validation(assignments)

    assert not has_conflict(
        issues,
        ConflictType.ROOM_OVERLAP,
    )


def test_no_room_overlap_consecutive_exams():

    # Mathematics 1: 09:00–10:00
    # Programming 1: 10:00–11:00
    # Same room, but no time overlap.

    assignments = [
        ScheduleAssignment(
            exam_id="exam_math1",
            date=date(2027, 1, 21),
            start_time=time(9, 0),
            room_ids=["room_m101"],
        ),
        ScheduleAssignment(
            exam_id="exam_prog1",
            date=date(2027, 1, 21),
            start_time=time(10, 0),
            room_ids=["room_m101"],
        ),
    ]

    issues = run_validation(assignments)

    assert not has_conflict(
        issues,
        ConflictType.ROOM_OVERLAP,
    )
