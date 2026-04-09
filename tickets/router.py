from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_viewer
from auth.models import User, get_db
from tickets.schemas import (
    AvailableSeatsOut, BuyTicketRequest,
    MyTicketsOut, SessionListOut, TicketOut,
)
from tickets.service import TicketError, buy_ticket, get_available_seats, get_my_tickets, list_sessions

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/sessions", response_model=SessionListOut)
async def sessions(db: AsyncSession = Depends(get_db)):
    rows = await list_sessions(db)
    return {"sessions": rows, "total": len(rows)}


@router.get("/sessions/{session_id}/seats", response_model=AvailableSeatsOut)
async def available_seats(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await get_available_seats(db, session_id)
    except TicketError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return result


@router.post("/buy", response_model=TicketOut, status_code=201)
async def buy(
    body: BuyTicketRequest,
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    try:
        ticket = await buy_ticket(
            db,
            user_id=current_user.id,
            session_id=body.session_id,
            seat_id=body.seat_id,
        )
    except TicketError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    my = await get_my_tickets(db, current_user.id)
    rich = next((t for t in my if t["id"] == ticket.id), None)
    if rich is None:
        raise HTTPException(status_code=500, detail="Ticket created but could not be retrieved")
    return rich


@router.get("/my", response_model=MyTicketsOut)
async def my_tickets(
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    tickets = await get_my_tickets(db, current_user.id)
    return {"tickets": tickets, "total": len(tickets)}
