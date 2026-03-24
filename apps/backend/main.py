"""
GoalPilot Intelligence API — FastAPI entrypoint.

Run with:
    cd apps/backend/intelligence/src
    uvicorn main_api:app --reload --port 8000
"""

import sys
import os

# Anchor sys.path so routers can import core modules

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router_chat, router_goals, router_dashboard, router_cashflow, router_input
from data.db import ensure_database_initialized

app = FastAPI(
    title="GoalPilot Intelligence API",
    version="0.1.0",
    description="Backend API for GoalPilot — AI Financial Assistant",
)

# CORS — allow all origins in dev (Expo Go needs this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(router_chat.router,      prefix="/api", tags=["Chat"])
app.include_router(router_goals.router,     prefix="/api", tags=["Goals"])
app.include_router(router_dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(router_cashflow.router,  prefix="/api", tags=["CashFlow"])
app.include_router(router_input.router,     prefix="/api", tags=["InputData"])


@app.on_event("startup")
def initialize_database():
    ensure_database_initialized()


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "GoalPilot Intelligence API"}
