"""App factory: logging, CORS, routers, exception handlers."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    routes_analysis,
    routes_comparison,
    routes_logs,
    routes_mods,
    routes_repairs,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("mpa")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Minecraft Modpack Analyzer",
        description="Local read-only analysis of Minecraft modpack folders.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = FastAPI()  # unused — routers mount directly
    del api

    app.include_router(routes_analysis.router, prefix="/api")
    app.include_router(routes_mods.router, prefix="/api")
    app.include_router(routes_logs.router, prefix="/api")
    app.include_router(routes_repairs.router, prefix="/api")
    app.include_router(routes_comparison.router, prefix="/api")

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    return app


app = create_app()
