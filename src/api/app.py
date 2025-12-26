# src/api/app.py
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routes import downloads, suggestions, topics, chat, history
from src.weather.api.routes.weather import router as weather_router

def get_base_dir() -> Path:
    # When running as a PyInstaller bundle
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    # Normal dev mode
    return Path(__file__).resolve().parents[3]


BASE_DIR = get_base_dir()
STATIC_DIR = BASE_DIR / "static"
STATIC_BUILD_DIR = BASE_DIR / "static_build"


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.mount("/static_build", StaticFiles(directory=str(STATIC_BUILD_DIR)), name="static_build")

    @app.get("/", response_class=FileResponse)
    async def index():
        return FileResponse(STATIC_DIR / "index.html")

    app.include_router(topics.router, prefix="")
    app.include_router(suggestions.router, prefix="")
    app.include_router(chat.router, prefix="")
    app.include_router(downloads.router, prefix="")
    app.include_router(history.router, prefix="")
    app.include_router(weather_router, prefix="")

    return app