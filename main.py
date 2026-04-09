from fastapi import FastAPI

from auth.router import router as auth_router
from reports.router import router as reports_router

app = FastAPI(
    title="Cinema Ticket Service",
    version="1.0.0",
    description="RESTful API for cinema ticket management",
)

app.include_router(auth_router)
app.include_router(reports_router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
