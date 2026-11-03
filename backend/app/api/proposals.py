from fastapi import APIRouter, HTTPException, Depends
from app.auth.core import require_admin

from app.data.demo_plan import (
    proposals,
    proposal_metadata,
    schedules,
    current_schedules,
    planning_cycles,
    data_revision,
    room_unavailability,
    expected_students,
)
from app.data.mock_data import exams, rooms
from app.models.schedule import ScheduleStatus
from app.generator.schedule_diff import compare_schedules
from app.validator.schedule import validate_schedule


router = APIRouter(
    prefix="/proposals",
    tags=["Schedule Proposals"],
)



# GET /api/proposals/{proposal_id}

@router.get("/{proposal_id}")
def get_proposal(proposal_id: str):

    proposal = proposals.get(proposal_id)

    if proposal is None:
        raise HTTPException(
            status_code=404,
            detail="Proposal not found",
        )

    baseline_id = proposal.based_on_schedule_id
    baseline = schedules.get(baseline_id)

    if baseline is None:
        raise HTTPException(
            status_code=409,
            detail="Baseline schedule no longer exists",
        )

    return {
        "proposal": proposal,
        "diff": compare_schedules(baseline, proposal),
    }



# POST /api/proposals/{proposal_id}/confirm
@router.post(
    "/{proposal_id}/confirm",
    dependencies=[Depends(require_admin)],
)
def confirm_proposal(proposal_id: str):

    proposal = proposals.get(proposal_id)

    if proposal is None:
        raise HTTPException(
            status_code=404,
            detail="Proposal not found",
        )

    metadata = proposal_metadata[proposal_id]
    cycle_id = proposal.planning_cycle_id

    cycle = planning_cycles.get(cycle_id)

    if cycle is None:
        raise HTTPException(
            status_code=404,
            detail="Planning cycle not found",
        )

    # Prevent confirming a proposal based on
    # an outdated schedule.
    current_id = current_schedules.get(cycle_id)

    if current_id != metadata["baseline_id"]:
        raise HTTPException(
            status_code=409,
            detail="Baseline schedule has changed",
        )

    # Prevent confirming after relevant data changes.
    if data_revision["value"] != metadata["data_revision"]:
        raise HTTPException(
            status_code=409,
            detail="Planning data changed. Regenerate proposal.",
        )

    # Revalidate before saving.
    issues = validate_schedule(
        schedule=proposal,
        exams=exams,
        rooms=rooms,
        cycle=cycle,
        unavailable=room_unavailability,
        expected_students=expected_students,
    )

    if issues:
        raise HTTPException(
            status_code=409,
            detail="Proposal violates hard constraints",
        )

    # Allocate the next confirmed version number.
    versions = [
        schedule.version_number
        for schedule in schedules.values()
        if schedule.planning_cycle_id == cycle_id
        and schedule.status == ScheduleStatus.CONFIRMED
        and schedule.version_number is not None
    ]

    next_version = max(versions, default=0) + 1

    # Make a copy, preserving the original proposal
    # as a separate object.
    confirmed = proposal.model_copy(deep=True)

    confirmed.id = f"{cycle_id}_v{next_version}"
    confirmed.name = f"{cycle.name} - V{next_version}"
    confirmed.status = ScheduleStatus.CONFIRMED
    confirmed.version_number = next_version

    # The original baseline remains unchanged.
    schedules[confirmed.id] = confirmed
    current_schedules[cycle_id] = confirmed.id

    # A proposal must not be confirmed twice.
    del proposals[proposal_id]
    del proposal_metadata[proposal_id]

    return {
        "message": "Schedule confirmed",
        "schedule": confirmed,
    }
