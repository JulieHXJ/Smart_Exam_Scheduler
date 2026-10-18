
from datetime import datetime, timedelta

from app.models.schedule import Schedule
from app.models.exam import Exam
from app.models.room import Room
from app.models.planning_cycle import PlanningCycle

from app.models.validator import (
    ConflictType,
    ValidationIssue,
)

def overlaps(start_a, end_a, start_b, end_b):
    return start_a < end_b and start_b < end_a


def check_exam_period(
    assignment,
    cycle,
) -> list[ValidationIssue]:

    if (
        cycle.exam_period_start
        <= assignment.date
        <= cycle.exam_period_end
    ):
        return []

    return [
        ValidationIssue(
            type=ConflictType.OUTSIDE_EXAM_PERIOD,
            message=(
                f"Exam {assignment.exam_id} is outside "
                "the examination period."
            ),
            exam_ids=[assignment.exam_id],
        )
    ]

def check_room_capacity(
    assignment,
    rooms_by_id: dict,
    required_students: int | None,
) -> list[ValidationIssue]:

    if required_students is None:
        return []

    total_capacity = sum(
        rooms_by_id[room_id].capacity or 0
        for room_id in set(assignment.room_ids)
        if room_id in rooms_by_id
    )

    if total_capacity >= required_students:
        return []

    return [
        ValidationIssue(
            type=ConflictType.INSUFFICIENT_CAPACITY,
            message=(
                f"Exam {assignment.exam_id} requires "
                f"{required_students} seats, but only "
                f"{total_capacity} are available."
            ),
            exam_ids=[assignment.exam_id],
            room_ids=assignment.room_ids,
        )
    ]

def check_exam_exists(
    assignment,
    exams_by_id: dict,
) -> list[ValidationIssue]:

    if assignment.exam_id in exams_by_id:
        return []

    return [
        ValidationIssue(
            type=ConflictType.UNKNOWN_EXAM,
            message=f"Exam {assignment.exam_id} does not exist.",
            exam_ids=[assignment.exam_id],
        )
    ]


def check_room_exists(
    assignment,
    rooms_by_id: dict,
) -> list[ValidationIssue]:

    issues = []

    for room_id in set(assignment.room_ids):
        if room_id not in rooms_by_id:
            issues.append(
                ValidationIssue(
                    type=ConflictType.UNKNOWN_ROOM,
                    message=f"Room {room_id} does not exist.",
                    exam_ids=[assignment.exam_id],
                    room_ids=[room_id],
                )
            )

    return issues


# room availability helper
def get_exam_interval(
    assignment,
    exam: Exam,
) -> tuple[datetime, datetime]:

    start = datetime.combine(
        assignment.date,
        assignment.start_time,
    )

    end = start + timedelta(
        minutes=exam.duration_minutes
    )

    return start, end


def check_room_availability(
    assignment,
    exam: Exam,
    unavailable: list,
) -> list[ValidationIssue]:

    issues = []
    start, end = get_exam_interval(assignment, exam)

    for blocked in unavailable:

        if blocked.room_id not in assignment.room_ids:
            continue

        if overlaps(start, end, blocked.start, blocked.end):
            issues.append(
                ValidationIssue(
                    type=ConflictType.ROOM_UNAVAILABLE,
                    message=(
                        f"Room {blocked.room_id} is unavailable "
                        f"during exam {assignment.exam_id}."
                    ),
                    exam_ids=[assignment.exam_id],
                    room_ids=[blocked.room_id],
                )
            )

    return issues

def check_room_overlap(
    schedule: Schedule,
    exams_by_id: dict,
) -> list[ValidationIssue]:

    issues = []
    assignments = schedule.assignments

    for i, assignment_a in enumerate(assignments):

        exam_a = exams_by_id.get(assignment_a.exam_id)

        if exam_a is None:
            continue

        start_a, end_a = get_exam_interval(
            assignment_a, exam_a
        )

        for assignment_b in assignments[i + 1:]:

            exam_b = exams_by_id.get(assignment_b.exam_id)

            if exam_b is None:
                continue

            shared_rooms = (
                set(assignment_a.room_ids)
                & set(assignment_b.room_ids)
            )

            if not shared_rooms:
                continue

            start_b, end_b = get_exam_interval(
                assignment_b, exam_b
            )

            if overlaps(start_a, end_a, start_b, end_b):
                issues.append(
                    ValidationIssue(
                        type=ConflictType.ROOM_OVERLAP,
                        message=(
                            f"Exams {assignment_a.exam_id} and "
                            f"{assignment_b.exam_id} overlap "
                            "in the same room."
                        ),
                        exam_ids=[
                            assignment_a.exam_id,
                            assignment_b.exam_id,
                        ],
                        room_ids=sorted(shared_rooms),
                    )
                )

    return issues



def validate_schedule(
    schedule: Schedule,
    exams: list[Exam],
    rooms: list[Room],
    cycle: PlanningCycle,
    unavailable: list,
    expected_students: dict[str, int],
) -> list[ValidationIssue]:

    issues: list[ValidationIssue] = []

    exams_by_id = {
        exam.id: exam
        for exam in exams
    }

    rooms_by_id = {
        room.id: room
        for room in rooms
    }

    for assignment in schedule.assignments:

        exam_issues = check_exam_exists(
            assignment,
            exams_by_id,
        )
        issues.extend(exam_issues)

        if exam_issues:
            continue
        exam = exams_by_id[assignment.exam_id]

        issues.extend(
            check_exam_period(
                assignment,
                cycle,
            )
        )

        issues.extend(
            check_room_exists(
                assignment,
                rooms_by_id,
            )
        )

        room_issues = check_room_exists(
            assignment,
            rooms_by_id,
        )

        issues.extend(room_issues)
        if not room_issues:
            issues.extend(
                check_room_capacity(
                    assignment,
                    rooms_by_id,
                    expected_students.get(exam.id),
                )
            )

        issues.extend(
            check_room_availability(
                assignment,
                exam,
                unavailable,
            )
        )

    # Check overlapping room assignments
    issues.extend(
        check_room_overlap(
            schedule,
            exams_by_id,
        )
    )

    return issues
