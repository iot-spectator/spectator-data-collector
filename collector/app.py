"""Spectator Data Collector Application."""

import contextlib
import fastapi

from fastapi.middleware.cors import CORSMiddleware


ORIGINS = ["127.0.0.1:3000", "http://localhost:3000", "localhost:3000"]


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    """Startup and shutdown."""
    print("Service starts...")
    yield
    print("Service shutdowns...")


app = fastapi.FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def read_root() -> dict:
    """Return welcome message for the API root."""
    return {"message": "Welcome to Spectator Data Collector!"}
