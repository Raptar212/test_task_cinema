from fastapi import FastAPI


app = FastAPI(
    title="Cinema Ticket Service",
    version="1.0.0",
    description="RESTful API for cinema ticket management",
)

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
