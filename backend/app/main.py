from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ai, applications, auth, candidates, health, interviews, jobs, resumes
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


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

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
