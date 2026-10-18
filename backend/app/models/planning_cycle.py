
from datetime import date
from pydantic import BaseModel, Field, model_validator


class PlanningCycle(BaseModel):
    id: str
    name: str
    exam_period_start: date
    exam_period_end: date
    reference_schedule_id: str | None = None
    current_schedule_id: str | None = None

    @model_validator(mode="after")
    def check_period(self):
        if self.exam_period_end < self.exam_period_start:
            raise ValueError(
                "Exam period end must not precede start"
            )
        return self
