from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, model_validator



class RoomType(str, Enum):
    EXAM_ROOM = "exam_room"
    LAB = "lab"
    EXTERNAL = "external"
    SPECIAL = "special"

class Room(BaseModel):
    id: str
    name: str
    capacity: int | None = Field(default=None, ge=0)
    room_type: RoomType

class RoomUnavailability(BaseModel):
    id: str
    room_id: str
    start: datetime
    end: datetime
    reason: str | None = None

    @model_validator(mode="after")
    def validate_interval(self):
        if self.end <= self.start:
            raise ValueError(
                "End must be after start"
            )
        return self

