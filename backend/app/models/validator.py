
from enum import Enum
from pydantic import BaseModel, Field

class ConflictType(str, Enum):
    ROOM_OVERLAP = "ROOM_OVERLAP"
    ROOM_UNAVAILABLE = "ROOM_UNAVAILABLE"
    INSUFFICIENT_CAPACITY = "INSUFFICIENT_CAPACITY"
    OUTSIDE_EXAM_PERIOD = "OUTSIDE_EXAM_PERIOD"
    UNKNOWN_EXAM = "UNKNOWN_EXAM"
    UNKNOWN_ROOM = "UNKNOWN_ROOM"


class ValidationIssue(BaseModel):
    type: ConflictType
    message: str
    exam_ids: list[str] = Field(default_factory=list)
    room_ids: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    valid: bool
    issues: list[ValidationIssue]
