from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Task API", version="1.0")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Spec wants {"error": "..."} instead of FastAPI's default {"detail": "..."}
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Read a book", "done": True},
]
next_id = 4


@app.get("/", summary="API info")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get a single task")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
