
from datetime import date, time

from app.models.planning_cycle import PlanningCycle
from app.models.schedule import (
    Schedule,
    ScheduleAssignment,
    ScheduleStatus,
)


planning_cycles = {
    "plan_ws_2026": PlanningCycle(
        id="plan_ws_2026",
        name="WS 2026/27",
        exam_period_start=date(2027, 1, 18),
        exam_period_end=date(2027, 2, 12),
    )
}


schedules = {
    "schedule_v1": Schedule(
        id="schedule_v1",
        name="WS 2026/27 - V1",
        planning_cycle_id="plan_ws_2026",
        version_number=1,
        status=ScheduleStatus.CONFIRMED,
        assignments=[
            ScheduleAssignment(
                exam_id="exam_math1",
                date=date(2027, 1, 19),
                start_time=time(9, 0),
                room_ids=["room_m101"],
            ),
            ScheduleAssignment(
                exam_id="exam_prog1",
                date=date(2027, 1, 20),
                start_time=time(9, 0),
                room_ids=["room_m102"],
            ),
            ScheduleAssignment(
                exam_id="exam_db",
                date=date(2027, 1, 21),
                start_time=time(9, 0),
                room_ids=["room_m101"],
            ),
        ],
    )
}


current_schedules = {
    "plan_ws_2026": "schedule_v1"
}


room_unavailability = []

expected_students = {
    "exam_math1": 30,
    "exam_prog1": 25,
    "exam_db": 35,
}
