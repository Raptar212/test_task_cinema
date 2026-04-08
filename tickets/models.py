from sqlalchemy import (
    CheckConstraint, Column, DateTime, Enum,
    ForeignKey, Integer, SmallInteger, String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import relationship

from auth.models import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    sessions = relationship("Session", back_populates="movie")


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        CheckConstraint(
            "(room_type = 'open' AND max_capacity IS NOT NULL AND max_capacity > 0) OR "
            "(room_type = 'fixed' AND max_capacity IS NULL)",
            name="chk_room_capacity",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    room_type = Column(Enum("fixed", "open", name="room_type"), nullable=False)
    max_capacity = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    seats = relationship("RoomSeat", back_populates="room", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="room")


class RoomSeat(Base):
    __tablename__ = "room_seats"
    __table_args__ = (
        UniqueConstraint("room_id", "row_num", "seat_num", name="uq_room_seat"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    row_num = Column(SmallInteger, nullable=False)
    seat_num = Column(SmallInteger, nullable=False)

    room = relationship("Room", back_populates="seats")
    tickets = relationship("Ticket", back_populates="seat")


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="chk_session_times"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="RESTRICT"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)

    movie = relationship("Movie", back_populates="sessions")
    room = relationship("Room", back_populates="sessions")
    tickets = relationship("Ticket", back_populates="session")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("session_id", "seat_id", name="uq_ticket_seat"),
        UniqueConstraint("session_id", "user_id", "seat_id", name="uq_ticket_user_seat"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="RESTRICT"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    seat_id = Column(Integer, ForeignKey("room_seats.id", ondelete="RESTRICT"), nullable=True)
    status = Column(Enum("reserved", "cancelled", name="ticket_status"), nullable=False, default="reserved")
    purchased_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    session = relationship("Session", back_populates="tickets")
    seat = relationship("RoomSeat", back_populates="tickets")
