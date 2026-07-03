from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api.routes.candidates import router as candidates_router
from api.api.routes.jd_intelligence import router as jd_intelligence_router
from api.api.routes.jobs import router as jobs_router
from api.api.routes.recommendations import router as recommendations_router
from api.api.routes.signals import router as signals_router
from api.core.config import settings
from api.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered talent sourcing platform API.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(jobs_router)
    app.include_router(jd_intelligence_router)
    app.include_router(candidates_router)
    app.include_router(signals_router)
    app.include_router(recommendations_router)

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    @app.get("/health", tags=["System"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
