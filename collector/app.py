"""Spectator Data Collector Application."""

import fastapi

from fastapi.middleware.cors import CORSMiddleware


app = fastapi.FastAPI()

ORIGINS = ["127.0.0.1:3000", "http://localhost:3000", "localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Start services."""
    print("Service starts...")


@app.on_event("shutdown")
def shutdown_event():
    """Shutdown services."""
    print("Service shutdowns...")


@app.get("/", tags=["root"])
async def read_root() -> dict:
    """Return welcome message for the API root."""
    return {"message": "Welcome to Spectator Data Collector!"}
