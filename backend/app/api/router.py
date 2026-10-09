from fastapi import APIRouter
from app.data.mock_data import exams, registrations, rooms, students

router = APIRouter()

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