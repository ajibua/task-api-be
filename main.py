from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, SQLModel, select

from app.database import engine
from app.models import Task
from app.routes import router
from app.auth_routes import router as auth_router
from app.protected_routes import router as protected_router
from app.public_routes import router as public_router

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small to-do list API, backed by Postgres (or SQLite locally), "
        "supporting full CRUD on tasks -- plus Supabase-backed auth: "
        "sign up, log in, log out, and token-protected routes.",
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


def init_db():
    """Creates the tasks table if it doesn't already exist, then seeds
    three example tasks -- but only the first time, when the table is
    empty. Postgres also gets this table created by init.sql on first
    container start; this is a harmless no-op if the table already
    exists (CREATE TABLE IF NOT EXISTS)."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(Task)).first()
        if existing is None:
            session.add_all([
                Task(title="complete BE tasks on flyrank", done=False),
                Task(title="pick up my learning on system design", done=False),
                Task(title="strengthen my DS", done=True),
            ])
            session.commit()


@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(router)
app.include_router(auth_router)
app.include_router(protected_router)
app.include_router(public_router)
