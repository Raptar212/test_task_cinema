-- Migration 003: rooms + room_seats
-- Depends on: 002

CREATE TYPE room_type AS ENUM ('fixed', 'open');

CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    room_type room_type NOT NULL,
    max_capacity INT,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_room_capacity CHECK (
        (room_type = 'open'  AND max_capacity IS NOT NULL AND max_capacity > 0)
        OR
        (room_type = 'fixed' AND max_capacity IS NULL)
    )
);

CREATE TABLE room_seats (
    id SERIAL PRIMARY KEY,
    room_id INT NOT NULL REFERENCES rooms (id) ON DELETE CASCADE,
    row_num SMALLINT NOT NULL CHECK (row_num  > 0),
    seat_num SMALLINT NOT NULL CHECK (seat_num > 0),

    CONSTRAINT uq_room_seat UNIQUE (room_id, row_num, seat_num)
);

CREATE INDEX idx_room_seats_room_id ON room_seats (room_id);
