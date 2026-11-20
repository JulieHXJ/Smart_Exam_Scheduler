from enum import Enum
from pydantic import BaseModel, Field

class ExamType(str, Enum):
    WRITTEN = "written"
    DIGITAL = "digital"
    ORAL = "oral"
    PRESENTATION = "presentation"

class ExamCategory(str, Enum):
    REGULAR = "regular"
    REPEATER = "repeater"
    ELECTIVE = "elective"


class Exam(BaseModel):
    id: str
    exam_number: str | None = None
    title: str
    study_program: str
    semester: int
    duration_minutes: int = Field(gt=0)
    examiner_ids: list[str]
    exam_type: ExamType
    category: ExamCategory = ExamCategory.REGULAR