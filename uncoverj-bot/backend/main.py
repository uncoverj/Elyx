from fastapi import FastAPI
from backend.routers import leaderboard as leaderboard_router

app = FastAPI(title="Uncoverj API", version="1.0.0")

app.include_router(leaderboard_router.router, prefix="/api", tags=["leaderboard"])
