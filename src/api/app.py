# src/api/app.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes import downloads, suggestions, topics, chat

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATIC_BUILD_DIR = os.path.join(BASE_DIR, "static_build")


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
  app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
  app.mount("/static_build", StaticFiles(directory=STATIC_BUILD_DIR), name="static_build")

  # Root path of webpage
  @app.get("/", response_class=FileResponse)
  async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

  # Routers
  app.include_router(topics.router, prefix="")
  app.include_router(suggestions.router, prefix="")
  app.include_router(chat.router, prefix="")
  app.include_router(downloads.router, prefix="")

  return app
