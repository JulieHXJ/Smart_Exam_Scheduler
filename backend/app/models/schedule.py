from datetime import date, time
from enum import Enum
from pydantic import BaseModel, Field, model_validator

class ScheduleStatus(str, Enum):
    PROPOSAL = "proposal"
    CONFIRMED = "confirmed"

class ScheduleAssignment(BaseModel):
    exam_id: str
    date: date
    start_time: time
    room_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_rooms(self):
        if len(self.room_ids) != len(set(self.room_ids)):
            raise ValueError("Duplicate room IDs are not allowed")
        return self


class Schedule(BaseModel):
    id: str
    name: str
    planning_cycle_id: str
    version_number: int | None = None
    status: ScheduleStatus = ScheduleStatus.PROPOSAL
    based_on_schedule_id: str | None = None
    assignments: list[ScheduleAssignment] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_version(self):
        if (
            self.status == ScheduleStatus.CONFIRMED
            and self.version_number is None
        ):
            raise ValueError(
                "Confirmed schedules require a version number"
            )

        if (
            self.status == ScheduleStatus.PROPOSAL
            and self.version_number is not None
        ):
            raise ValueError(
                "Proposals must not have a confirmed version number"
            )

        return self
