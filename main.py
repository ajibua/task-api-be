from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel, Field, Session, create_engine, select

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small to-do list API, backed by SQLite, supporting full CRUD on tasks.",
)


# --- Database setup -------------------------------------------------------

DATABASE_FILE = "tasks.db"
engine = create_engine(f"sqlite:///{DATABASE_FILE}")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    done: bool = False


def init_db():
    """Creates tasks.db and the tasks table if they don't already exist,
    then seeds three example tasks -- but only the first time, when the
    table is empty."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(Task)).first()
        if existing is None:
            session.add_all([
                Task(title="Buy milk", done=False),
                Task(title="Walk the dog", done=False),
                Task(title="Read a book", done=True),
            ])
            session.commit()


@app.on_event("startup")
def on_startup():
    init_db()


# --- Request/response models ----------------------------------------------

class TaskCreate(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Spec wants {"error": "..."} instead of FastAPI's default {"detail": "..."}
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.get("/", summary="API info")
def root():
    """Describes this API: its name, version, and available endpoints."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check")
def health():
    """Returns ok if the server is alive. Used for uptime/monitoring checks."""
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    """Returns every task currently stored in the database."""
    with Session(engine) as session:
        return session.exec(select(Task)).all()


@app.get("/tasks/{task_id}", summary="Get a single task")
def get_task(task_id: int):
    """Returns a single task by id, or 404 if it doesn't exist."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    """Creates a new task from a JSON body with a title. Fails with 400 if title is missing/empty."""
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")

    with Session(engine) as session:
        new_task = Task(title=task.title.strip(), done=False)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return new_task


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, update: TaskUpdate):
    """Updates a task's title and/or done status. 404 if unknown id, 400 if title is emptied out."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if update.title is not None:
            if not update.title.strip():
                raise HTTPException(status_code=400, detail="title cannot be empty")
            task.title = update.title.strip()
        if update.done is not None:
            task.done = update.done
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Deletes a task by id. Returns 204 with no body on success, 404 if unknown id."""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        session.delete(task)
        session.commit()
        return
