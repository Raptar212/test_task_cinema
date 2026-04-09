-- Migration 005: tickets
-- Depends on: 004

CREATE TYPE ticket_status AS ENUM ('reserved', 'cancelled');

CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES sessions (id) ON DELETE RESTRICT,
    user_id INT NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    seat_id INT REFERENCES room_seats (id) ON DELETE RESTRICT,
    status ticket_status NOT NULL DEFAULT 'reserved',
    purchased_at TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    -- one seat per session (fixed rooms)
    CONSTRAINT uq_ticket_seat UNIQUE (session_id, seat_id),
    -- one user can't book the same seat twice for the same session
    CONSTRAINT uq_ticket_user_seat UNIQUE (session_id, user_id, seat_id)
);

CREATE INDEX idx_tickets_session_id ON tickets (session_id);
CREATE INDEX idx_tickets_user_id ON tickets (user_id);
CREATE INDEX idx_tickets_purchased_at ON tickets (purchased_at);
