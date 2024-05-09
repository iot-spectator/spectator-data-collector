"""Spectator Data Collector Application."""

import contextlib
import logging

import fastapi

from fastapi.middleware.cors import CORSMiddleware

from collector import logger
from collector.controller import device_manager
from collector.controller import resource_manager


logger.setup_logger(level=logging.DEBUG, console=True)
app_logger = logger.get_logger(name=__name__)

ORIGINS = ["127.0.0.1:3000", "http://localhost:3000", "localhost:3000"]


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    """Startup and shutdown."""
    app_logger.info("Service starts...")
    yield
    app_logger.info("Service shutdowns...")


app = fastapi.FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(device_manager.router)
app.include_router(resource_manager.router)


@app.get("/", tags=["root"])
async def read_root() -> dict:
    """Return welcome message for the API root."""
    return {"message": "Welcome to Spectator Data Collector!"}


@app.post("/shutdown", tags=["root"])
async def shutdown() -> None:
    """Shutdown the device gracefully."""
    raise NotImplementedError("The method is not implemented!")
