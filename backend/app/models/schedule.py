from datetime import date, time
from pydantic import BaseModel

class ScheduleAssignment(BaseModel):
    exam_id: str
    date: date
    start_time: time
    room_ids: list[str] # can be multiple rooms for one exam


class Schedule(BaseModel):
    id: str
    name: str
    assignments: list[ScheduleAssignment]