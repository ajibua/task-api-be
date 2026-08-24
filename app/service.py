from typing import Optional

from fastapi import HTTPException

from app.repository import TaskRepository


class TaskService:
    """Business rules live here, not in routes or the repository. This
    class only knows about the TaskRepository interface -- it has no idea
    whether tasks live in SQLite or Postgres, and it never needs to."""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def list_tasks(self):
        return self.repository.list_all()

    def get_task(self, task_id: int):
        task = self.repository.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def create_task(self, title: str):
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="title is required and cannot be empty")
        return self.repository.create(title.strip())

    def update_task(self, task_id: int, title: Optional[str], done: Optional[bool]):
        if title is not None and not title.strip():
            raise HTTPException(status_code=400, detail="title cannot be empty")
        title = title.strip() if title is not None else None
        task = self.repository.update(task_id, title, done)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def delete_task(self, task_id: int):
        deleted = self.repository.delete(task_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")
