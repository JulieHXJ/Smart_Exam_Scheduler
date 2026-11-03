
from fastapi import APIRouter, HTTPException

from app.data.mock_data import exams, rooms
from app.data.demo_plan import (
    planning_cycles,
    schedules,
    current_schedules,
    room_unavailability,
    expected_students,
)
from app.validator.schedule import validate_schedule


from fastapi import HTTPException

from app.data.demo_plan import (
    proposals,
    proposal_metadata,
    data_revision,
)
from app.generator.proposal import generate_proposal
from app.generator.schedule_diff import compare_schedules


router = APIRouter(
    prefix="/planning-cycles",
    tags=["Planning Cycles"],
)


@router.get("")
def list_planning_cycles():
    return list(planning_cycles.values())


@router.get("/{cycle_id}")
def get_planning_cycle(cycle_id: str):
    cycle = planning_cycles.get(cycle_id)

    if cycle is None:
        raise HTTPException(
            status_code=404,
            detail="Planning cycle not found",
        )

    return cycle


@router.get("/{cycle_id}/schedules/current")
def get_current_schedule(cycle_id: str):
    if cycle_id not in planning_cycles:
        raise HTTPException(
            status_code=404,
            detail="Planning cycle not found",
        )

    schedule_id = current_schedules.get(cycle_id)

    if schedule_id is None:
        raise HTTPException(
            status_code=404,
            detail="No confirmed schedule found",
        )

    return schedules[schedule_id]


@router.post("/{cycle_id}/validate")
def validate_current_schedule(cycle_id: str):

    cycle = planning_cycles.get(cycle_id)

    if cycle is None:
        raise HTTPException(
            status_code=404,
            detail="Planning cycle not found",
        )

    schedule_id = current_schedules.get(cycle_id)

    if schedule_id is None:
        raise HTTPException(
            status_code=404,
            detail="No confirmed schedule found",
        )

    schedule = schedules[schedule_id]

    issues = validate_schedule(
        schedule=schedule,
        exams=exams,
        rooms=rooms,
        cycle=cycle,
        unavailable=room_unavailability,
        expected_students=expected_students,
    )

    return {
        "schedule_id": schedule.id,
        "valid": len(issues) == 0,
        "issues": issues,
    }



@router.post("/{cycle_id}/proposals")
def create_schedule_proposal(cycle_id: str):

    cycle = planning_cycles.get(cycle_id)

    if cycle is None:
        raise HTTPException(
            status_code=404,
            detail="Planning cycle not found",
        )

    current_id = current_schedules.get(cycle_id)

    # if no valid schedule, return 409 conflict.
    if current_id is None:
        raise HTTPException(
            status_code=409,
            detail="No baseline schedule available",
        )

    baseline = schedules[current_id]

    proposal = generate_proposal(
        baseline=baseline,
        cycle=cycle,
        exams=exams,
        rooms=rooms,
        unavailable=room_unavailability,
        expected_students=expected_students,
    )

    if proposal is None:
        raise HTTPException(
            status_code=409,
            detail="Could not generate a feasible proposal",
        )

    proposals[proposal.id] = proposal

    proposal_metadata[proposal.id] = {
        "baseline_id": baseline.id,
        "data_revision": data_revision["value"],
    }

    return {
        "proposal": proposal,
        "diff": compare_schedules(baseline, proposal),
    }
