from datetime import datetime

from pydantic import BaseModel


class SeatOut(BaseModel):
    id: int
    row_num: int
    seat_num: int

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: int
    movie_id: int
    movie_title: str
    room_id: int
    room_name: str
    room_type: str
    starts_at: datetime
    ends_at: datetime
    seats_available: int | None
    capacity_available: int | None

    model_config = {"from_attributes": True}


class SessionListOut(BaseModel):
    sessions: list[SessionOut]
    total: int


class AvailableSeatsOut(BaseModel):
    session_id: int
    room_type: str
    seats: list[SeatOut]


class BuyTicketRequest(BaseModel):
    session_id: int
    seat_id: int | None = None


class TicketOut(BaseModel):
    id: int
    session_id: int
    seat_id: int | None
    status: str
    purchased_at: datetime
    movie_title: str
    starts_at: datetime
    row_num: int | None
    seat_num: int | None

    model_config = {"from_attributes": True}


class MyTicketsOut(BaseModel):
    tickets: list[TicketOut]
    total: int
