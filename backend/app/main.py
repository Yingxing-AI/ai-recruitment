import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api.routes import ai, applications, audit, auth, candidates, dashboard, health, interviews, jobs, resumes
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger(__name__)


def wait_for_database_ready() -> None:
    max_attempts = max(1, settings.database_startup_max_attempts)
    delay_seconds = max(0.0, settings.database_startup_retry_delay_seconds)

    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except OperationalError:
            if attempt == max_attempts:
                raise
            logger.warning(
                "Database is not ready on startup; retrying in %ss (%s/%s)",
                delay_seconds,
                attempt,
                max_attempts,
            )
            time.sleep(delay_seconds)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
    app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["candidates"])
    app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["resumes"])
    app.include_router(applications.router, prefix="/api/v1/applications", tags=["applications"])
    app.include_router(interviews.router, prefix="/api/v1/interviews", tags=["interviews"])
    app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
    app.include_router(audit.router, prefix="/api/v1/audit-logs", tags=["audit-logs"])

    @app.on_event("startup")
    def on_startup() -> None:
        wait_for_database_ready()
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
