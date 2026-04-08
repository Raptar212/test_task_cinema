-- Migration 004: sessions
-- Depends on: 003

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    movie_id INT NOT NULL REFERENCES movies (id) ON DELETE RESTRICT,
    room_id INT NOT NULL REFERENCES rooms  (id) ON DELETE RESTRICT,
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT chk_session_times CHECK (ends_at > starts_at)
);

CREATE INDEX idx_sessions_movie_id  ON sessions (movie_id);
CREATE INDEX idx_sessions_room_id   ON sessions (room_id);
CREATE INDEX idx_sessions_starts_at ON sessions (starts_at);
