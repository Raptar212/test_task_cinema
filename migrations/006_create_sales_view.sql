-- Migration 006: v_sales_report view
-- Depends on: 005

CREATE VIEW v_sales_report AS
SELECT
    m.title AS movie,
    t.purchased_at::DATE AS sale_date,
    COUNT(*) AS tickets_sold
FROM tickets t
    JOIN sessions s ON s.id = t.session_id
    JOIN movies m ON m.id = s.movie_id
WHERE t.status = 'reserved'
GROUP BY m.title, t.purchased_at::DATE;
