from abc import ABC, abstractmethod
from typing import List, Optional

from sqlmodel import Session, select

from app.models import Task


class TaskRepository(ABC):
    """The storage contract. Anything that can list, get, create, update,
    and delete tasks satisfies this -- regardless of what's behind it."""

    @abstractmethod
    def list_all(self) -> List[Task]:
        ...

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        ...

    @abstractmethod
    def create(self, title: str) -> Task:
        ...

    @abstractmethod
    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[Task]:
        ...

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        ...


class SQLModelTaskRepository(TaskRepository):
    """A single repository implementation, backed by whatever SQLAlchemy
    engine it's given. Point the engine at sqlite:///tasks.db or at
    postgresql://..., and this class doesn't change -- SQLModel's engine
    abstracts the SQL dialect away. That's the concrete proof that
    swapping storage only touches config (DATABASE_URL in .env), not code.
    """

    def __init__(self, engine):
        self.engine = engine

    def list_all(self) -> List[Task]:
        with Session(self.engine) as session:
            return session.exec(select(Task)).all()

    def get(self, task_id: int) -> Optional[Task]:
        with Session(self.engine) as session:
            return session.get(Task, task_id)

    def create(self, title: str) -> Task:
        with Session(self.engine) as session:
            task = Task(title=title, done=False)
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[Task]:
        with Session(self.engine) as session:
            task = session.get(Task, task_id)
            if task is None:
                return None
            if title is not None:
                task.title = title
            if done is not None:
                task.done = done
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    def delete(self, task_id: int) -> bool:
        with Session(self.engine) as session:
            task = session.get(Task, task_id)
            if task is None:
                return False
            session.delete(task)
            session.commit()
            return True
