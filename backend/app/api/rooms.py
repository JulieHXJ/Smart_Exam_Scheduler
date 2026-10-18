
from fastapi import APIRouter, HTTPException

from app.data.mock_data import rooms
from app.data.demo_plan import room_unavailability
from app.models.room import RoomUnavailability


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)


@router.put("/{room_id}/unavailability")
def update_room_unavailability(
    room_id: str,
    data: RoomUnavailability,
):
    # Check whether the room exists
    room_exists = any(
        room.id == room_id
        for room in rooms
    )

    if not room_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Room {room_id} not found",
        )

    # Ensure URL and request body refer to the same room
    if data.room_id != room_id:
        raise HTTPException(
            status_code=422,
            detail="Room ID in URL does not match request body",
        )

    # Replace an existing block with the same ID
    for index, blocked in enumerate(room_unavailability):
        if blocked.id == data.id:
            if blocked.room_id != room_id:
                raise HTTPException(
                    status_code=409,
                    detail="Block ID belongs to another room",
                )

            room_unavailability[index] = data

            return {
                "message": "Room availability updated",
                "data": data,
            }

    # Add a new block
    room_unavailability.append(data)

    return {
        "message": "Room availability updated",
        "data": data,
    }
