
from fastapi import APIRouter, Depends

from app.data.mock_data import exams, registrations, rooms, students

from app.api.planning_cycle import router as planning_cycles_router
from app.api.rooms import router as rooms_router
from app.api.proposals import router as proposals_router
from app.api.auth import router as auth_router

from app.auth.core import get_current_user, require_admin


router = APIRouter()

# Public authentication endpoints
router.include_router(auth_router)

# Protected planning endpoints
router.include_router(
    planning_cycles_router,
    dependencies=[Depends(get_current_user)],
)

router.include_router(
    rooms_router,
    dependencies=[Depends(require_admin)],
)

router.include_router(
    proposals_router,
    dependencies=[Depends(get_current_user)],
)


@router.get("/exams", dependencies=[Depends(get_current_user)])
def get_exams():
    return exams


@router.get("/rooms", dependencies=[Depends(get_current_user)])
def get_rooms():
    return rooms


@router.get("/students", dependencies=[Depends(get_current_user)])
def get_students():
    return students


@router.get("/registrations", dependencies=[Depends(get_current_user)])
def get_registrations():
    return registrations
