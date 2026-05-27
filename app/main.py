import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.database import create_all_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("orderbot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run on startup and shutdown."""
    log.info("Starting OrderBot...")
    await create_all_tables()
    log.info("Database tables ready.")
    yield
    log.info("OrderBot shutting down.")


app = FastAPI(
    title="OrderBot API",
    version="2.0.0",
    description="Async AI-powered supply chain assistant for Tata Steel",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        settings.FRONTEND_ORIGIN,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
