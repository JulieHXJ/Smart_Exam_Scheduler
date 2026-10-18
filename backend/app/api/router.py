from fastapi import APIRouter
from app.data.mock_data import exams, registrations, rooms, students
from app.api.planning_cycle import router as planning_cycles_router
from app.api.rooms import router as rooms_router


router = APIRouter()

router.include_router(planning_cycles_router)
router.include_router(rooms_router)

@router.get("/exams")
def get_exams():
    return exams

@router.get("/rooms")
def get_rooms():
    return rooms

@router.get("/students")
def get_students():
    return students

@router.get("/registrations")
def get_registrations():
    return registrations