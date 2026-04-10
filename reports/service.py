import csv
import io
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tickets.models import Movie, Session as Screening, Ticket


async def generate_sales_csv(
    db: AsyncSession,
    date_from: date,
    date_to: date,
) -> tuple[str, str]:
    stmt = (
        select(
            Movie.title.label("movie"),
            func.date(Ticket.purchased_at).label("sale_date"),
            func.count(Ticket.id).label("tickets_sold"),
        )
        .join(Screening, Screening.id == Ticket.session_id)
        .join(Movie, Movie.id == Screening.movie_id)
        .where(Ticket.status == "reserved")
        .where(func.date(Ticket.purchased_at) >= date_from)
        .where(func.date(Ticket.purchased_at) <= date_to)
        .group_by(Movie.title, func.date(Ticket.purchased_at))
        .order_by(Movie.title, func.date(Ticket.purchased_at))
    )

    result = await db.execute(stmt)
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["Film", "Data", "Sold Tickets"])

    last_movie = None
    for row in rows:
        movie_cell = row.movie if row.movie != last_movie else ""
        last_movie = row.movie
        sale_date = row.sale_date.isoformat() if hasattr(row.sale_date, "isoformat") else str(row.sale_date)
        writer.writerow([movie_cell, sale_date, row.tickets_sold])

    content = output.getvalue()
    filename = f"sales_{date_from.isoformat()}_{date_to.isoformat()}.csv"
    return content, filename
