
from app.models.schedule import Schedule


def compare_schedules(
    baseline: Schedule,
    proposal: Schedule,
) -> list[dict]:
    "Present a comparison of two schedules in a human-readable format."

    old_assignments = {
        assignment.exam_id: assignment
        for assignment in baseline.assignments
    }

    new_assignments = {
        assignment.exam_id: assignment
        for assignment in proposal.assignments
    }

    changes = []

    for exam_id in sorted(
        old_assignments.keys() | new_assignments.keys()
    ):
        old = old_assignments.get(exam_id)
        new = new_assignments.get(exam_id)

        if old is None:
            change_type = "ADDED"

        elif new is None:
            change_type = "REMOVED"

        elif old == new:
            change_type = "UNCHANGED"

        elif (
            old.date == new.date
            and old.start_time == new.start_time
        ):
            change_type = "ROOM_CHANGED"

        elif old.room_ids == new.room_ids:
            change_type = "TIME_CHANGED"

        else:
            change_type = "MULTIPLE_CHANGES"

        changes.append({
            "exam_id": exam_id,
            "change_type": change_type,
            "before": old,
            "after": new,
        })

    return changes
