from enum import Enum
from pydantic import BaseModel, Field

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