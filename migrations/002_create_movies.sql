-- Migration 002: movies
-- Depends on: 001

CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL CHECK (duration_minutes > 0),
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
