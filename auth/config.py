import os
from datetime import timedelta

SESSION_TTL = timedelta(hours=int(os.getenv("SESSION_TTL_HOURS", "24")))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://cinema:cinema@db:5432/cinema"
)
