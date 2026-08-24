from fastapi import APIRouter, Depends

from app.database import engine
from app.repository import SQLModelTaskRepository
from app.schemas import TaskCreate, TaskUpdate
from app.service import TaskService

router = APIRouter()


def get_service() -> TaskService:
    """This is the one seam where storage gets chosen. Change DATABASE_URL
    in .env and this still resolves to the same SQLModelTaskRepository --
    only the engine's connection string differs."""
    repository = SQLModelTaskRepository(engine)
    return TaskService(repository)


@router.get("/", summary="API info")
def root():
    """Describes this API: its name, version, and available endpoints."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@router.get("/health", summary="Health check")
def health():
    """Returns ok if the server is alive. Used for uptime/monitoring checks."""
    return {"status": "ok"}


@router.get("/tasks", summary="List all tasks")
def list_tasks(service: TaskService = Depends(get_service)):
    """Returns every task currently stored."""
    return service.list_tasks()


@router.get("/tasks/{task_id}", summary="Get a single task")
def get_task(task_id: int, service: TaskService = Depends(get_service)):
    """Returns a single task by id, or 404 if it doesn't exist."""
    return service.get_task(task_id)


@router.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate, service: TaskService = Depends(get_service)):
    """Creates a new task from a JSON body with a title. Fails with 400 if title is missing/empty."""
    return service.create_task(task.title)


@router.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, update: TaskUpdate, service: TaskService = Depends(get_service)):
    """Updates a task's title and/or done status. 404 if unknown id, 400 if title is emptied out."""
    return service.update_task(task_id, update.title, update.done)


@router.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int, service: TaskService = Depends(get_service)):
    """Deletes a task by id. Returns 204 with no body on success, 404 if unknown id."""
    service.delete_task(task_id)
