from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tickets.models import Movie, Room, RoomSeat, Session, Ticket


class TicketError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


async def list_sessions(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Session, Movie, Room)
        .join(Movie, Movie.id == Session.movie_id)
        .join(Room, Room.id == Session.room_id)
        .order_by(Session.starts_at)
    )

    sessions_out = []
    for session, movie, room in result.all():
        sold = await _count_sold(db, session.id)

        if room.room_type == "fixed":
            total_seats = await db.scalar(
                select(func.count()).where(RoomSeat.room_id == room.id)
            )
            available = total_seats - sold
            cap_available = None
        else:
            available = None
            cap_available = room.max_capacity - sold

        sessions_out.append({
            "id": session.id,
            "movie_id": movie.id,
            "movie_title": movie.title,
            "room_id": room.id,
            "room_name": room.name,
            "room_type": room.room_type,
            "starts_at": session.starts_at,
            "ends_at": session.ends_at,
            "seats_available": available,
            "capacity_available": cap_available,
        })
    return sessions_out


async def get_available_seats(db: AsyncSession, session_id: int) -> dict:
    session = await _get_session_or_raise(db, session_id)
    room = await db.get(Room, session.room_id)

    if room.room_type != "fixed":
        return {"session_id": session_id, "room_type": room.room_type, "seats": []}

    reserved_ids = (
        await db.scalars(
            select(Ticket.seat_id)
            .where(Ticket.session_id == session_id)
            .where(Ticket.status == "reserved")
        )
    ).all()

    available = (
        await db.scalars(
            select(RoomSeat)
            .where(RoomSeat.room_id == room.id)
            .where(RoomSeat.id.notin_(reserved_ids))
            .order_by(RoomSeat.row_num, RoomSeat.seat_num)
        )
    ).all()

    return {
        "session_id": session_id,
        "room_type": room.room_type,
        "seats": [
            {"id": s.id, "row_num": s.row_num, "seat_num": s.seat_num}
            for s in available
        ],
    }


async def buy_ticket(
    db: AsyncSession,
    user_id: int,
    session_id: int,
    seat_id: int | None,
) -> Ticket:
    session = await _get_session_or_raise(db, session_id)
    room = await db.get(Room, session.room_id)

    if room.room_type == "fixed":
        if seat_id is None:
            raise TicketError("seat_id is required for fixed-seat rooms", 422)

        seat = await db.scalar(
            select(RoomSeat)
            .where(RoomSeat.id == seat_id)
            .where(RoomSeat.room_id == room.id)
        )
        if seat is None:
            raise TicketError("Seat not found in this room", 404)

        already = await db.scalar(
            select(Ticket)
            .where(Ticket.session_id == session.id)
            .where(Ticket.seat_id == seat_id)
            .where(Ticket.status == "reserved")
        )
        if already:
            raise TicketError("This seat is already reserved", 409)

        ticket = Ticket(
            session_id=session.id,
            user_id=user_id,
            seat_id=seat_id,
            status="reserved",
        )
    else:
        if seat_id is not None:
            raise TicketError("seat_id must be omitted for open-space rooms", 422)

        sold = await _count_sold(db, session.id)
        if sold >= room.max_capacity:
            raise TicketError(f"Session is fully booked (capacity: {room.max_capacity})", 409)

        already = await db.scalar(
            select(Ticket)
            .where(Ticket.session_id == session.id)
            .where(Ticket.user_id == user_id)
            .where(Ticket.status == "reserved")
        )
        if already:
            raise TicketError("You already have a ticket for this session", 409)

        ticket = Ticket(
            session_id=session.id,
            user_id=user_id,
            seat_id=None,
            status="reserved",
        )

    db.add(ticket)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise TicketError("Booking failed, please try again", 409)

    await db.refresh(ticket)
    return ticket


async def get_my_tickets(db: AsyncSession, user_id: int) -> list[dict]:
    result = await db.execute(
        select(Ticket, Session, Movie)
        .join(Session, Session.id == Ticket.session_id)
        .join(Movie, Movie.id == Session.movie_id)
        .where(Ticket.user_id == user_id)
        .order_by(Ticket.purchased_at.desc())
    )

    out = []
    for ticket, session, movie in result.all():
        seat = await db.get(RoomSeat, ticket.seat_id) if ticket.seat_id else None
        out.append({
            "id": ticket.id,
            "session_id": ticket.session_id,
            "seat_id": ticket.seat_id,
            "status": ticket.status,
            "purchased_at": ticket.purchased_at,
            "movie_title": movie.title,
            "starts_at": session.starts_at,
            "row_num": seat.row_num if seat else None,
            "seat_num": seat.seat_num if seat else None,
        })
    return out


async def _get_session_or_raise(db: AsyncSession, session_id: int) -> Session:
    session = await db.get(Session, session_id)
    if not session:
        raise TicketError("Session not found", 404)
    return session


async def _count_sold(db: AsyncSession, session_id: int) -> int:
    return await db.scalar(
        select(func.count())
        .where(Ticket.session_id == session_id)
        .where(Ticket.status == "reserved")
    ) or 0
