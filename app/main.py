from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.registry import router as registry_router
from app.db import close_db, init_db

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    log.info("registry_ready")
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
app.include_router(registry_router, prefix="/api")
