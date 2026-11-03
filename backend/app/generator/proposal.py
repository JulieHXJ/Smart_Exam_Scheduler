
from app.models.validator import ValidationIssue
from app.validator.schedule import validate_schedule

from datetime import date, time, timedelta
from itertools import combinations

from uuid import uuid4

from app.models.schedule import (
    ScheduleAssignment,
    Schedule,
    ScheduleStatus,
)


# get_affected_exam_ids()
# generate_candidates()
# try_reschedule_exam()


TIME_SLOTS = [
    time(9, 0),
    time(11, 0),
    time(14, 0),
]


def get_affected_exam_ids(
    issues: list[ValidationIssue],
) -> list[str]:
    affected = []

    for issue in issues:
        if not issue.exam_ids:
            continue

        # For a pairwise overlap, prefer moving the
        # second examination first.
        exam_id = issue.exam_ids[-1]

        if exam_id not in affected:
            affected.append(exam_id)

    return affected


def generate_candidates(
    original: ScheduleAssignment,
    cycle,
    rooms,
):
    "Priority: "
    "1. same date/time, alternative rooms; "
    "2. alternative times/dates."
    # Try changing rooms at the original time first.
    dates = [original.date]

    current_date = cycle.exam_period_start

    while current_date <= cycle.exam_period_end:
        if (
            current_date.weekday() < 5
            and current_date != original.date
        ):
            dates.append(current_date)

        current_date += timedelta(days=1)

    times = [
        original.start_time,
        *[
            slot for slot in TIME_SLOTS
            if slot != original.start_time
        ],
    ]

    room_ids = [room.id for room in rooms]

    # Support one or two rooms in this demo.
    room_options = [
        list(group)
        for size in (1, 2)
        for group in combinations(room_ids, size)
    ]

    # Prefer the same room combination where possible.
    room_options.sort(
        key=lambda option: (
            set(option) != set(original.room_ids),
            len(option),
        )
    )

    # First: same date and time, alternative rooms.
    for room_option in room_options:
        if set(room_option) == set(original.room_ids):
            continue

        yield original.model_copy(
            update={"room_ids": room_option}
        )

    # Then: alternative times and dates.
    for day in dates:
        for slot in times:
            for room_option in room_options:

                if (
                    day == original.date
                    and slot == original.start_time
                ):
                    continue

                yield original.model_copy(
                    update={
                        "date": day,
                        "start_time": slot,
                        "room_ids": room_option,
                    }
                )



def try_reschedule_exam(
    schedule,
    exam_id,
    cycle,
    exams,
    rooms,
    unavailable,
    expected_students,
) -> bool:
    "Reschedule process:"
    "1. get the assignment"
    "2. replace with valid candidates"
    "3. validate the schedule"

    index = next(
        (
            i for i, assignment
            in enumerate(schedule.assignments)
            if assignment.exam_id == exam_id
        ),
        None,
    )

    if index is None:
        return False

    original = schedule.assignments[index]

    for candidate in generate_candidates(
        original, cycle, rooms
    ):
        schedule.assignments[index] = candidate

        issues = validate_schedule(
            schedule=schedule,
            exams=exams,
            rooms=rooms,
            cycle=cycle,
            unavailable=unavailable,
            expected_students=expected_students,
        )

        # Candidate must not violate any currently
        # implemented hard constraint involving this exam.
        if not any(
            exam_id in issue.exam_ids
            for issue in issues
        ):
            return True

    schedule.assignments[index] = original
    return False


# greedy version, may not find the best solution. Will implement CP-SAT later.
def generate_proposal(
    baseline: Schedule,
    cycle,
    exams,
    rooms,
    unavailable,
    expected_students,
) -> Schedule | None:

    proposal = baseline.model_copy(deep=True)

    proposal.id = f"proposal_{uuid4().hex[:12]}"
    proposal.name = f"{cycle.name} - Proposal"
    proposal.status = ScheduleStatus.PROPOSAL
    proposal.version_number = None
    proposal.based_on_schedule_id = baseline.id

    # Try to resolve the currently reported conflicts.
    # Stop if no further progress can be made.
    max_iterations = max(1, len(proposal.assignments) * 3)

    for _ in range(max_iterations):
        issues = validate_schedule(
            schedule=proposal,
            exams=exams,
            rooms=rooms,
            cycle=cycle,
            unavailable=unavailable,
            expected_students=expected_students,
        )

        if not issues:
            return proposal

        improved = False

        for exam_id in get_affected_exam_ids(issues):
            if try_reschedule_exam(
                proposal,
                exam_id,
                cycle,
                exams,
                rooms,
                unavailable,
                expected_students,
            ):
                improved = True
                break

        if not improved:
            return None

    return None
